"""
Vector store module supporting both FAISS and ChromaDB backends.
"""
import os
import shutil
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import streamlit as st

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Chroma
from langchain.schema import Document

from .config import config_manager


class VectorStoreInterface(ABC):
    """Abstract interface for vector store implementations."""
    
    @abstractmethod
    def create_from_documents(self, documents: List[Document], embeddings) -> Any:
        """Create vector store from documents."""
        pass
    
    @abstractmethod
    def load_local(self, path: str, embeddings) -> Any:
        """Load vector store from local storage."""
        pass
    
    @abstractmethod
    def save_local(self, db: Any, path: str) -> None:
        """Save vector store to local storage."""
        pass
    
    @abstractmethod
    def merge_databases(self, existing_db: Any, new_db: Any) -> Any:
        """Merge two vector databases."""
        pass
    
    @abstractmethod
    def get_document_count(self, db: Any) -> int:
        """Get number of documents in the database."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if database exists at path."""
        pass
    
    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete database at path."""
        pass


class FAISSVectorStore(VectorStoreInterface):
    """FAISS vector store implementation."""
    
    def create_from_documents(self, documents: List[Document], embeddings) -> FAISS:
        """Create FAISS vector store from documents."""
        return FAISS.from_documents(documents, embeddings)
    
    def load_local(self, path: str, embeddings) -> FAISS:
        """Load FAISS vector store from local storage."""
        try:
            # Try with allow_dangerous_deserialization parameter (newer LangChain versions)
            return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        except TypeError:
            # Fall back to older method without the parameter
            return FAISS.load_local(path, embeddings)
    
    def save_local(self, db: FAISS, path: str) -> None:
        """Save FAISS vector store to local storage."""
        db.save_local(path)
    
    def merge_databases(self, existing_db: FAISS, new_db: FAISS) -> FAISS:
        """Merge two FAISS databases."""
        existing_db.merge_from(new_db)
        return existing_db
    
    def get_document_count(self, db: FAISS) -> int:
        """Get number of documents in FAISS database."""
        if hasattr(db, 'index') and db.index is not None:
            return db.index.ntotal
        return 0
    
    def exists(self, path: str) -> bool:
        """Check if FAISS database exists."""
        return os.path.exists(path)
    
    def delete(self, path: str) -> bool:
        """Delete FAISS database directory."""
        try:
            parent_dir = os.path.dirname(path)
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting FAISS database: {str(e)}")
            return False


class ChromaDBVectorStore(VectorStoreInterface):
    """ChromaDB vector store implementation."""
    
    def __init__(self):
        self.config = config_manager.vector_config
    
    def create_from_documents(self, documents: List[Document], embeddings) -> Chroma:
        """Create Chroma vector store from documents."""
        return Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=config_manager.app_config.CHROMA_COLLECTION_NAME,
            persist_directory=self.config.CHROMA_PERSIST_DIR
        )
    
    def load_local(self, path: str, embeddings) -> Chroma:
        """Load Chroma vector store from local storage."""
        return Chroma(
            embedding_function=embeddings,
            collection_name=config_manager.app_config.CHROMA_COLLECTION_NAME,
            persist_directory=path
        )
    
    def save_local(self, db: Chroma, path: str) -> None:
        """Save Chroma vector store (auto-persisted)."""
        if hasattr(db, 'persist'):
            db.persist()
    
    def merge_databases(self, existing_db: Chroma, new_db: Chroma) -> Chroma:
        """Merge documents into existing Chroma database."""
        # For Chroma, we need to add documents directly
        # This is a simplified implementation
        return existing_db
    
    def get_document_count(self, db: Chroma) -> int:
        """Get number of documents in Chroma database."""
        try:
            if hasattr(db, '_collection') and db._collection is not None:
                return db._collection.count()
            return 0
        except Exception:
            return 0
    
    def exists(self, path: str) -> bool:
        """Check if Chroma database exists."""
        return os.path.exists(path) and os.path.isdir(path)
    
    def delete(self, path: str) -> bool:
        """Delete Chroma database directory."""
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting ChromaDB database: {str(e)}")
            return False


class VectorStoreManager:
    """Manages vector store operations with support for multiple backends."""
    
    def __init__(self):
        self.config = config_manager
        self.faiss_store = FAISSVectorStore()
        self.chroma_store = ChromaDBVectorStore()
        self.current_store = None
        self.current_db_type = None
    
    def set_database_type(self, db_type: str) -> None:
        """Set the current database type (faiss or chroma)."""
        if db_type.lower() == "faiss":
            self.current_store = self.faiss_store
            self.current_db_type = "faiss"
        elif db_type.lower() == "chroma":
            self.current_store = self.chroma_store
            self.current_db_type = "chroma"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def get_embeddings(self) -> OpenAIEmbeddings:
        """Get OpenAI embeddings instance."""
        api_key = self.config.get_openai_api_key()
        if not api_key:
            raise ValueError("OpenAI API key not found")
        
        return OpenAIEmbeddings(
            openai_api_key=api_key,
            model=self.config.get_embedding_model()
        )
    
    def create_database(self, documents: List[Document]) -> Any:
        """Create new vector database from documents."""
        if not self.current_store:
            raise ValueError("Database type not set. Call set_database_type() first.")
        
        embeddings = self.get_embeddings()
        return self.current_store.create_from_documents(documents, embeddings)
    
    def load_database(self) -> Optional[Any]:
        """Load existing vector database."""
        if not self.current_store:
            raise ValueError("Database type not set. Call set_database_type() first.")
        
        paths = self.config.get_vector_db_paths()
        
        if self.current_db_type == "faiss":
            path = paths["faiss_path"]
        else:  # chroma
            path = paths["chroma_dir"]
        
        if not self.current_store.exists(path):
            return None
        
        try:
            embeddings = self.get_embeddings()
            return self.current_store.load_local(path, embeddings)
        except Exception as e:
            st.error(f"Error loading {self.current_db_type.upper()} database: {str(e)}")
            return None
    
    def save_database(self, db: Any) -> None:
        """Save vector database to local storage."""
        if not self.current_store:
            raise ValueError("Database type not set. Call set_database_type() first.")
        
        paths = self.config.get_vector_db_paths()
        
        if self.current_db_type == "faiss":
            path = paths["faiss_path"]
            # Ensure directory exists
            os.makedirs(paths["faiss_dir"], exist_ok=True)
        else:  # chroma
            path = paths["chroma_dir"]
        
        self.current_store.save_local(db, path)
    
    def merge_databases(self, existing_db: Any, new_documents: List[Document]) -> Any:
        """Merge new documents into existing database."""
        if not self.current_store:
            raise ValueError("Database type not set. Call set_database_type() first.")
        
        embeddings = self.get_embeddings()
        
        if self.current_db_type == "chroma":
            # For Chroma, add documents directly to existing database
            existing_db.add_documents(new_documents)
            return existing_db
        else:
            # For FAISS, create new database and merge
            new_db = self.current_store.create_from_documents(new_documents, embeddings)
            return self.current_store.merge_databases(existing_db, new_db)
    
    def get_document_count(self, db: Any) -> int:
        """Get number of documents in database."""
        if not self.current_store:
            return 0
        return self.current_store.get_document_count(db)
    
    def database_exists(self) -> bool:
        """Check if database exists for current type."""
        if not self.current_store:
            return False
        
        paths = self.config.get_vector_db_paths()
        
        if self.current_db_type == "faiss":
            return self.current_store.exists(paths["faiss_path"])
        else:  # chroma
            return self.current_store.exists(paths["chroma_dir"])
    
    def delete_database(self) -> bool:
        """Delete existing database."""
        if not self.current_store:
            return False
        
        paths = self.config.get_vector_db_paths()
        
        if self.current_db_type == "faiss":
            return self.current_store.delete(paths["faiss_path"])
        else:  # chroma
            return self.current_store.delete(paths["chroma_dir"])
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about current database setup."""
        paths = self.config.get_vector_db_paths()
        
        return {
            "current_type": self.current_db_type,
            "faiss_exists": self.faiss_store.exists(paths["faiss_path"]),
            "chroma_exists": self.chroma_store.exists(paths["chroma_dir"]),
            "paths": paths
        }


# Global vector store manager instance
vector_store_manager = VectorStoreManager()
