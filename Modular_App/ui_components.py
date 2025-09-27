"""
UI components module for Streamlit interface elements.
"""
from typing import List, Optional, Tuple, Any
import streamlit as st
from config import config_manager
from document_processor import document_processor
from vector_store import vector_store_manager
from chat_engine import conversation_manager


class UIComponents:
    """Reusable UI components for the Streamlit application."""
    
    @staticmethod
    def show_app_header() -> None:
        """Display application header and title."""
        st.set_page_config(
            page_title="Gen AI PDF Chatbot",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title(config_manager.app_config.APP_TITLE)
        st.caption(f"Version {config_manager.app_config.APP_VERSION}")
    
    @staticmethod
    def show_database_selector() -> str:
        """
        Show database type selector.
        
        Returns:
            str: Selected database type ('faiss' or 'chroma')
        """
        st.sidebar.subheader("🗄️ Vector Database")
        
        db_info = vector_store_manager.get_database_info()
        
        # Show existing databases status
        if db_info["faiss_exists"]:
            st.sidebar.success("✅ FAISS database available")
        
        if db_info["chroma_exists"]:
            st.sidebar.success("✅ ChromaDB database available")
        
        if not db_info["faiss_exists"] and not db_info["chroma_exists"]:
            st.sidebar.info("📂 No databases found")
        
        # Database type selector
        db_type = st.sidebar.radio(
            "Choose database type:",
            ("FAISS", "ChromaDB"),
            help="FAISS: Fast similarity search. ChromaDB: Advanced vector database with metadata support."
        )
        
        return db_type.lower().replace("db", "")
    
    @staticmethod
    def show_action_selector(has_existing_db: bool) -> str:
        """
        Show action selector based on database availability.
        
        Args:
            has_existing_db (bool): Whether existing database exists
            
        Returns:
            str: Selected action
        """
        if has_existing_db:
            st.success("🗃️ Existing knowledge base found! You can chat directly or add more documents.")
            
            action = st.radio(
                "Choose an action:",
                (
                    "💬 Chat with existing knowledge base",
                    "📚 Add new PDFs to knowledge base", 
                    "🆕 Start fresh (replace existing data)"
                ),
                help="You can chat with existing documents or add more PDFs to expand the knowledge base."
            )
        else:
            st.info("📂 No existing knowledge base found. Please upload PDF files to get started.")
            action = "📚 Add new PDFs to knowledge base"
        
        return action
    
    @staticmethod
    def show_file_uploader(action: str) -> Optional[List]:
        """
        Show file uploader based on selected action.
        
        Args:
            action (str): Selected action
            
        Returns:
            Optional[List]: Uploaded files or None
        """
        if action == "💬 Chat with existing knowledge base":
            return None
        
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=config_manager.app_config.ALLOWED_FILE_TYPES,
            accept_multiple_files=True,
            help=f"Maximum file size: {config_manager.app_config.MAX_FILE_SIZE_MB}MB per file"
        )
        
        if uploaded_files:
            # Validate files
            valid_files, errors = document_processor.validate_files(uploaded_files)
            
            if errors:
                st.warning("⚠️ File validation errors:")
                for error in errors:
                    st.error(f"• {error}")
            
            if valid_files:
                st.success(f"✅ {len(valid_files)} valid file(s) ready for processing")
                return valid_files
        
        return None
    
    @staticmethod
    def show_storage_options(action: str, has_existing_db: bool) -> str:
        """
        Show storage options selector.
        
        Args:
            action (str): Selected action
            has_existing_db (bool): Whether existing database exists
            
        Returns:
            str: Selected storage option
        """
        if action == "💬 Chat with existing knowledge base":
            return "Save to disk (persistent)"
        
        default_index = 1 if has_existing_db else 0
        
        storage_option = st.radio(
            "Choose storage option:",
            ("Memory only (temporary)", "Save to disk (persistent)"),
            index=default_index,
            help="Memory only: Data lost when app restarts. Save to disk: Data persists between sessions."
        )
        
        return storage_option
    
    @staticmethod
    def show_processing_status(documents: List, action: str) -> None:
        """
        Show document processing status and statistics.
        
        Args:
            documents (List): Processed documents
            action (str): Current action
        """
        if not documents:
            return
        
        stats = document_processor.get_document_stats(documents)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 Document Chunks", stats["total_docs"])
        
        with col2:
            st.metric("📝 Total Characters", f"{stats['total_chars']:,}")
        
        with col3:
            st.metric("📊 Avg Chunk Length", stats["avg_doc_length"])
        
        with st.expander("📋 Document Details"):
            st.write(f"**Source Files:** {', '.join(stats['sources'])}")
            st.write(f"**Processing Action:** {action}")
    
    @staticmethod
    def show_chat_interface(vector_db: Any) -> None:
        """
        Show chat interface for interacting with documents.
        
        Args:
            vector_db: Vector database instance
        """
        # Initialize conversation manager
        conversation_manager.initialize_session_state()
        
        # Initialize chat engine if not ready
        chat_engine = st.session_state.chat_engine
        if not chat_engine.is_ready():
            chat_engine.initialize_chain(vector_db)
        
        # Display knowledge base info
        doc_count = vector_store_manager.get_document_count(vector_db)
        st.info(f"📊 Knowledge base contains {doc_count:,} document chunks")
        
        # Chat interface
        st.subheader("💬 Ask a question about your documents")
        
        # Display chat history
        conversation_manager.display_chat_history()
        
        # Chat input
        user_question = st.chat_input(
            "Type your question here...",
            key="chat_input"
        )
        
        if user_question:
            # Add user message to history
            conversation_manager.add_message("user", user_question)
            
            # Display user message
            with st.chat_message("user"):
                st.write(user_question)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    response = chat_engine.get_response(user_question)
                st.write(response)
                
                # Add assistant message to history
                conversation_manager.add_message("assistant", response)
        
        # Chat controls in sidebar
        UIComponents.show_chat_controls()
    
    @staticmethod
    def show_chat_controls() -> None:
        """Show chat control buttons in sidebar."""
        st.sidebar.subheader("💬 Chat Controls")
        
        # Conversation stats
        stats = conversation_manager.get_conversation_stats()
        if stats["has_conversation"]:
            st.sidebar.metric("Messages", stats["total_messages"])
            
            # Clear conversation button
            if st.sidebar.button("🗑️ Clear Conversation"):
                conversation_manager.clear_conversation()
                st.sidebar.success("Conversation cleared!")
                st.experimental_rerun()
            
            # Export conversation button
            if st.sidebar.button("📥 Export Conversation"):
                exported_text = conversation_manager.export_conversation()
                st.sidebar.download_button(
                    label="💾 Download Conversation",
                    data=exported_text,
                    file_name="conversation_export.txt",
                    mime="text/plain"
                )
    
    @staticmethod
    def show_database_management() -> None:
        """Show database management controls in sidebar."""
        st.sidebar.subheader("📚 Knowledge Base Management")
        
        db_info = vector_store_manager.get_database_info()
        current_type = db_info.get("current_type", "Not set")
        
        if current_type != "Not set":
            st.sidebar.info(f"Active: {current_type.upper()}")
            
            # Show database stats
            if vector_store_manager.database_exists():
                try:
                    db = vector_store_manager.load_database()
                    if db:
                        doc_count = vector_store_manager.get_document_count(db)
                        st.sidebar.metric("📄 Document Chunks", f"{doc_count:,}")
                except Exception:
                    st.sidebar.warning("⚠️ Could not load database stats")
                
                # Delete database button
                if st.sidebar.button(f"🗑️ Delete {current_type.upper()} Database"):
                    if vector_store_manager.delete_database():
                        st.sidebar.success("Database deleted successfully!")
                        st.experimental_rerun()
                    else:
                        st.sidebar.error("Failed to delete database")
    
    @staticmethod
    def show_help_section() -> None:
        """Show help and tips section."""
        with st.expander("💡 Tips for better results"):
            st.markdown("""
            **Getting Better Answers:**
            - Be specific in your questions
            - Ask about topics covered in your uploaded documents
            - Try rephrasing if you don't get the expected answer
            - The AI will only answer based on document content
            
            **Database Types:**
            - **FAISS**: Fast, lightweight, good for most use cases
            - **ChromaDB**: Advanced features, metadata support, better for complex queries
            
            **Storage Options:**
            - **Memory only**: Faster, temporary, good for one-time use
            - **Persistent**: Slower initially, builds knowledge base over time
            """)
    
    @staticmethod
    def show_error_message(message: str, details: Optional[str] = None) -> None:
        """
        Show error message with optional details.
        
        Args:
            message (str): Main error message
            details (Optional[str]): Additional error details
        """
        st.error(f"❌ {message}")
        
        if details:
            with st.expander("🔍 Error Details"):
                st.code(details)
    
    @staticmethod
    def show_success_message(message: str, details: Optional[str] = None) -> None:
        """
        Show success message with optional details.
        
        Args:
            message (str): Main success message
            details (Optional[str]): Additional details
        """
        st.success(f"✅ {message}")
        
        if details:
            st.info(details)


# Global UI components instance
ui_components = UIComponents()
