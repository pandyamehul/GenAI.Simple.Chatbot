"""
Comprehensive Test Suite for Enhanced Features
Tests source attribution, collaborative features, and integration points.
"""

import pytest
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Modular_App.source_attribution import (
    SourceAttributionManager, ChunkMetadata, Citation, 
    AttributedResponse, CitationStyle, ConfidenceLevel
)
from Modular_App.collaboration import (
    WorkspaceManager, CollaborativeChatManager, WebSocketConnectionManager,
    Workspace, WorkspaceMember, WorkspaceRole, PresenceStatus
)
from Modular_App.attributed_chat_engine import AttributedChatEngine
from Modular_App.enhanced_vector_store import enhanced_vector_store_manager
from Modular_App.conversation_manager import conversation_manager


class TestSourceAttribution:
    """Test suite for source attribution features."""
    
    def setup_method(self):
        """Setup test environment."""
        self.attribution_manager = SourceAttributionManager()
    
    def test_chunk_metadata_creation(self):
        """Test creation of chunk metadata."""
        chunk_metadata = self.attribution_manager.track_document_chunk(
            doc_id="test_doc_001",
            chunk_text="This is a test chunk of text for attribution testing.",
            document_name="test_document.pdf",
            file_path="/path/to/test_document.pdf",
            page_number=1,
            section_title="Introduction"
        )
        
        assert chunk_metadata.document_id == "test_doc_001"
        assert chunk_metadata.document_name == "test_document.pdf"
        assert chunk_metadata.page_number == 1
        assert chunk_metadata.section_title == "Introduction"
        assert chunk_metadata.confidence_score > 0
        assert chunk_metadata.word_count > 0
        assert chunk_metadata.character_count > 0
    
    def test_citation_generation(self):
        """Test citation generation in different styles."""
        # Create sample metadata
        chunk_metadata = ChunkMetadata(
            document_id="test_doc_001",
            chunk_id="chunk_001",
            document_name="sample_paper.pdf",
            file_path="/path/to/sample_paper.pdf",
            page_number=15,
            section_title="Results",
            text_content="Sample text content for testing citations.",
            coordinates=None,
            extraction_timestamp=datetime.utcnow(),
            confidence_score=0.85
        )
        
        # Test APA citation
        attributed_response = self.attribution_manager.generate_attributed_response(
            response_text="This is a test response.",
            sources=[chunk_metadata],
            citation_style=CitationStyle.APA
        )
        
        assert len(attributed_response.citations) == 1
        assert attributed_response.citations[0].citation_format == CitationStyle.APA
        assert "sample_paper.pdf" in attributed_response.citations[0].source_reference
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        chunk_metadata = self.attribution_manager.track_document_chunk(
            doc_id="test_doc_002",
            chunk_text="This is a longer chunk of text that should have a higher confidence score due to its length and content.",
            document_name="detailed_document.pdf",
            file_path="/path/to/detailed_document.pdf"
        )
        
        # Confidence should be reasonable for good content
        assert 0.3 <= chunk_metadata.confidence_score <= 1.0
    
    def test_attributed_response_creation(self):
        """Test creation of attributed responses."""
        # Create multiple chunk metadata
        chunks = []
        for i in range(3):
            chunk = self.attribution_manager.track_document_chunk(
                doc_id=f"doc_{i}",
                chunk_text=f"Content from document {i}",
                document_name=f"document_{i}.pdf",
                file_path=f"/path/to/document_{i}.pdf",
                page_number=i+1
            )
            chunks.append(chunk)
        
        attributed_response = self.attribution_manager.generate_attributed_response(
            response_text="This response references multiple sources.",
            sources=chunks,
            ai_provider="test_provider",
            model_used="test_model"
        )
        
        assert len(attributed_response.sources) == 3
        assert len(attributed_response.citations) == 3
        assert attributed_response.ai_provider == "test_provider"
        assert attributed_response.model_used == "test_model"
        assert attributed_response.overall_confidence > 0


class TestCollaborativeFeatures:
    """Test suite for collaborative features."""
    
    def setup_method(self):
        """Setup test environment."""
        self.workspace_manager = WorkspaceManager()
        self.chat_manager = CollaborativeChatManager()
        self.connection_manager = WebSocketConnectionManager()
    
    def test_workspace_creation(self):
        """Test workspace creation."""
        workspace = self.workspace_manager.create_workspace(
            owner_id="user_001",
            name="Test Workspace",
            description="A workspace for testing"
        )
        
        assert workspace.name == "Test Workspace"
        assert workspace.owner_id == "user_001"
        assert len(workspace.members) == 1
        assert workspace.members[0].role == WorkspaceRole.OWNER
    
    def test_workspace_member_management(self):
        """Test adding and managing workspace members."""
        # Create workspace
        workspace = self.workspace_manager.create_workspace(
            owner_id="user_001",
            name="Member Test Workspace",
            description="Testing member management"
        )
        
        # Add member
        success = self.workspace_manager.add_member(
            workspace_id=workspace.id,
            user_id="user_002",
            username="test_user_2",
            email="user2@test.com",
            role=WorkspaceRole.MEMBER
        )
        
        assert success
        updated_workspace = self.workspace_manager.get_workspace(workspace.id)
        assert len(updated_workspace.members) == 2
        
        # Find the new member
        new_member = next(
            (m for m in updated_workspace.members if m.user_id == "user_002"),
            None
        )
        assert new_member is not None
        assert new_member.role == WorkspaceRole.MEMBER
    
    def test_chat_message_handling(self):
        """Test collaborative chat message handling."""
        # Create workspace
        workspace = self.workspace_manager.create_workspace(
            owner_id="user_001",
            name="Chat Test Workspace",
            description="Testing chat functionality"
        )
        
        # Send chat message
        message = self.chat_manager.send_chat_message(
            workspace_id=workspace.id,
            user_id="user_001",
            username="test_user",
            content="Hello, this is a test message!"
        )
        
        assert message.workspace_id == workspace.id
        assert message.user_id == "user_001"
        assert message.content == "Hello, this is a test message!"
        assert message.message_type == "text"
    
    def test_websocket_connection_management(self):
        """Test WebSocket connection management."""
        workspace_id = "test_workspace_001"
        user_id = "user_001"
        
        # Simulate connection
        self.connection_manager.add_user_to_workspace(workspace_id, user_id)
        
        # Check if user is in workspace
        workspace_users = self.connection_manager.get_workspace_users(workspace_id)
        assert user_id in workspace_users
        
        # Simulate disconnection
        self.connection_manager.remove_user_from_workspace(workspace_id, user_id)
        workspace_users = self.connection_manager.get_workspace_users(workspace_id)
        assert user_id not in workspace_users


class TestAttributedChatEngine:
    """Test suite for attributed chat engine."""
    
    def setup_method(self):
        """Setup test environment."""
        self.attributed_chat_engine = AttributedChatEngine()
    
    def test_citation_style_setting(self):
        """Test setting citation style."""
        self.attributed_chat_engine.set_citation_style(CitationStyle.MLA)
        assert self.attributed_chat_engine.citation_style == CitationStyle.MLA
    
    def test_max_sources_setting(self):
        """Test setting maximum sources."""
        self.attributed_chat_engine.set_max_sources(7)
        assert self.attributed_chat_engine.max_sources == 7
        
        # Test bounds
        self.attributed_chat_engine.set_max_sources(-1)
        assert self.attributed_chat_engine.max_sources == 1
        
        self.attributed_chat_engine.set_max_sources(15)
        assert self.attributed_chat_engine.max_sources == 10


class TestConversationManager:
    """Test suite for conversation manager."""
    
    def setup_method(self):
        """Setup test environment."""
        self.conversation_manager = conversation_manager
        # Clear any existing history
        self.conversation_manager.clear_history()
    
    def test_attributed_message_storage(self):
        """Test storing attributed messages."""
        # Create sample attributed response
        chunk_metadata = ChunkMetadata(
            document_id="test_doc",
            chunk_id="test_chunk",
            document_name="test.pdf",
            file_path="/test.pdf",
            text_content="Test content",
            extraction_timestamp=datetime.utcnow(),
            confidence_score=0.8
        )
        
        citation = Citation(
            citation_id="cite_1",
            text_snippet="Test snippet",
            source_reference="Test (2024)",
            citation_format=CitationStyle.APA
        )
        
        attributed_response = AttributedResponse(
            response_id="resp_001",
            response_text="Test response",
            sources=[chunk_metadata],
            citations=[citation],
            overall_confidence=0.85
        )
        
        # Add message
        self.conversation_manager.add_attributed_message(
            question="Test question?",
            attributed_response=attributed_response
        )
        
        # Verify storage
        history = self.conversation_manager.get_attributed_history()
        assert len(history) == 1
        assert history[0]['question'] == "Test question?"
        assert history[0]['confidence'] == 0.85
        assert len(history[0]['sources']) == 1
        assert len(history[0]['citations']) == 1
    
    def test_conversation_summary(self):
        """Test conversation summary generation."""
        # Add some messages first
        for i in range(3):
            self.conversation_manager.add_regular_message(
                question=f"Question {i}?",
                answer=f"Answer {i}"
            )
        
        summary = self.conversation_manager.get_conversation_summary()
        assert summary['total_messages'] == 3
        assert summary['has_attribution'] == False


class TestIntegration:
    """Integration tests for enhanced features."""
    
    def test_attribution_vector_store_integration(self):
        """Test integration between attribution and vector store."""
        # This would test the full pipeline from document upload
        # to vector store creation with attribution metadata
        pass
    
    def test_collaborative_attribution_integration(self):
        """Test integration between collaborative features and attribution."""
        # This would test collaborative queries with attribution
        pass


def run_comprehensive_tests():
    """Run all tests and provide detailed results."""
    print("🧪 Running Enhanced Features Test Suite...")
    print("=" * 50)
    
    test_results = {
        "source_attribution": [],
        "collaborative_features": [],
        "attributed_chat_engine": [],
        "conversation_manager": [],
        "integration": []
    }
    
    # Run Source Attribution Tests
    print("\n📍 Testing Source Attribution...")
    try:
        test_attribution = TestSourceAttribution()
        test_attribution.setup_method()
        
        test_attribution.test_chunk_metadata_creation()
        test_results["source_attribution"].append("✅ Chunk metadata creation")
        
        test_attribution.test_citation_generation()
        test_results["source_attribution"].append("✅ Citation generation")
        
        test_attribution.test_confidence_calculation()
        test_results["source_attribution"].append("✅ Confidence calculation")
        
        test_attribution.test_attributed_response_creation()
        test_results["source_attribution"].append("✅ Attributed response creation")
        
    except Exception as e:
        test_results["source_attribution"].append(f"❌ Error: {str(e)}")
    
    # Run Collaborative Features Tests
    print("\n🤝 Testing Collaborative Features...")
    try:
        test_collab = TestCollaborativeFeatures()
        test_collab.setup_method()
        
        test_collab.test_workspace_creation()
        test_results["collaborative_features"].append("✅ Workspace creation")
        
        test_collab.test_workspace_member_management()
        test_results["collaborative_features"].append("✅ Member management")
        
        test_collab.test_chat_message_handling()
        test_results["collaborative_features"].append("✅ Chat message handling")
        
        test_collab.test_websocket_connection_management()
        test_results["collaborative_features"].append("✅ WebSocket management")
        
    except Exception as e:
        test_results["collaborative_features"].append(f"❌ Error: {str(e)}")
    
    # Run Attributed Chat Engine Tests
    print("\n🤖 Testing Attributed Chat Engine...")
    try:
        test_chat = TestAttributedChatEngine()
        test_chat.setup_method()
        
        test_chat.test_citation_style_setting()
        test_results["attributed_chat_engine"].append("✅ Citation style setting")
        
        test_chat.test_max_sources_setting()
        test_results["attributed_chat_engine"].append("✅ Max sources setting")
        
    except Exception as e:
        test_results["attributed_chat_engine"].append(f"❌ Error: {str(e)}")
    
    # Run Conversation Manager Tests
    print("\n💬 Testing Conversation Manager...")
    try:
        test_conv = TestConversationManager()
        test_conv.setup_method()
        
        test_conv.test_attributed_message_storage()
        test_results["conversation_manager"].append("✅ Attributed message storage")
        
        test_conv.test_conversation_summary()
        test_results["conversation_manager"].append("✅ Conversation summary")
        
    except Exception as e:
        test_results["conversation_manager"].append(f"❌ Error: {str(e)}")
    
    # Print Results
    print("\n" + "=" * 50)
    print("🧪 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in test_results.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for result in results:
            print(f"  {result}")
            total_tests += 1
            if result.startswith("✅"):
                passed_tests += 1
    
    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Enhanced features are ready.")
        return True
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed. Review implementation.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
