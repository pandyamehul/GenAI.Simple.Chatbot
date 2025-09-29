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
    
    # Model Provider settings
    DEFAULT_PROVIDER: str = "openai"  # openai, anthropic, google, local
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Multi-language settings
    DEFAULT_LANGUAGE: str = "en"  # English
    SUPPORTED_LANGUAGES: Dict[str, str] = None
    AUTO_DETECT_LANGUAGE: bool = True
    
    # UI settings
    SIDEBAR_WIDTH: int = 300
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.ALLOWED_FILE_TYPES is None:
            self.ALLOWED_FILE_TYPES = ["pdf", "docx", "xlsx", "pptx", "txt"]
            
        if self.SUPPORTED_LANGUAGES is None:
            self.SUPPORTED_LANGUAGES = {
                "en": "English",
                "es": "Español", 
                "fr": "Français",
                "de": "Deutsch",
                "it": "Italiano",
                "pt": "Português",
                "ru": "Русский",
                "zh": "中文",
                "ja": "日本語",
                "ko": "한국어",
                "ar": "العربية",
                "hi": "हिन्दी"
            }


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
class ModelProviderConfig:
    """Multi-model provider configurations."""
    
    # OpenAI
    OPENAI_MODELS: Dict[str, str] = None
    OPENAI_EMBEDDING_MODELS: Dict[str, str] = None
    
    # Anthropic
    ANTHROPIC_MODELS: Dict[str, str] = None
    
    # Google
    GOOGLE_MODELS: Dict[str, str] = None
    
    # Local models (Ollama, etc.)
    LOCAL_MODELS: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize model configurations."""
        if self.OPENAI_MODELS is None:
            self.OPENAI_MODELS = {
                "gpt-3.5-turbo": "GPT-3.5 Turbo (Fast)",
                "gpt-4": "GPT-4 (Advanced)",
                "gpt-4-turbo": "GPT-4 Turbo (Latest)"
            }
            
        if self.OPENAI_EMBEDDING_MODELS is None:
            self.OPENAI_EMBEDDING_MODELS = {
                "text-embedding-ada-002": "Ada-002 (Standard)",
                "text-embedding-3-small": "Embedding v3 Small", 
                "text-embedding-3-large": "Embedding v3 Large"
            }
            
        if self.ANTHROPIC_MODELS is None:
            self.ANTHROPIC_MODELS = {
                "claude-3-haiku": "Claude 3 Haiku (Fast)",
                "claude-3-sonnet": "Claude 3 Sonnet (Balanced)",
                "claude-3-opus": "Claude 3 Opus (Advanced)"
            }
            
        if self.GOOGLE_MODELS is None:
            self.GOOGLE_MODELS = {
                "gemini-pro": "Gemini Pro",
                "gemini-pro-vision": "Gemini Pro Vision"
            }
            
        if self.LOCAL_MODELS is None:
            self.LOCAL_MODELS = {
                "llama2": "Llama 2",
                "mistral": "Mistral 7B",
                "codellama": "Code Llama"
            }


@dataclass
class LanguageConfig:
    """Language-specific configurations."""
    
    # Language detection
    DETECTION_CONFIDENCE_THRESHOLD: float = 0.8
    
    # Language-specific embeddings
    MULTILINGUAL_EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    # Translation settings
    ENABLE_TRANSLATION: bool = True
    TARGET_LANGUAGE_FOR_PROCESSING: str = "en"  # Process all in English internally


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
        self.model_config = ModelProviderConfig()
        self.language_config = LanguageConfig()
    
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
    
    def get_available_models(self, provider: str) -> Dict[str, str]:
        """Get available models for a specific provider."""
        provider = provider.lower()
        if provider == "openai":
            return self.model_config.OPENAI_MODELS
        elif provider == "anthropic":
            return self.model_config.ANTHROPIC_MODELS
        elif provider == "google":
            return self.model_config.GOOGLE_MODELS
        elif provider == "local":
            return self.model_config.LOCAL_MODELS
        return {}
    
    def get_available_embedding_models(self, provider: str = "openai") -> Dict[str, str]:
        """Get available embedding models for a provider."""
        if provider.lower() == "openai":
            return self.model_config.OPENAI_EMBEDDING_MODELS
        return {"multilingual": "Multilingual (Local)"}
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages."""
        return self.app_config.SUPPORTED_LANGUAGES
    
    def get_current_language(self) -> str:
        """Get current language setting."""
        return os.getenv("APP_LANGUAGE", self.app_config.DEFAULT_LANGUAGE)
    
    def validate_provider_credentials(self, provider: str) -> tuple[bool, str]:
        """Validate credentials for a specific provider."""
        provider = provider.lower()
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return False, "OpenAI API key not found"
                
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return False, "Anthropic API key not found"
                
        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return False, "Google API key not found"
                
        elif provider == "local":
            # Local models don't need API keys
            pass
            
        return True, ""


# Global configuration instance
config_manager = ConfigManager()