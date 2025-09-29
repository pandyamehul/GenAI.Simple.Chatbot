"""
Chat engine module for handling conversational AI interactions.
"""
from typing import Any, Optional
import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from .config import config_manager


class ChatEngine:
    """Handles conversational AI interactions with document retrieval."""
    
    def __init__(self):
        self.config = config_manager
        self.chain: Optional[ConversationalRetrievalChain] = None
        self.memory: Optional[ConversationBufferMemory] = None
    
    def initialize_chain(self, vector_db: Any) -> None:
        """
        Initialize the conversational retrieval chain.
        
        Args:
            vector_db: Vector database instance (FAISS or Chroma)
        """
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key=self.config.chat_config.MEMORY_KEY,
            return_messages=self.config.chat_config.RETURN_MESSAGES
        )
        
        # Create custom prompt template
        custom_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.config.chat_config.SYSTEM_PROMPT
        )
        
        # Initialize ChatOpenAI
        llm = ChatOpenAI(
            openai_api_key=self.config.get_openai_api_key(),
            model_name=self.config.get_openai_model(),
            temperature=self.config.chat_config.TEMPERATURE,
            max_tokens=self.config.chat_config.MAX_TOKENS
        )
        
        # Create conversational retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vector_db.as_retriever(),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": custom_prompt},
            verbose=False  # Set to True for debugging
        )
    
    def get_response(self, question: str) -> str:
        """
        Get AI response for a question.
        
        Args:
            question (str): User's question
            
        Returns:
            str: AI generated response
            
        Raises:
            ValueError: If chain is not initialized
        """
        if not self.chain:
            raise ValueError("Chat engine not initialized. Call initialize_chain() first.")
        
        try:
            response = self.chain.run(question)
            return response.strip()
        
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while processing your question. Please try again."
    
    def get_chat_history(self) -> list:
        """
        Get current chat history.
        
        Returns:
            list: Chat history messages
        """
        if not self.memory:
            return []
        
        try:
            return self.memory.chat_memory.messages
        except Exception:
            return []
    
    def clear_memory(self) -> None:
        """Clear chat memory."""
        if self.memory:
            self.memory.clear()
    
    def get_memory_stats(self) -> dict:
        """
        Get memory statistics.
        
        Returns:
            dict: Memory statistics
        """
        history = self.get_chat_history()
        
        return {
            "total_messages": len(history),
            "user_messages": len([msg for msg in history if hasattr(msg, 'type') and msg.type == 'human']),
            "ai_messages": len([msg for msg in history if hasattr(msg, 'type') and msg.type == 'ai']),
            "memory_initialized": self.memory is not None,
            "chain_initialized": self.chain is not None
        }
    
    def is_ready(self) -> bool:
        """
        Check if chat engine is ready to handle questions.
        
        Returns:
            bool: True if engine is ready
        """
        return self.chain is not None and self.memory is not None


class ConversationManager:
    """Manages conversation state and history in Streamlit session."""
    
    @staticmethod
    def initialize_session_state() -> None:
        """Initialize conversation state in Streamlit session."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "chat_engine" not in st.session_state:
            st.session_state.chat_engine = ChatEngine()
    
    @staticmethod
    def add_message(role: str, content: str) -> None:
        """
        Add message to session state.
        
        Args:
            role (str): Message role ('user' or 'assistant')
            content (str): Message content
        """
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        st.session_state.messages.append({
            "role": role,
            "content": content
        })
    
    @staticmethod
    def get_messages() -> list:
        """
        Get all messages from session state.
        
        Returns:
            list: List of message dictionaries
        """
        return st.session_state.get("messages", [])
    
    @staticmethod
    def clear_conversation() -> None:
        """Clear conversation history."""
        if "messages" in st.session_state:
            st.session_state.messages = []
        
        if "chat_engine" in st.session_state:
            st.session_state.chat_engine.clear_memory()
    
    @staticmethod
    def get_conversation_stats() -> dict:
        """
        Get conversation statistics.
        
        Returns:
            dict: Conversation statistics
        """
        messages = ConversationManager.get_messages()
        
        return {
            "total_messages": len(messages),
            "user_messages": len([msg for msg in messages if msg.get("role") == "user"]),
            "assistant_messages": len([msg for msg in messages if msg.get("role") == "assistant"]),
            "has_conversation": len(messages) > 0
        }
    
    @staticmethod
    def display_chat_history() -> None:
        """Display chat history in Streamlit interface."""
        messages = ConversationManager.get_messages()
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            with st.chat_message(role):
                st.write(content)
    
    @staticmethod
    def export_conversation() -> str:
        """
        Export conversation as text.
        
        Returns:
            str: Formatted conversation text
        """
        messages = ConversationManager.get_messages()
        
        if not messages:
            return "No conversation to export."
        
        exported_text = "# Conversation Export\n\n"
        
        for i, message in enumerate(messages, 1):
            role = message.get("role", "user").title()
            content = message.get("content", "")
            exported_text += f"## {i}. {role}\n{content}\n\n"
        
        return exported_text

# Global instances
chat_engine = ChatEngine()
conversation_manager = ConversationManager()