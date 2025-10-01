"""
Enhanced GenAI PDF Chatbot - Main Application with Source Attribution & Collaboration

A production-ready chatbot application with advanced features including:
- Document source attribution with citations
- Real-time collaborative workspaces
- Enhanced user interface with source tracking
- Multi-user support with WebSocket integration

Version: 3.0.0
Author: GenAI Team
"""

import streamlit as st
from dotenv import load_dotenv
import sys
import os
import asyncio
from typing import Optional, Any

# Load environment variables
load_dotenv()

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing modules
from Modular_App.config import config_manager
from Modular_App.auth import auth_manager
from Modular_App.document_processor import document_processor
from Modular_App.vector_store import vector_store_manager
from Modular_App.ui_components import ui_components

# Import enhanced modules
from Modular_App.source_attribution import SourceAttributionManager, CitationStyle
from Modular_App.collaboration import (
    WorkspaceManager, WebSocketConnectionManager, CollaborativeChatManager,
    UserRole as WorkspaceRole, WorkspacePermission, MessageType, create_collaboration_system
)
from Modular_App.attributed_chat_engine import (
    AttributedChatEngine, collaborative_attributed_chat_manager
)
from Modular_App.enhanced_vector_store import enhanced_vector_store_manager

from Modular_App.enhanced_ui_components import enhanced_ui_components

# --- TOP-LEVEL FULL SOURCE DISPLAY (before app class instantiation) ---
if 'show_full_source' in st.session_state and st.session_state['show_full_source']:
    source = st.session_state.get('full_source_data', {})
    st.markdown(f"### 📖 Source: {source.get('document_name', 'N/A')}")
    st.markdown(f"**Page:** {source.get('page_number', 'N/A')}")
    st.markdown(f"**Section:** {source.get('section_title', 'N/A')}")
    st.markdown(f"**Confidence:** {source.get('confidence_score', 'N/A')}")
    st.text_area("Full Content", source.get('text_content', ''), height=300)
    if st.button("Close", key="close_full_source_top"):
        st.session_state['show_full_source'] = False
        st.session_state['full_source_data'] = None


class EnhancedGenAIChatbotApp:
    """Enhanced main application class with attribution and collaboration."""
    
    def __init__(self):
        """Initialize the enhanced application."""
        self.config = config_manager
        self.attribution_manager = SourceAttributionManager()
        self.attributed_chat_engine = None  # Will be initialized when chat engine is available
        
        # Initialize collaboration system
        self.workspace_manager, self.connection_manager, self.chat_manager = create_collaboration_system()
        
        # Initialize Streamlit session state
        if "enhanced_app_initialized" not in st.session_state:
            self._initialize_enhanced_session_state()
    
    def _initialize_enhanced_session_state(self) -> None:
        """Initialize enhanced session state variables."""
        st.session_state.enhanced_app_initialized = True
        st.session_state.current_db_type = None
        st.session_state.vector_db = None
        st.session_state.attribution_enabled = True
        st.session_state.citation_style = CitationStyle.APA.value
        st.session_state.max_sources = 5
        st.session_state.collaboration_enabled = False
        st.session_state.current_workspace_id = None
        st.session_state.user_role = WorkspaceRole.COLLABORATOR.value
        st.session_state.workspace_members = []
        st.session_state.chat_history_with_sources = []
        
        # Initialize conversation manager
        from Modular_App.conversation_manager import conversation_manager
        conversation_manager.initialize_session_state()
    
    def _initialize_attributed_chat_engine(self, chat_engine, vector_store):
        """Initialize attributed chat engine when dependencies are available."""
        if self.attributed_chat_engine is None:
            self.attributed_chat_engine = AttributedChatEngine(
                chat_engine=chat_engine,
                vector_store=vector_store,
                attribution_manager=self.attribution_manager
            )
    
    def run(self) -> None:
        """Run the enhanced application."""
        try:
            # Show full source modal if needed (always at the top, outside any expander)
            enhanced_ui_components.show_full_source_if_needed()

            # Setup enhanced UI
            enhanced_ui_components.show_enhanced_app_header()

            # Authentication
            if not auth_manager.require_authentication():
                return

            # Show feature toggles
            self._show_feature_controls()

            # Main application flow
            if st.session_state.collaboration_enabled:
                self._run_collaborative_workflow()
            else:
                self._run_standard_workflow()

        except Exception as e:
            enhanced_ui_components.show_error_message(
                "An unexpected error occurred",
                str(e)
            )
            st.stop()
    
    def _show_feature_controls(self) -> None:
        """Show controls for enabling/disabling enhanced features."""
        st.sidebar.header("🚀 Enhanced Features")
        
        # Attribution settings
        with st.sidebar.expander("📍 Source Attribution", expanded=True):
            st.session_state.attribution_enabled = st.checkbox(
                "Enable Source Attribution", 
                value=st.session_state.attribution_enabled,
                help="Include source citations in responses"
            )
            
            if st.session_state.attribution_enabled:
                st.session_state.citation_style = st.selectbox(
                    "Citation Style",
                    options=[style.value for style in CitationStyle],
                    index=[style.value for style in CitationStyle].index(st.session_state.citation_style),
                    help="Choose citation format"
                )
                
                st.session_state.max_sources = st.slider(
                    "Maximum Sources",
                    min_value=1, max_value=10,
                    value=st.session_state.max_sources,
                    help="Maximum number of sources to include"
                )
        
        # Collaboration settings
        with st.sidebar.expander("🤝 Collaboration", expanded=False):
            collaboration_enabled = st.checkbox(
                "Enable Collaborative Mode", 
                value=st.session_state.collaboration_enabled,
                help="Work in shared workspaces with real-time features"
            )
            
            if collaboration_enabled != st.session_state.collaboration_enabled:
                st.session_state.collaboration_enabled = collaboration_enabled
                if collaboration_enabled:
                    st.success("Collaborative mode enabled! You can now create or join workspaces.")
                else:
                    st.info("Switched to standard mode.")
                st.rerun()
    
    def _run_standard_workflow(self) -> None:
        """Run the standard application workflow with enhanced attribution."""
        # Validate environment
        is_valid, error_msg = self.config.validate_environment()
        if not is_valid:
            enhanced_ui_components.show_error_message("Configuration Error", error_msg)
            st.stop()
        
        # Database type selection
        selected_db_type = enhanced_ui_components.show_enhanced_database_selector()
        
        # Set database type if changed
        if st.session_state.current_db_type != selected_db_type:
            enhanced_vector_store_manager.set_database_type(selected_db_type)
            st.session_state.current_db_type = selected_db_type
        
        # Show database management controls
        enhanced_ui_components.show_enhanced_database_management()
        
        # Check for existing database
        has_existing_db = enhanced_vector_store_manager.database_exists()
        
        # Action selection
        action = enhanced_ui_components.show_enhanced_action_selector(has_existing_db)
        
        # File upload (if needed)
        uploaded_files = enhanced_ui_components.show_enhanced_file_uploader(action)
        
        # Storage options
        storage_option = enhanced_ui_components.show_enhanced_storage_options(action, has_existing_db)
        
        # Process documents and setup chat
        vector_db = self._process_enhanced_workflow(action, uploaded_files, storage_option, has_existing_db)
        
        if vector_db:
            # Enhanced chat interface with attribution
            self._show_attributed_chat_interface(vector_db)
            
            # Enhanced help section
            enhanced_ui_components.show_enhanced_help_section()
    
    def _run_collaborative_workflow(self) -> None:
        """Run the collaborative workflow with workspaces."""
        # Workspace management interface
        workspace_action = enhanced_ui_components.show_workspace_selector()
        
        if workspace_action == "create":
            self._create_workspace_interface()
        elif workspace_action == "join":
            self._join_workspace_interface()
        elif workspace_action == "select":
            self._select_workspace_interface()
        
        # If workspace is selected, show collaborative interface
        if st.session_state.current_workspace_id:
            self._show_collaborative_interface()
    
    def _create_workspace_interface(self) -> None:
        """Interface for creating a new workspace."""
        st.subheader("🏢 Create New Workspace")
        
        with st.form("create_workspace"):
            workspace_name = st.text_input("Workspace Name", placeholder="My Team Workspace")
            workspace_description = st.text_area("Description", placeholder="Workspace for team collaboration...")
            is_public = st.checkbox("Public Workspace", help="Allow others to discover and join")
            
            if st.form_submit_button("Create Workspace"):
                if workspace_name:
                    try:
                        workspace = self.workspace_manager.create_workspace(
                            name=workspace_name,
                            description=workspace_description,
                            creator_id=auth_manager.get_current_user_id(),
                            creator_username=auth_manager.get_current_username()
                        )
                        
                        st.session_state.current_workspace_id = workspace.workspace_id
                        st.session_state.user_role = WorkspaceRole.OWNER.value
                        
                        st.success(f"Workspace '{workspace_name}' created successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Failed to create workspace: {str(e)}")
                else:
                    st.error("Please enter a workspace name")
    
    def _join_workspace_interface(self) -> None:
        """Interface for joining an existing workspace."""
        st.subheader("🚪 Join Workspace")
        
        with st.form("join_workspace"):
            workspace_code = st.text_input("Workspace Invite Code", placeholder="Enter invite code...")
            
            if st.form_submit_button("Join Workspace"):
                if workspace_code:
                    try:
                        success = self.workspace_manager.invite_user(
                            workspace_id=workspace_code,
                            user_id=auth_manager.get_current_user_id(),
                            username=auth_manager.get_current_username()
                        )
                        
                        if success:
                            st.success("Successfully joined workspace!")
                            st.rerun()
                        else:
                            st.error("Invalid invite code or workspace not found")
                            
                    except Exception as e:
                        st.error(f"Failed to join workspace: {str(e)}")
                else:
                    st.error("Please enter an invite code")
    
    def _select_workspace_interface(self) -> None:
        """Interface for selecting from user's workspaces."""
        user_workspaces = self.workspace_manager.get_user_workspaces(auth_manager.get_current_user_id())
        
        if user_workspaces:
            st.subheader("📂 Select Workspace")
            
            workspace_options = {ws.name: ws.id for ws in user_workspaces}
            selected_workspace_name = st.selectbox(
                "Choose workspace",
                options=list(workspace_options.keys()),
                help="Select a workspace to enter collaborative mode"
            )
            
            if st.button("Enter Workspace"):
                st.session_state.current_workspace_id = workspace_options[selected_workspace_name]
                
                # Get user role in workspace
                workspace = self.workspace_manager.get_workspace(st.session_state.current_workspace_id)
                user_member = next(
                    (member for member in workspace.users.values() if member.user_id == auth_manager.get_current_user_id()),
                    None
                )
                st.session_state.user_role = user_member.role.value if user_member else WorkspaceRole.COLLABORATOR.value
                
                st.success(f"Entered workspace: {selected_workspace_name}")
                st.rerun()
        else:
            st.info("You're not a member of any workspaces yet. Create one or ask for an invite!")
    
    def _show_collaborative_interface(self) -> None:
        """Show the main collaborative interface."""
        workspace = self.workspace_manager.get_workspace(st.session_state.current_workspace_id)
        
        if not workspace:
            st.error("Workspace not found")
            st.session_state.current_workspace_id = None
            st.rerun()
            return
        
        # Workspace header
        enhanced_ui_components.show_workspace_header(workspace, st.session_state.user_role)
        
        # Collaborative tabs
        tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📄 Documents", "👥 Members", "⚙️ Settings"])
        
        with tab1:
            self._show_collaborative_chat_tab(workspace)
        
        with tab2:
            self._show_collaborative_documents_tab(workspace)
        
        with tab3:
            self._show_workspace_members_tab(workspace)
        
        with tab4:
            self._show_workspace_settings_tab(workspace)
    
    def _show_collaborative_chat_tab(self, workspace) -> None:
        """Show collaborative chat interface."""
        st.subheader("💬 Collaborative Chat")
        
        # Real-time presence indicators
        enhanced_ui_components.show_presence_indicators(workspace.id)
        
        # Chat history with attribution
        self._show_collaborative_chat_history()
        
        # Chat input
        self._show_collaborative_chat_input(workspace.id)
    
    def _show_collaborative_documents_tab(self, workspace) -> None:
        """Show collaborative document management."""
        st.subheader("📄 Shared Documents")
        
        # Document upload for workspace
        enhanced_ui_components.show_workspace_document_uploader(workspace.id)
        
        # Shared document list
        enhanced_ui_components.show_workspace_documents(workspace.id)
    
    def _show_workspace_members_tab(self, workspace) -> None:
        """Show workspace members management."""
        st.subheader("👥 Workspace Members")
        
        # Member list
        enhanced_ui_components.show_workspace_members(workspace)
        
        # Invite management (if user has permission)
        if st.session_state.user_role in [WorkspaceRole.OWNER.value, WorkspaceRole.ADMIN.value]:
            enhanced_ui_components.show_member_invite_interface(workspace.id)
    
    def _show_workspace_settings_tab(self, workspace) -> None:
        """Show workspace settings."""
        st.subheader("⚙️ Workspace Settings")
        
        if st.session_state.user_role == WorkspaceRole.OWNER.value:
            enhanced_ui_components.show_workspace_settings_interface(workspace)
        else:
            st.info("Only workspace owners can modify settings")
    
    def _process_enhanced_workflow(self, action: str, uploaded_files, storage_option: str, has_existing_db: bool):
        """Process workflow with enhanced attribution tracking."""
        if action == "💬 Chat with existing knowledge base":
            return self._load_existing_enhanced_database()
        elif uploaded_files:
            return self._process_documents_with_attribution(action, uploaded_files, storage_option, has_existing_db)
        else:
            st.info("👆 Please upload PDF files to continue.")
            return None
    
    def _load_existing_enhanced_database(self):
        """Load existing database with enhanced features."""
        try:
            with st.spinner("Loading existing knowledge base with attribution support..."):
                db = enhanced_vector_store_manager.load_database()
                
                if db:
                    enhanced_ui_components.show_success_message("Enhanced knowledge base loaded successfully!")
                    return db
                else:
                    enhanced_ui_components.show_error_message("Database Error", "Failed to load existing database")
                    return None
                    
        except Exception as e:
            enhanced_ui_components.show_error_message("Error loading database", str(e))
            return None
    
    def _process_documents_with_attribution(self, action: str, uploaded_files, storage_option: str, has_existing_db: bool):
        """Process documents with source attribution tracking."""
        try:
            # Process documents with attribution
            with st.spinner("Processing documents with source attribution..."):
                documents = document_processor.load_documents(uploaded_files)
                
                if not documents:
                    enhanced_ui_components.show_error_message("Document Error", "No documents could be processed")
                    return None
                
                # Track documents for attribution
                doc_metadata = {}
                for uploaded_file in uploaded_files:
                    doc_id = self.attribution_manager.generate_document_id(uploaded_file.name)
                    doc_metadata[uploaded_file.name] = doc_id
                
                # Split documents with attribution tracking
                docs_with_attribution = []
                for doc in documents:
                    # Split document
                    doc_chunks = document_processor.split_documents([doc])
                    
                    # Track each chunk with attribution
                    for chunk in doc_chunks:
                        chunk_metadata = self.attribution_manager.track_document_chunk(
                            doc_id=doc_metadata.get(doc.metadata.get('source', 'unknown'), 'unknown'),
                            chunk_text=chunk.page_content,
                            document_name=doc.metadata.get('source', 'unknown'),
                            file_path=doc.metadata.get('source', ''),
                            page_number=chunk.metadata.get('page', None),
                            section_title=chunk.metadata.get('section', None)
                        )
                        
                        # Add attribution metadata to chunk
                        chunk.metadata.update({
                            'chunk_id': chunk_metadata.chunk_id,
                            'document_id': chunk_metadata.document_id,
                            'confidence_score': chunk_metadata.confidence_score,
                            'attribution_enabled': True
                        })
                        
                        docs_with_attribution.append(chunk)
                
                if not docs_with_attribution:
                    enhanced_ui_components.show_error_message("Attribution Error", "Document processing with attribution failed")
                    return None
            
            # Show enhanced processing status
            enhanced_ui_components.show_enhanced_processing_status(docs_with_attribution, action)
            
            # Handle enhanced vector database
            return self._handle_enhanced_vector_database(action, docs_with_attribution, storage_option, has_existing_db)
            
        except Exception as e:
            enhanced_ui_components.show_error_message("Error processing documents with attribution", str(e))
            return None
    
    def _handle_enhanced_vector_database(self, action: str, docs, storage_option: str, has_existing_db: bool):
        """Handle enhanced vector database with attribution metadata."""
        try:
            with st.spinner("Creating enhanced vector database..."):
                if action == "🔄 Add to existing knowledge base" and has_existing_db:
                    db = enhanced_vector_store_manager.add_documents_to_existing(docs, storage_option)
                else:
                    db = enhanced_vector_store_manager.create_database(docs, storage_option)
                
                if db:
                    enhanced_ui_components.show_success_message(
                        f"Enhanced vector database created/updated successfully! "
                        f"Processed {len(docs)} chunks with source attribution."
                    )
                    return db
                else:
                    enhanced_ui_components.show_error_message("Database Error", "Failed to create enhanced vector database")
                    return None
                    
        except Exception as e:
            enhanced_ui_components.show_error_message("Error creating enhanced vector database", str(e))
            return None
    
    def _show_attributed_chat_interface(self, vector_db: Any) -> None:
        """Show chat interface with source attribution."""
        st.subheader("💬 Chat with Attribution")
        
        # Attribution settings display
        if st.session_state.attribution_enabled:
            with st.expander("📍 Attribution Settings", expanded=False):
                st.write(f"**Citation Style:** {st.session_state.citation_style.upper()}")
                st.write(f"**Max Sources:** {st.session_state.max_sources}")
                st.write("**Source Attribution:** Enabled ✅")
        
        # Chat history with sources
        enhanced_ui_components.show_attributed_chat_history()
        
        # Chat input
        with st.form(key=f"attributed_chat_form_{len(st.session_state.chat_history_with_sources)}", clear_on_submit=True):
            user_question = st.text_area(
                "Ask a question about your documents:",
                height=100,
                placeholder="Type your question here...",
                key=f"user_question_{len(st.session_state.chat_history_with_sources)}"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                submit_button = st.form_submit_button("Send 🚀", use_container_width=True)

            if submit_button and user_question:
                self._process_attributed_chat_message(user_question, vector_db)
    
    def _process_attributed_chat_message(self, question: str, vector_db: Any) -> None:
        """Process chat message with attribution."""
        try:
            with st.spinner("Generating response with source attribution..."):
                # Initialize attributed chat engine if not already done
                if self.attributed_chat_engine is None:
                    # For now, initialize with None chat_engine as we'll use vector_db directly
                    self.attributed_chat_engine = AttributedChatEngine(
                        chat_engine=None,
                        vector_store=vector_db,
                        attribution_manager=self.attribution_manager
                    )
                
                # Configure attribution settings
                self.attributed_chat_engine.set_citation_style(CitationStyle(st.session_state.citation_style))
                self.attributed_chat_engine.set_max_sources(st.session_state.max_sources)
                
                # Get attributed response
                attributed_response = self.attributed_chat_engine.get_response_with_attribution(
                    question=question,
                    vector_db=vector_db
                )
                
                # Add to chat history
                if 'chat_history_with_sources' not in st.session_state:
                    st.session_state.chat_history_with_sources = []
                
                st.session_state.chat_history_with_sources.append({
                    'question': question,
                    'response': attributed_response.response_text,
                    'sources': [source.to_dict() for source in attributed_response.sources],
                    'citations': [citation.to_dict() for citation in attributed_response.citations],
                    'confidence': attributed_response.overall_confidence,
                    'timestamp': attributed_response.generated_at.isoformat(),
                    'response_id': attributed_response.response_id
                })
                st.rerun()
                
        except Exception as e:
            st.error(f"Error generating attributed response: {str(e)}")
    
    def _show_collaborative_chat_history(self) -> None:
        """Show collaborative chat history with real-time updates."""
        # This would integrate with WebSocket for real-time updates
        enhanced_ui_components.show_collaborative_chat_history(st.session_state.current_workspace_id)
    
    def _show_collaborative_chat_input(self, workspace_id: str) -> None:
        """Show collaborative chat input interface."""
        with st.form("collaborative_chat_form", clear_on_submit=True):
            user_message = st.text_area(
                "Send a message to the workspace:",
                height=80,
                placeholder="Type your message here..."
            )
            
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                send_button = st.form_submit_button("Send 💬")
            with col2:
                query_docs_button = st.form_submit_button("Query Docs 📄")
            
            if send_button and user_message:
                self._send_collaborative_message(workspace_id, user_message, "chat")
            elif query_docs_button and user_message:
                self._send_collaborative_message(workspace_id, user_message, "document_query")
    
    def _send_collaborative_message(self, workspace_id: str, message: str, message_type: str) -> None:
        """Send message to collaborative workspace."""
        try:
            if message_type == "chat":
                # Send regular chat message
                collaborative_attributed_chat_manager.send_chat_message(
                    workspace_id=workspace_id,
                    user_id=auth_manager.get_current_user_id(),
                    content=message
                )
            elif message_type == "document_query":
                # Process as document query with attribution
                collaborative_attributed_chat_manager.process_collaborative_query(
                    workspace_id=workspace_id,
                    user_id=auth_manager.get_current_user_id(),
                    query=message
                )
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to send message: {str(e)}")


def main():
    """Main entry point for the enhanced application."""
    # Only call set_page_config if not already called (should be first Streamlit command in entrypoint)
    # Remove this call here to avoid duplicate set_page_config errors.
    # Create and run enhanced application
    app = EnhancedGenAIChatbotApp()
    app.run()


if __name__ == "__main__":
    main()
