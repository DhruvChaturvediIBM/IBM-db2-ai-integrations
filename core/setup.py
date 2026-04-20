"""Setup configuration for IBM DB2 AI Connector"""

from setuptools import setup, find_packages

with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ibm-db2-ai",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Framework-agnostic utility library for integrating IBM DB2 with AI frameworks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ibm-db2-ai-integrations",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ibm-db2-ai-integrations/issues",
        "Documentation": "https://github.com/yourusername/ibm-db2-ai-integrations/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/ibm-db2-ai-integrations",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ibm_db>=3.0.0",
        "ibm_db_dbi>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "vector": [
            "numpy>=1.20.0",
        ],
        "langchain": [
            "langchain>=0.1.0",
            "langchain-community>=0.0.1",
        ],
    },
    keywords=[
        "ibm",
        "db2",
        "database",
        "ai",
        "machine-learning",
        "vector-search",
        "embeddings",
        "langchain",
        "autogen",
        "crewai",
        "haystack",
        "n8n",
    ],
    include_package_data=True,
    zip_safe=False,
)

# Made with Bob
