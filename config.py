"""
Configuration settings for the GenAI Chatbot application.
"""
import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # App metadata
    APP_TITLE: str = "📚 Gen AI Chatbot with PDF Knowledge Base"
    APP_VERSION: str = "2.0.0"
    
    # Authentication
    DEFAULT_USERNAME: str = "admin"
    DEFAULT_PASSWORD: str = "password123"
    
    # File settings
    ALLOWED_FILE_TYPES: list = None
    MAX_FILE_SIZE_MB: int = 100
    
    # Text processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Vector database settings
    VECTOR_DB_DIR: str = "vector_db"
    FAISS_INDEX_NAME: str = "faiss_index"
    CHROMA_COLLECTION_NAME: str = "pdf_documents"
    
    # OpenAI settings
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # UI settings
    SIDEBAR_WIDTH: int = 300
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.ALLOWED_FILE_TYPES is None:
            self.ALLOWED_FILE_TYPES = ["pdf"]


@dataclass
class VectorStoreConfig:
    """Vector store specific configurations."""
    
    # FAISS settings
    FAISS_SIMILARITY_THRESHOLD: float = 0.7
    FAISS_K_DOCUMENTS: int = 5
    
    # ChromaDB settings
    CHROMA_DISTANCE_FUNCTION: str = "cosine"
    CHROMA_K_DOCUMENTS: int = 5
    CHROMA_PERSIST_DIR: str = "chroma_db"


@dataclass
class ChatConfig:
    """Chat engine configurations."""
    
    # Memory settings
    MEMORY_KEY: str = "chat_history"
    RETURN_MESSAGES: bool = True
    
    # Response settings
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.1
    
    # System prompt
    SYSTEM_PROMPT: str = """
        You are Gen AI, a helpful assistant that answers questions based on the uploaded PDF documents.

        Use the following pieces of context to answer the question at the end.
        If the answer is not in the documents, respond with "I don't know".
        Be concise and to the point.

        Context: {context}
        Question: {question}

        Answer:"""


class ConfigManager:
    """Manages application configuration and environment variables."""
    
    def __init__(self):
        self.app_config = AppConfig()
        self.vector_config = VectorStoreConfig()
        self.chat_config = ChatConfig()
    
    def get_openai_api_key(self) -> str:
        """Get OpenAI API key from environment."""
        return os.getenv("OPENAI_API_KEY", "")
    
    def get_openai_model(self) -> str:
        """Get OpenAI model from environment or default."""
        return os.getenv("OPENAI_MODEL", self.app_config.DEFAULT_MODEL)
    
    def get_embedding_model(self) -> str:
        """Get embedding model from environment or default."""
        return os.getenv("OPENAI_EMBEDDING_MODEL", self.app_config.DEFAULT_EMBEDDING_MODEL)
    
    def validate_environment(self) -> tuple[bool, str]:
        """Validate required environment variables."""
        api_key = self.get_openai_api_key()
        if not api_key:
            return False, "OpenAI API key not found. Please set OPENAI_API_KEY in your .env file"
        return True, ""
    
    def get_vector_db_paths(self) -> Dict[str, str]:
        """Get vector database paths."""
        return {
            "faiss_dir": self.app_config.VECTOR_DB_DIR,
            "faiss_path": os.path.join(self.app_config.VECTOR_DB_DIR, self.app_config.FAISS_INDEX_NAME),
            "chroma_dir": self.vector_config.CHROMA_PERSIST_DIR
        }


# Global configuration instance
config_manager = ConfigManager()