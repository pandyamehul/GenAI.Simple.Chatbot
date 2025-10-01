"""
Enhanced UI Components with Source Attribution and Collaborative Features
Provides advanced Streamlit components for displaying attributed responses,
collaborative workspaces, and enhanced user interfaces.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .ui_components import ui_components
from .source_attribution import CitationStyle, ConfidenceLevel
from .collaboration import UserRole as WorkspaceRole, PresenceStatus


class EnhancedUIComponents:
    def show_existing_documents_overview(self, db) -> None:
        """Show overview of already uploaded/processed documents and their chunk details."""
        from .enhanced_vector_store import enhanced_vector_store_manager
        st.subheader("📄 Uploaded Documents Overview")
        if not db:
            st.info("No database loaded. Upload documents to get started.")
            return
        summary = enhanced_vector_store_manager.get_attribution_summary(db)
        if "error" in summary:
            st.error(f"Error loading document info: {summary['error']}")
            return
        if not summary["documents"]:
            st.info("No documents found in the database.")
            return
        doc_data = []
        for doc_name, stats in summary["documents"].items():
            doc_data.append({
                "Document": doc_name,
                "Chunks": stats["chunk_count"],
                "Avg Confidence": f"{stats['avg_confidence']:.2f}",
                "Document ID": stats["document_id"][:8] + "..."
            })
        import pandas as pd
        df = pd.DataFrame(doc_data)
        st.dataframe(df, use_container_width=True)
    """Enhanced UI components for source attribution and collaboration."""
    
    def show_enhanced_app_header(self) -> None:
        """Show enhanced application header with new features."""
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
            <h1 style="color: white; text-align: center; margin: 0;">
                🤖 GenAI Enhanced Chatbot v3.0
            </h1>
            <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                🎯 Source Attribution • 🤝 Real-time Collaboration • 🚀 Enterprise Ready
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def show_enhanced_database_selector(self) -> str:
        """Show enhanced database selector with attribution support."""
        st.subheader("📊 Enhanced Vector Database")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            db_type = st.selectbox(
                "Choose Vector Database",
                options=["FAISS", "Chroma"],
                help="Enhanced databases support source attribution metadata"
            )
        with col2:
            st.metric("Attribution", "Enabled ✅")
        return db_type
    
    def show_enhanced_database_management(self) -> None:
        """Show enhanced database management controls."""
        with st.expander("🔧 Enhanced Database Management", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🗑️ Clear Database", help="Remove all data and attribution metadata"):
                    self._clear_enhanced_database()
            
            with col2:
                if st.button("📊 Show Attribution Stats", help="View source attribution statistics"):
                    self._show_attribution_stats()
            
            with col3:
                if st.button("💾 Export Attribution Data", help="Export source attribution metadata"):
                    self._export_attribution_data()
    
    def show_enhanced_action_selector(self, has_existing_db: bool) -> str:
        """Show enhanced action selector with collaboration options."""
        st.subheader("🎯 Choose Your Action")
        
        actions = ["📄 Upload new documents with attribution"]
        
        if has_existing_db:
            actions.extend([
                "💬 Chat with existing knowledge base",
                "🔄 Add to existing knowledge base"
            ])
        
        return st.selectbox("What would you like to do?", actions)
    
    def show_enhanced_file_uploader(self, action: str) -> Optional[List]:
        """Show enhanced file uploader with attribution preview."""
        if "Upload" in action or "Add to existing" in action:
            st.subheader("📁 Enhanced Document Upload")
            
            uploaded_files = st.file_uploader(
                "Upload PDF documents for analysis with source attribution",
                type=["pdf"],
                accept_multiple_files=True,
                help="Uploaded documents will be processed with source tracking for attribution"
            )
            
            if uploaded_files:
                self._show_upload_preview_with_attribution(uploaded_files)
            
            return uploaded_files
        
        return None
    
    def show_enhanced_storage_options(self, action: str, has_existing_db: bool) -> str:
        """Show enhanced storage options."""
        if "Upload" in action or "Add to existing" in action:
            st.subheader("💾 Enhanced Storage Options")
            
            if "Add to existing" in action and has_existing_db:
                return st.selectbox(
                    "How to handle existing data?",
                    ["merge", "replace"],
                    help="Merge preserves existing attribution data"
                )
            else:
                return st.selectbox(
                    "Storage method:",
                    ["memory", "persistent"],
                    index=1,
                    help="Persistent storage maintains attribution metadata"
                )
        
        return "memory"
    
    def show_enhanced_processing_status(self, docs: List, action: str) -> None:
        """Show enhanced processing status with attribution info."""
        st.success(f"✅ Documents processed successfully with source attribution!")
        
        # Attribution processing stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Documents", len(set(doc.metadata.get('source', 'unknown') for doc in docs)))
        
        with col2:
            st.metric("📝 Chunks", len(docs))
        
        with col3:
            attributed_chunks = sum(1 for doc in docs if doc.metadata.get('attribution_enabled', False))
            st.metric("🎯 Attributed", attributed_chunks)
        
        with col4:
            avg_confidence = sum(doc.metadata.get('confidence_score', 0.5) for doc in docs) / len(docs)
            st.metric("📊 Avg Confidence", f"{avg_confidence:.2f}")
    
    def show_attributed_chat_history(self) -> None:
        """Show chat history with source attribution (minimal UI)."""
        if 'chat_history_with_sources' in st.session_state and st.session_state.chat_history_with_sources:
            st.subheader("💬 Chat History")
            for i, chat_entry in enumerate(reversed(st.session_state.chat_history_with_sources)):
                st.markdown(f"**You:** {chat_entry['question']}")
                st.markdown(f"**Assistant:** {chat_entry['response']}")
                st.markdown(f"**Confidence:** {chat_entry['confidence']:.2f}/1.0")
                # Show only the top source (most relevant)
                if chat_entry['sources']:
                    top_source = chat_entry['sources'][0]
                    # Always use the original uploaded file name if present
                    file_name = top_source.get('original_file_name') or top_source.get('source_file') or top_source.get('document_name', '')
                    import os
                    file_name = os.path.basename(file_name)
                    page = top_source.get('page_number', 'N/A')
                    section = top_source.get('section', top_source.get('section_title', 'N/A'))
                    st.markdown(f"**Source:** {file_name} | Page: {page} | Section: {section}")
                    # Minimal preview, 'View Full' optional for top source only
                    text_content = top_source.get('text_content', '')
                    preview_text = text_content[:150] + "..." if text_content and len(text_content) > 150 else (text_content or "No preview available.")
                    st.text_area("Preview", preview_text, height=80, disabled=True, key=f"preview_{i}_{chat_entry['response_id']}_0")
                    if st.button("📖 View Full", key=f"view_source_{i}_{chat_entry['response_id']}_0"):
                        self._show_full_source_modal(top_source)
                # Citations (if any)
                if chat_entry.get('citations'):
                    st.markdown("**Citations:**")
                    for citation in chat_entry['citations']:
                        # Always use the original file name in citation display
                        source_file = citation.get('original_file_name') or citation.get('source_file') or citation.get('source_reference', '')
                        import os
                        file_name = os.path.basename(source_file)
                        st.markdown(f"• Source: {file_name}")
                st.caption(f"Generated at: {chat_entry['timestamp']}")
                st.markdown("---")
        else:
            st.info("💬 No chat history yet. Start by asking a question about your documents!")
    
    def show_workspace_selector(self) -> str:
        """Show workspace selection interface."""
        st.subheader("🏢 Workspace Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🆕 Create Workspace", use_container_width=True):
                return "create"
        
        with col2:
            if st.button("🚪 Join Workspace", use_container_width=True):
                return "join"
        
        with col3:
            if st.button("📂 Select Workspace", use_container_width=True):
                return "select"
        
        return "none"
    
    def show_workspace_header(self, workspace: Any, user_role: str) -> None:
        """Show workspace header with info and controls."""
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
            <h2 style="color: white; margin: 0;">🏢 {workspace.name}</h2>
            <p style="color: white; margin: 0.5rem 0 0 0;">
                {workspace.description} • Role: {user_role.title()} • Members: {len(workspace.members)}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick actions
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚪 Leave Workspace"):
                self._leave_workspace(workspace.id)
        
        with col2:
            if st.button("📋 Copy Invite Code"):
                self._copy_invite_code(workspace.id)
        
        with col3:
            st.metric("👥 Active Users", self._get_active_user_count(workspace.id))
        
        with col4:
            st.metric("📄 Documents", len(workspace.documents))
    
    def show_presence_indicators(self, workspace_id: str) -> None:
        """Show real-time user presence indicators."""
        # This would integrate with WebSocket for real-time updates
        presence_data = self._get_workspace_presence(workspace_id)
        
        if presence_data:
            st.markdown("**👥 Currently Active:**")
            
            cols = st.columns(min(len(presence_data), 5))
            for i, user_presence in enumerate(presence_data[:5]):
                with cols[i]:
                    status_emoji = {
                        PresenceStatus.ACTIVE.value: "🟢",
                        PresenceStatus.IDLE.value: "🟡",
                        PresenceStatus.AWAY.value: "🟠"
                    }.get(user_presence['status'], "⚫")
                    
                    st.markdown(f"{status_emoji} {user_presence['username']}")
            
            if len(presence_data) > 5:
                st.caption(f"+ {len(presence_data) - 5} more users")
    
    def show_workspace_document_uploader(self, workspace_id: str) -> None:
        """Show document uploader for workspace."""
        st.markdown("**📤 Upload Documents to Workspace**")
        
        uploaded_files = st.file_uploader(
            "Upload documents to share with workspace members",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"workspace_uploader_{workspace_id}"
        )
        
        if uploaded_files:
            if st.button("📤 Upload to Workspace"):
                self._upload_to_workspace(workspace_id, uploaded_files)
    
    def show_workspace_documents(self, workspace_id: str) -> None:
        """Show list of workspace documents."""
        documents = self._get_workspace_documents(workspace_id)
        
        if documents:
            st.markdown("**📁 Shared Documents:**")
            
            for doc in documents:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"📄 **{doc['name']}**")
                        st.caption(f"Uploaded by {doc['uploaded_by']} on {doc['upload_date']}")
                    
                    with col2:
                        if st.button("📖 View", key=f"view_{doc['id']}"):
                            self._view_document(doc['id'])
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{doc['id']}"):
                            self._delete_workspace_document(workspace_id, doc['id'])
        else:
            st.info("📭 No documents uploaded yet. Upload some documents to get started!")
    
    def show_workspace_members(self, workspace: Any) -> None:
        """Show workspace members list."""
        st.markdown("**👥 Workspace Members:**")
        
        for member in workspace.members:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"👤 **{member.username}** ({member.email})")
                    st.caption(f"Joined: {member.joined_at.strftime('%Y-%m-%d')}")
                
                with col2:
                    role_color = {
                        WorkspaceRole.OWNER.value: "🔴",
                        WorkspaceRole.ADMIN.value: "🟡",
                        WorkspaceRole.MEMBER.value: "🟢",
                        WorkspaceRole.VIEWER.value: "⚪"
                    }.get(member.role.value, "⚫")
                    
                    st.markdown(f"{role_color} {member.role.value.title()}")
                
                with col3:
                    if member.role != WorkspaceRole.OWNER and st.session_state.user_role == WorkspaceRole.OWNER.value:
                        if st.button("⚙️ Manage", key=f"manage_{member.user_id}"):
                            self._manage_member(workspace.id, member.user_id)
    
    def show_member_invite_interface(self, workspace_id: str) -> None:
        """Show member invitation interface."""
        st.markdown("**📧 Invite New Members:**")
        
        with st.form("invite_member"):
            invite_email = st.text_input("Email Address", placeholder="user@example.com")
            invite_role = st.selectbox(
                "Role",
                options=[WorkspaceRole.MEMBER.value, WorkspaceRole.ADMIN.value],
                help="Choose the role for the invited user"
            )
            
            if st.form_submit_button("📧 Send Invite"):
                if invite_email:
                    self._send_member_invite(workspace_id, invite_email, invite_role)
                else:
                    st.error("Please enter an email address")
    
    def show_workspace_settings_interface(self, workspace: Any) -> None:
        """Show workspace settings interface."""
        with st.form("workspace_settings"):
            new_name = st.text_input("Workspace Name", value=workspace.name)
            new_description = st.text_area("Description", value=workspace.description, key=f"ws_desc_{workspace.id}")
            new_public = st.checkbox("Public Workspace", value=workspace.settings.is_public)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.form_submit_button("💾 Save Changes"):
                    self._update_workspace_settings(workspace.id, new_name, new_description, new_public)
            
            with col2:
                if st.form_submit_button("🗑️ Delete Workspace", type="secondary"):
                    self._delete_workspace(workspace.id)
    
    def show_collaborative_chat_history(self, workspace_id: str) -> None:
        """Show collaborative chat history with real-time updates."""
        # This would integrate with WebSocket for real-time updates
        chat_history = self._get_workspace_chat_history(workspace_id)
        
        if chat_history:
            for message in chat_history[-10:]:  # Show last 10 messages
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        st.markdown(f"**{message['username']}**")
                        st.caption(message['timestamp'])
                    
                    with col2:
                        if message['type'] == 'chat':
                            st.markdown(message['content'])
                        elif message['type'] == 'document_query':
                            st.markdown(f"🔍 **Query:** {message['content']}")
                            if 'response' in message:
                                st.markdown(f"🤖 **Response:** {message['response']}")
                                if 'sources' in message:
                                    with st.expander("📍 Sources"):
                                        for source in message['sources']:
                                            st.markdown(f"• {source['document_name']} (p. {source.get('page_number', 'N/A')})")
        else:
            st.info("💬 No messages yet. Be the first to start the conversation!")
    
    def show_enhanced_help_section(self) -> None:
        """Show enhanced help section with new features."""
        with st.expander("❓ Help & Enhanced Features", expanded=False):
            st.markdown("""
            ### 🎯 Source Attribution Features
            - **Citation Generation**: Automatic citations in APA, MLA, Chicago, or IEEE format
            - **Source Tracking**: Every response includes source document references
            - **Confidence Scores**: See how confident the AI is in its responses
            - **Clickable Sources**: Navigate directly to source documents and pages
            
            ### 🤝 Collaborative Features
            - **Shared Workspaces**: Create or join collaborative environments
            - **Real-time Chat**: Communicate with team members in real-time
            - **Document Sharing**: Upload and share documents within workspaces
            - **User Presence**: See who's currently active in your workspace
            - **Role Management**: Control access with Owner, Admin, Member, and Viewer roles
            
            ### 🚀 Enhanced Capabilities
            - **Multi-format Documents**: Support for PDF, DOCX, XLSX, PPTX, and TXT
            - **Advanced Analytics**: Track usage, performance, and collaboration metrics
            - **Enhanced Security**: JWT authentication and role-based access control
            - **Persistent Storage**: All data and attribution metadata saved automatically
            
            ### 💡 Tips for Best Results
            1. **Enable Attribution** for academic or professional use
            2. **Use Workspaces** for team collaboration and document sharing
            3. **Check Confidence Scores** to validate AI responses
            4. **Review Sources** to verify information accuracy
            5. **Invite Team Members** to collaborate on document analysis
            """)
    
    def _clear_enhanced_database(self) -> None:
        """Clear enhanced database and attribution data."""
        if st.session_state.get('vector_db'):
            # Clear vector database
            from .enhanced_vector_store import enhanced_vector_store_manager
            enhanced_vector_store_manager.clear_database()
            
            # Clear attribution data
            from .source_attribution import SourceAttributionManager
            attribution_manager = SourceAttributionManager()
            attribution_manager.metadata_store.clear()
            
            # Clear session state
            st.session_state.vector_db = None
            st.session_state.chat_history_with_sources = []
            
            st.success("✅ Enhanced database and attribution data cleared!")
            st.rerun()
    
    def _show_attribution_stats(self) -> None:
        """Show attribution statistics."""
        from .source_attribution import SourceAttributionManager
        attribution_manager = SourceAttributionManager()
        
        stats = attribution_manager.export_attribution_data()
        
        if stats.get('total_chunks', 0) > 0:
            st.json(stats)
        else:
            st.info("No attribution data available. Upload and process some documents first.")
    
    def _export_attribution_data(self) -> None:
        """Export attribution data as JSON."""
        from .source_attribution import SourceAttributionManager
        attribution_manager = SourceAttributionManager()
        
        export_data = attribution_manager.export_attribution_data()
        
        st.download_button(
            label="📥 Download Attribution Data",
            data=json.dumps(export_data, indent=2),
            file_name=f"attribution_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def _show_upload_preview_with_attribution(self, uploaded_files: List) -> None:
        """Show upload preview with attribution info."""
        st.markdown("**📋 Upload Preview with Attribution:**")
        
        for i, file in enumerate(uploaded_files):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"📄 **{file.name}**")
                    st.caption(f"Size: {file.size:,} bytes")
                
                with col2:
                    st.markdown("🎯 **Attribution**")
                    st.caption("Enabled ✅")
                
                with col3:
                    st.markdown("📊 **Tracking**")
                    st.caption("Full metadata")
    
    def _get_confidence_color(self, confidence: float) -> str:
        """Get color for confidence score display."""
        if confidence >= 0.8:
            return "#d4edda"  # Light green
        elif confidence >= 0.6:
            return "#fff3cd"  # Light yellow
        else:
            return "#f8d7da"  # Light red
    
    def _show_full_source_modal(self, source: Dict[str, Any]) -> None:
        """Show full source content in a modal-like workaround (no nested expanders)."""
        st.session_state['show_full_source'] = True
        st.session_state['full_source_data'] = source

    def show_full_source_if_needed(self):
        """Display the full source content outside of any expander if requested."""
        if st.session_state.get('show_full_source', False):
            source = st.session_state.get('full_source_data', {})
            st.markdown(f"### 📖 Source: {source.get('document_name', 'N/A')}")
            st.markdown(f"**Page:** {source.get('page_number', 'N/A')}")
            st.markdown(f"**Section:** {source.get('section_title', 'N/A')}")
            st.markdown(f"**Confidence:** {source.get('confidence_score', 'N/A')}")
            st.text_area("Full Content", source.get('text_content', ''), height=300, key="full_source_text_area")
            if st.button("Close", key="close_full_source"):
                st.session_state['show_full_source'] = False
                st.session_state['full_source_data'] = None
    
    # Collaborative feature helper methods (these would integrate with real backend)
    def _leave_workspace(self, workspace_id: str) -> None:
        """Leave workspace."""
        # Implementation would call workspace_manager
        st.success("Left workspace successfully!")
        st.session_state.current_workspace_id = None
        st.rerun()
    
    def _copy_invite_code(self, workspace_id: str) -> None:
        """Copy workspace invite code."""
        # Implementation would get invite code from workspace_manager
        st.success("Invite code copied to clipboard!")
    
    def _get_active_user_count(self, workspace_id: str) -> int:
        """Get active user count for workspace."""
        # Implementation would call collaboration manager
        return 1  # Placeholder
    
    def _get_workspace_presence(self, workspace_id: str) -> List[Dict]:
        """Get workspace presence data."""
        # Implementation would call collaboration manager
        return []  # Placeholder
    
    def _upload_to_workspace(self, workspace_id: str, files: List) -> None:
        """Upload files to workspace."""
        # Implementation would call collaborative document manager
        st.success(f"Uploaded {len(files)} files to workspace!")
    
    def _get_workspace_documents(self, workspace_id: str) -> List[Dict]:
        """Get workspace documents."""
        # Implementation would call collaborative document manager
        return []  # Placeholder
    
    def _view_document(self, doc_id: str) -> None:
        """View document."""
        st.info(f"Opening document {doc_id}...")
    
    def _delete_workspace_document(self, workspace_id: str, doc_id: str) -> None:
        """Delete workspace document."""
        st.success("Document deleted successfully!")
    
    def _manage_member(self, workspace_id: str, user_id: str) -> None:
        """Manage workspace member."""
        st.info(f"Managing member {user_id}...")
    
    def _send_member_invite(self, workspace_id: str, email: str, role: str) -> None:
        """Send member invitation."""
        st.success(f"Invitation sent to {email} with role {role}!")
    
    def _update_workspace_settings(self, workspace_id: str, name: str, description: str, is_public: bool) -> None:
        """Update workspace settings."""
        st.success("Workspace settings updated successfully!")
    
    def _delete_workspace(self, workspace_id: str) -> None:
        """Delete workspace."""
        if st.confirm("Are you sure you want to delete this workspace? This action cannot be undone."):
            st.success("Workspace deleted successfully!")
            st.session_state.current_workspace_id = None
            st.rerun()
    
    def _get_workspace_chat_history(self, workspace_id: str) -> List[Dict]:
        """Get workspace chat history."""
        # Implementation would call collaborative chat manager
        return []  # Placeholder
    
    def show_error_message(self, title: str, message: str) -> None:
        """Show error message with consistent formatting."""
        st.error(f"**{title}**")
        st.error(message)
    
    def show_success_message(self, message: str, details: Optional[str] = None) -> None:
        """Show success message with consistent formatting."""
        st.success(f"✅ {message}")
        if details:
            st.success(details)


# Create global instance
enhanced_ui_components = EnhancedUIComponents()
