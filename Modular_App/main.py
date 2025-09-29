"""
GenAI PDF Chatbot - Main Application

A modular, production-ready chatbot application that allows users to upload PDF documents
and interact with them using natural language queries. Supports both FAISS and ChromaDB
vector databases with persistent storage capabilities.

Version: 2.0.0
Author: GenAI Team
"""

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from .config import config_manager
from .auth import auth_manager
from .document_processor import document_processor
from .vector_store import vector_store_manager
from .chat_engine import chat_engine, conversation_manager
from .ui_components import ui_components


class GenAIChatbotApp:
    """Main application class for the GenAI PDF Chatbot."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = config_manager
        
        # Initialize Streamlit session state
        if "app_initialized" not in st.session_state:
            self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Initialize Streamlit session state variables."""
        st.session_state.app_initialized = True
        st.session_state.current_db_type = None
        st.session_state.vector_db = None
        conversation_manager.initialize_session_state()
    
    def run(self) -> None:
        """Run the main application."""
        try:
            # Setup UI
            ui_components.show_app_header()
            
            # Authentication
            if not auth_manager.require_authentication():
                return
            
            # Main application flow
            self._run_main_workflow()
            
        except Exception as e:
            ui_components.show_error_message(
                "An unexpected error occurred",
                str(e)
            )
            st.stop()
    
    def _run_main_workflow(self) -> None:
        """Run the main application workflow."""
        # Validate environment
        is_valid, error_msg = self.config.validate_environment()
        if not is_valid:
            ui_components.show_error_message(error_msg)
            st.stop()
        
        # Database type selection
        selected_db_type = ui_components.show_database_selector()
        
        # Set database type if changed
        if st.session_state.current_db_type != selected_db_type:
            vector_store_manager.set_database_type(selected_db_type)
            st.session_state.current_db_type = selected_db_type
        
        # Show database management controls
        ui_components.show_database_management()
        
        # Check for existing database
        has_existing_db = vector_store_manager.database_exists()
        
        # Action selection
        action = ui_components.show_action_selector(has_existing_db)
        
        # File upload (if needed)
        uploaded_files = ui_components.show_file_uploader(action)
        
        # Storage options
        storage_option = ui_components.show_storage_options(action, has_existing_db)
        
        # Process documents and setup chat
        vector_db = self._process_workflow(action, uploaded_files, storage_option, has_existing_db)
        
        if vector_db:
            # Chat interface
            ui_components.show_chat_interface(vector_db)
            
            # Help section
            ui_components.show_help_section()
    
    def _process_workflow(self, action: str, uploaded_files, storage_option: str, has_existing_db: bool):
        """
        Process the main workflow based on user selections.
        
        Args:
            action (str): Selected action
            uploaded_files: Uploaded files (if any)
            storage_option (str): Storage option
            has_existing_db (bool): Whether existing database exists
            
        Returns:
            Vector database instance or None
        """
        # Handle different actions
        if action == "💬 Chat with existing knowledge base":
            return self._load_existing_database()
        
        elif uploaded_files:
            return self._process_documents(action, uploaded_files, storage_option, has_existing_db)
        
        else:
            st.info("👆 Please upload PDF files to continue.")
            return None
    
    def _load_existing_database(self):
        """Load existing vector database."""
        try:
            with st.spinner("Loading existing knowledge base..."):
                db = vector_store_manager.load_database()
                
                if db:
                    ui_components.show_success_message("Knowledge base loaded successfully!")
                    return db
                else:
                    ui_components.show_error_message("Failed to load existing database")
                    return None
                    
        except Exception as e:
            ui_components.show_error_message("Error loading database", str(e))
            return None
    
    def _process_documents(self, action: str, uploaded_files, storage_option: str, has_existing_db: bool):
        """
        Process uploaded documents and create/update vector database.
        
        Args:
            action (str): Selected action
            uploaded_files: Uploaded files
            storage_option (str): Storage option
            has_existing_db (bool): Whether existing database exists
            
        Returns:
            Vector database instance or None
        """
        try:
            # Process documents
            with st.spinner("Processing PDF documents..."):
                documents = document_processor.load_documents(uploaded_files)
                
                if not documents:
                    ui_components.show_error_message("No documents could be processed")
                    return None
                
                # Split documents
                docs = document_processor.split_documents(documents)
                
                if not docs:
                    ui_components.show_error_message("Document splitting failed")
                    return None
            
            # Show processing status
            ui_components.show_processing_status(docs, action)
            
            # Handle vector database creation/updating
            return self._handle_vector_database(action, docs, storage_option, has_existing_db)
            
        except Exception as e:
            ui_components.show_error_message("Error processing documents", str(e))
            return None
    
    def _handle_vector_database(self, action: str, docs, storage_option: str, has_existing_db: bool):
        """
        Handle vector database creation or updating.
        
        Args:
            action (str): Selected action
            docs: Processed document chunks
            storage_option (str): Storage option
            has_existing_db (bool): Whether existing database exists
            
        Returns:
            Vector database instance or None
        """
        try:
            if storage_option == "Memory only (temporary)":
                return self._create_memory_database(docs)
            
            else:  # Persistent storage
                return self._handle_persistent_database(action, docs, has_existing_db)
                
        except Exception as e:
            ui_components.show_error_message("Error creating vector database", str(e))
            return None
    
    def _create_memory_database(self, docs):
        """Create temporary in-memory vector database."""
        with st.spinner("Creating vector database in memory..."):
            db = vector_store_manager.create_database(docs)
            ui_components.show_success_message(
                "Vector database created in memory",
                "Data will be lost when the app restarts"
            )
            return db
    
    def _handle_persistent_database(self, action: str, docs, has_existing_db: bool):
        """Handle persistent vector database creation/updating."""
        if action == "🆕 Start fresh (replace existing data)":
            return self._create_fresh_database(docs)
        
        elif has_existing_db:
            return self._update_existing_database(docs)
        
        else:
            return self._create_new_database(docs)
    
    def _create_fresh_database(self, docs):
        """Create fresh database (replacing existing)."""
        with st.spinner("Creating new knowledge base (replacing existing)..."):
            # Delete existing database first
            if vector_store_manager.database_exists():
                vector_store_manager.delete_database()
            
            # Create new database
            db = vector_store_manager.create_database(docs)
            vector_store_manager.save_database(db)
            
            ui_components.show_success_message("New knowledge base created successfully!")
            return db
    
    def _update_existing_database(self, docs):
        """Update existing database with new documents."""
        with st.spinner("Adding documents to existing knowledge base..."):
            # Load existing database
            existing_db = vector_store_manager.load_database()
            
            if not existing_db:
                ui_components.show_error_message("Failed to load existing database")
                return None
            
            # Merge new documents
            updated_db = vector_store_manager.merge_databases(existing_db, docs)
            vector_store_manager.save_database(updated_db)
            
            ui_components.show_success_message("Documents added to existing knowledge base!")
            return updated_db
    
    def _create_new_database(self, docs):
        """Create new persistent database."""
        with st.spinner("Creating new knowledge base..."):
            db = vector_store_manager.create_database(docs)
            vector_store_manager.save_database(db)
            
            ui_components.show_success_message("New knowledge base created and saved!")
            return db


def main():
    """Main entry point of the application."""
    app = GenAIChatbotApp()
    app.run()


if __name__ == "__main__":
    main()