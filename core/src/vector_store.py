"""IBM DB2 Vector Store - Framework Agnostic

Provides vector store operations for IBM DB2 databases with vector support.
This is a wrapper around the langchain-db2 implementation that can be used
across different AI frameworks.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DB2VectorStore:
    """Vector store operations for IBM DB2.
    
    This class provides a framework-agnostic interface to DB2's vector
    capabilities. It wraps the langchain-db2 DB2VS implementation.
    
    Example:
        >>> from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2VectorStore
        >>> config = DB2Config(database="mydb", hostname="localhost",
        ...                    username="user", password="pass")
        >>> with DB2ConnectionManager(config) as conn:
        ...     vector_store = DB2VectorStore(
        ...         connection=conn,
        ...         table_name="embeddings",
        ...         embedding_function=my_embedding_fn
        ...     )
        ...     vector_store.add_texts(["Hello world", "AI is amazing"])
        ...     results = vector_store.search("artificial intelligence", k=5)
    """
    
    def __init__(
        self,
        connection,
        table_name: str,
        embedding_function,
        distance_strategy: str = "EUCLIDEAN",
        embedding_dim: Optional[int] = None
    ):
        """Initialize vector store.
        
        Args:
            connection: Active ibm_db_dbi connection
            table_name: Name of the table to store vectors
            embedding_function: Function or model to generate embeddings
            distance_strategy: Distance metric (EUCLIDEAN, COSINE, DOT_PRODUCT)
            embedding_dim: Dimension of embeddings (auto-detected if None)
        """
        self.connection = connection
        self.table_name = table_name
        self.embedding_function = embedding_function
        self.distance_strategy = distance_strategy
        self._embedding_dim = embedding_dim
        
        logger.info(
            f"Initialized DB2VectorStore: table={table_name}, "
            f"distance={distance_strategy}"
        )
    
    def _get_embedding_dim(self) -> int:
        """Get or detect embedding dimension.
        
        Returns:
            Embedding dimension
        """
        if self._embedding_dim:
            return self._embedding_dim
        
        # Detect dimension by embedding a sample text
        sample_embedding = self._embed_text("sample")
        self._embedding_dim = len(sample_embedding)
        return self._embedding_dim
    
    def _embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if callable(self.embedding_function):
            return self.embedding_function(text)
        elif hasattr(self.embedding_function, 'embed_query'):
            return self.embedding_function.embed_query(text)
        else:
            raise TypeError("embedding_function must be callable or have embed_query method")
    
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if hasattr(self.embedding_function, 'embed_documents'):
            return self.embedding_function.embed_documents(texts)
        else:
            return [self._embed_text(text) for text in texts]
    
    def create_table(self) -> None:
        """Create vector table if it doesn't exist.
        
        Raises:
            RuntimeError: If table creation fails
        """
        try:
            embedding_dim = self._get_embedding_dim()
            
            cursor = self.connection.cursor()
            ddl = f"""
                CREATE TABLE {self.table_name} (
                    id CHAR(16) PRIMARY KEY NOT NULL,
                    text CLOB,
                    metadata BLOB,
                    embedding VECTOR({embedding_dim}, FLOAT32)
                )
            """
            cursor.execute(ddl)
            cursor.execute("COMMIT")
            cursor.close()
            
            logger.info(f"Created table {self.table_name} with dimension {embedding_dim}")
            
        except Exception as e:
            if "SQL0601N" in str(e):  # Table already exists
                logger.info(f"Table {self.table_name} already exists")
            else:
                error_msg = f"Error creating table: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg) from e
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add texts to the vector store.
        
        Args:
            texts: List of texts to add
            metadatas: Optional metadata for each text
            ids: Optional IDs for each text
            
        Returns:
            List of IDs for added texts
            
        Raises:
            RuntimeError: If insertion fails
        """
        try:
            # Use langchain-db2 implementation if available
            try:
                from langchain_db2 import DB2VS
                from langchain_community.vectorstores.utils import DistanceStrategy
                
                # Map distance strategy
                strategy_map = {
                    "EUCLIDEAN": DistanceStrategy.EUCLIDEAN_DISTANCE,
                    "COSINE": DistanceStrategy.COSINE,
                    "DOT_PRODUCT": DistanceStrategy.DOT_PRODUCT,
                }
                
                db2vs = DB2VS(
                    client=self.connection,
                    embedding_function=self.embedding_function,
                    table_name=self.table_name,
                    distance_strategy=strategy_map.get(
                        self.distance_strategy,
                        DistanceStrategy.EUCLIDEAN_DISTANCE
                    )
                )
                
                return db2vs.add_texts(texts, metadatas=metadatas, ids=ids)
                
            except ImportError:
                logger.warning("langchain-db2 not available, using basic implementation")
                # Basic implementation without langchain-db2
                return self._add_texts_basic(texts, metadatas, ids)
                
        except Exception as e:
            error_msg = f"Error adding texts: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _add_texts_basic(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]],
        ids: Optional[List[str]]
    ) -> List[str]:
        """Basic implementation of add_texts without langchain-db2."""
        import hashlib
        import json
        import uuid
        
        # Generate IDs if not provided
        if not ids:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Hash IDs
        hashed_ids = [
            hashlib.sha256(id_.encode()).hexdigest()[:16].upper()
            for id_ in ids
        ]
        
        # Generate embeddings
        embeddings = self._embed_texts(texts)
        
        # Prepare metadata
        if not metadatas:
            metadatas = [{} for _ in texts]
        
        # Insert data
        embedding_dim = len(embeddings[0])
        cursor = self.connection.cursor()
        
        sql = f"""
            INSERT INTO {self.table_name} (id, text, metadata, embedding)
            VALUES (?, ?, SYSTOOLS.JSON2BSON(?), VECTOR(?, {embedding_dim}, FLOAT32))
        """
        
        data = [
            (hashed_id, text, json.dumps(metadata), str(embedding))
            for hashed_id, text, metadata, embedding
            in zip(hashed_ids, texts, metadatas, embeddings)
        ]
        
        cursor.executemany(sql, data)
        cursor.execute("COMMIT")
        cursor.close()
        
        return hashed_ids
    
    def search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar texts.
        
        Args:
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of tuples (text, score, metadata)
        """
        try:
            # Use langchain-db2 if available
            try:
                from langchain_db2 import DB2VS
                from langchain_community.vectorstores.utils import DistanceStrategy
                
                strategy_map = {
                    "EUCLIDEAN": DistanceStrategy.EUCLIDEAN_DISTANCE,
                    "COSINE": DistanceStrategy.COSINE,
                    "DOT_PRODUCT": DistanceStrategy.DOT_PRODUCT,
                }
                
                db2vs = DB2VS(
                    client=self.connection,
                    embedding_function=self.embedding_function,
                    table_name=self.table_name,
                    distance_strategy=strategy_map.get(
                        self.distance_strategy,
                        DistanceStrategy.EUCLIDEAN_DISTANCE
                    )
                )
                
                docs_and_scores = db2vs.similarity_search_with_score(
                    query, k=k, filter=filter
                )
                
                return [
                    (doc.page_content, score, doc.metadata)
                    for doc, score in docs_and_scores
                ]
                
            except ImportError:
                logger.warning("langchain-db2 not available, using basic search")
                return self._search_basic(query, k, filter)
                
        except Exception as e:
            error_msg = f"Error searching: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _search_basic(
        self,
        query: str,
        k: int,
        filter: Optional[Dict[str, Any]]
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Basic search implementation without langchain-db2."""
        import json
        
        # Generate query embedding
        query_embedding = self._embed_text(query)
        embedding_dim = len(query_embedding)
        
        # Distance function mapping
        distance_func = {
            "EUCLIDEAN": "EUCLIDEAN",
            "COSINE": "COSINE",
            "DOT_PRODUCT": "DOT"
        }.get(self.distance_strategy, "EUCLIDEAN")
        
        # Execute search
        sql = f"""
            SELECT 
                text,
                SYSTOOLS.BSON2JSON(metadata) as metadata,
                vector_distance(
                    embedding,
                    VECTOR('{query_embedding}', {embedding_dim}, FLOAT32),
                    {distance_func}
                ) as distance
            FROM {self.table_name}
            ORDER BY distance
            FETCH FIRST {k} ROWS ONLY
        """
        
        cursor = self.connection.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        
        return [
            (
                row[0],
                row[2],
                json.loads(row[1]) if row[1] else {}
            )
            for row in results
        ]
    
    def delete(self, ids: List[str]) -> None:
        """Delete vectors by IDs.
        
        Args:
            ids: List of IDs to delete
        """
        import hashlib
        
        hashed_ids = [
            hashlib.sha256(id_.encode()).hexdigest()[:16].upper()
            for id_ in ids
        ]
        
        placeholders = ", ".join(["?" for _ in hashed_ids])
        sql = f"DELETE FROM {self.table_name} WHERE id IN ({placeholders})"
        
        cursor = self.connection.cursor()
        cursor.execute(sql, hashed_ids)
        cursor.execute("COMMIT")
        cursor.close()
        
        logger.info(f"Deleted {len(ids)} vectors")
    
    def drop_table(self) -> None:
        """Drop the vector table.
        
        Warning: This will delete all data in the table.
        """
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE {self.table_name}")
        cursor.execute("COMMIT")
        cursor.close()
        
        logger.info(f"Dropped table {self.table_name}")

# Made with Bob
