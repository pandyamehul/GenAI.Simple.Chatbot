"""
Multi-model provider support for the GenAI Chatbot.
Supports OpenAI, Anthropic, Google, and local model providers.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import os

# LangChain imports for different providers
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import BaseMessage

# Import providers with fallback handling
try:
    from langchain.chat_models import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from langchain.chat_models import ChatGooglePalm
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from langchain.chat_models import Ollama
    LOCAL_AVAILABLE = True
except ImportError:
    LOCAL_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from .config import config_manager


class ModelProvider(ABC):
    """Abstract base class for model providers."""
    
    @abstractmethod
    def get_chat_model(self, model_name: str, **kwargs) -> Any:
        """Get chat model instance."""
        pass
    
    @abstractmethod
    def get_embedding_model(self, model_name: str, **kwargs) -> Any:
        """Get embedding model instance."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass


class OpenAIProvider(ModelProvider):
    """OpenAI model provider."""
    
    def get_chat_model(self, model_name: str, **kwargs) -> ChatOpenAI:
        """Get OpenAI chat model."""
        return ChatOpenAI(
            model_name=model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=kwargs.get("temperature", 0.1),
            max_tokens=kwargs.get("max_tokens", 1000)
        )
    
    def get_embedding_model(self, model_name: str, **kwargs) -> OpenAIEmbeddings:
        """Get OpenAI embedding model."""
        return OpenAIEmbeddings(
            model=model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return bool(os.getenv("OPENAI_API_KEY"))


class AnthropicProvider(ModelProvider):
    """Anthropic model provider."""
    
    def get_chat_model(self, model_name: str, **kwargs) -> Any:
        """Get Anthropic chat model."""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not installed")
        
        return ChatAnthropic(
            model=model_name,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=kwargs.get("temperature", 0.1),
            max_tokens=kwargs.get("max_tokens", 1000)
        )
    
    def get_embedding_model(self, model_name: str, **kwargs) -> Any:
        """Anthropic doesn't provide embeddings, fallback to OpenAI or local."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            return SentenceTransformer(config_manager.language_config.MULTILINGUAL_EMBEDDING_MODEL)
        raise NotImplementedError("Anthropic embeddings not available")
    
    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return ANTHROPIC_AVAILABLE and bool(os.getenv("ANTHROPIC_API_KEY"))


class GoogleProvider(ModelProvider):
    """Google model provider."""
    
    def get_chat_model(self, model_name: str, **kwargs) -> Any:
        """Get Google chat model."""
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google AI package not installed")
        
        return ChatGooglePalm(
            model_name=model_name,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=kwargs.get("temperature", 0.1)
        )
    
    def get_embedding_model(self, model_name: str, **kwargs) -> Any:
        """Google embeddings - fallback to multilingual."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            return SentenceTransformer(config_manager.language_config.MULTILINGUAL_EMBEDDING_MODEL)
        raise NotImplementedError("Google embeddings not available")
    
    def is_available(self) -> bool:
        """Check if Google AI is available."""
        return GOOGLE_AVAILABLE and bool(os.getenv("GOOGLE_API_KEY"))


class LocalProvider(ModelProvider):
    """Local model provider (Ollama, etc.)."""
    
    def get_chat_model(self, model_name: str, **kwargs) -> Any:
        """Get local chat model."""
        if not LOCAL_AVAILABLE:
            raise ImportError("Ollama package not installed")
        
        return Ollama(
            model=model_name,
            temperature=kwargs.get("temperature", 0.1)
        )
    
    def get_embedding_model(self, model_name: str, **kwargs) -> Any:
        """Get local embedding model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            return SentenceTransformer(config_manager.language_config.MULTILINGUAL_EMBEDDING_MODEL)
        raise NotImplementedError("Local embeddings require sentence-transformers")
    
    def is_available(self) -> bool:
        """Check if local models are available."""
        return LOCAL_AVAILABLE


class MultiModelManager:
    """Manager for multiple model providers."""
    
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "google": GoogleProvider(),
            "local": LocalProvider()
        }
        self.config = config_manager
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [name for name, provider in self.providers.items() if provider.is_available()]
    
    def get_chat_model(self, provider: str, model_name: str, **kwargs) -> Any:
        """Get chat model from specified provider."""
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not self.providers[provider].is_available():
            raise RuntimeError(f"Provider {provider} is not available")
        
        return self.providers[provider].get_chat_model(model_name, **kwargs)
    
    def get_embedding_model(self, provider: str, model_name: str, **kwargs) -> Any:
        """Get embedding model from specified provider."""
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not self.providers[provider].is_available():
            raise RuntimeError(f"Provider {provider} is not available")
        
        return self.providers[provider].get_embedding_model(model_name, **kwargs)
    
    def validate_provider_setup(self, provider: str) -> Dict[str, Any]:
        """Validate provider setup and return status."""
        status = {
            "available": False,
            "chat_models": [],
            "embedding_models": [],
            "error": None
        }
        
        try:
            if provider in self.providers:
                provider_instance = self.providers[provider]
                status["available"] = provider_instance.is_available()
                
                if status["available"]:
                    # Get available models for this provider
                    status["chat_models"] = list(self.config.get_available_models(provider).keys())
                    status["embedding_models"] = list(self.config.get_available_embedding_models(provider).keys())
                else:
                    status["error"] = f"Provider {provider} credentials not configured"
            else:
                status["error"] = f"Unknown provider: {provider}"
                
        except Exception as e:
            status["error"] = str(e)
        
        return status


# Global multi-model manager instance
multi_model_manager = MultiModelManager()