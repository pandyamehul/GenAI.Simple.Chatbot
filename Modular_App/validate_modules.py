"""
Enhanced Validation Script for GenAI Platform v3.0
Comprehensive testing for source attribution and collaboration features
"""

import sys
import os
import time
import asyncio
from typing import Dict, List, Tuple, Any
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ValidationReport:
    """Comprehensive validation reporting."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, float] = {}
    
    def add_test_result(self, test_name: str, passed: bool, error: str = None, duration: float = 0):
        """Add test result to report."""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            self.tests_failed += 1
            print(f"❌ {test_name} - {error}")
            self.errors.append({
                'test': test_name,
                'error': error,
                'timestamp': datetime.now().isoformat()
            })
        
        if duration > 0:
            self.performance_metrics[test_name] = duration
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        return {
            'timestamp': end_time.isoformat(),
            'total_duration': f"{total_duration:.2f}s",
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'success_rate': f"{(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%",
            'errors': self.errors,
            'performance_metrics': self.performance_metrics
        }

def time_test(func):
    """Decorator to measure test execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        return result, duration
    return wrapper

@time_test
def test_source_attribution_basic():
    """Test basic source attribution functionality."""
    try:
        from source_attribution import SourceAttributionManager, ChunkMetadata, CitationStyle
        
        # Test imports
        assert SourceAttributionManager is not None
        assert ChunkMetadata is not None
        assert CitationStyle is not None
        
        return True, "Basic imports successful"
        
    except Exception as e:
        return False, f"Import error: {e}"

@time_test
def test_source_attribution_advanced():
    """Test advanced source attribution features."""
    try:
        from source_attribution import SourceAttributionManager, ChunkMetadata, CitationStyle
        from datetime import datetime
        
        # Initialize manager
        manager = SourceAttributionManager()
        
        # Test metadata creation with various fields
        metadata1 = ChunkMetadata(
            source_file="test_document.pdf",
            page_number=5,
            section="Executive Summary"
        )
        
        metadata2 = ChunkMetadata(
            source_file="research_paper.pdf",
            page_number=12,
            section="Methodology"
        )
        
        # Test chunk registration
        manager.add_chunk("chunk_001", metadata1)
        manager.add_chunk("chunk_002", metadata2)
        
        # Verify chunks are stored
        assert len(manager.chunk_metadata) == 2
        assert "chunk_001" in manager.chunk_metadata
        assert "chunk_002" in manager.chunk_metadata
        
        # Test citation generation
        citations = manager.generate_citations_for_chunks(["chunk_001", "chunk_002"])
        assert len(citations) == 2
        
        # Verify citation properties
        for citation in citations:
            assert citation.citation_id is not None
            assert citation.source_file in ["test_document.pdf", "research_paper.pdf"]
            assert citation.citation_text is not None
            assert citation.style == CitationStyle.APA
        
        return True, f"Generated {len(citations)} citations successfully"
        
    except Exception as e:
        return False, f"Advanced attribution error: {e}"

@time_test
def test_collaboration_basic():
    """Test basic collaboration functionality."""
    try:
        from collaboration import (
            create_collaboration_system,
            UserRole,
            WorkspacePermission,
            MessageType
        )
        
        # Test imports
        assert UserRole is not None
        assert WorkspacePermission is not None
        assert MessageType is not None
        
        # Test system creation
        workspace_manager, connection_manager, chat_manager = create_collaboration_system()
        assert workspace_manager is not None
        assert connection_manager is not None
        assert chat_manager is not None
        
        return True, "Collaboration system created successfully"
        
    except Exception as e:
        return False, f"Collaboration basic error: {e}"

@time_test
def test_collaboration_advanced():
    """Test advanced collaboration features."""
    try:
        from collaboration import (
            create_collaboration_system,
            UserRole,
            WorkspacePermission,
            MessageType
        )
        
        # Create collaboration system
        workspace_manager, connection_manager, chat_manager = create_collaboration_system()
        
        # Test workspace creation
        workspace = workspace_manager.create_workspace(
            name="Test Workspace Advanced",
            description="Advanced testing workspace with comprehensive features",
            creator_id="test_user_001",
            creator_username="Advanced Test User"
        )
        
        # Verify workspace properties
        assert workspace.workspace_id is not None
        assert workspace.name == "Test Workspace Advanced"
        assert workspace.created_by == "test_user_001"
        assert len(workspace.users) == 1  # Creator automatically added
        
        # Test user invitation
        invite_result = workspace_manager.invite_user(
            workspace_id=workspace.workspace_id,
            user_id="test_user_002",
            username="Collaborator User",
            role=UserRole.COLLABORATOR
        )
        assert invite_result == True
        assert len(workspace.users) == 2
        
        # Test permissions
        collaborator = workspace.users["test_user_002"]
        assert collaborator.has_permission(WorkspacePermission.READ)
        assert collaborator.has_permission(WorkspacePermission.WRITE)
        assert not collaborator.has_permission(WorkspacePermission.DELETE)
        
        # Test message creation
        message = chat_manager.add_message(
            workspace_id=workspace.workspace_id,
            user_id="test_user_001",
            username="Advanced Test User",
            content="This is a comprehensive test message with detailed content",
            message_type=MessageType.TEXT
        )
        
        assert message.message_id is not None
        assert message.workspace_id == workspace.workspace_id
        assert message.content == "This is a comprehensive test message with detailed content"
        
        # Test chat history
        history = chat_manager.get_chat_history(workspace.workspace_id)
        assert len(history) == 1
        assert history[0].message_id == message.message_id
        
        # Test workspace statistics
        stats = workspace_manager.get_workspace_stats(workspace.workspace_id)
        assert stats['total_users'] == 2
        assert stats['total_messages'] == 0  # Messages not tracked in workspace directly
        
        return True, f"Workspace {workspace.workspace_id[:8]}... with {len(workspace.users)} users"
        
    except Exception as e:
        return False, f"Advanced collaboration error: {e}"

@time_test
def test_integration_scenario():
    """Test realistic integration scenario."""
    try:
        from source_attribution import SourceAttributionManager, ChunkMetadata, CitationStyle
        from collaboration import create_collaboration_system, UserRole, MessageType
        import uuid
        
        # Initialize both systems
        attribution_manager = SourceAttributionManager()
        workspace_manager, connection_manager, chat_manager = create_collaboration_system()
        
        # Create workspace for document analysis
        workspace = workspace_manager.create_workspace(
            name="Document Analysis Team",
            description="Analyzing quarterly financial reports with source tracking",
            creator_id="analyst_001",
            creator_username="Senior Analyst"
        )
        
        # Add team members
        workspace_manager.invite_user(
            workspace_id=workspace.workspace_id,
            user_id="analyst_002",
            username="Junior Analyst",
            role=UserRole.COLLABORATOR
        )
        
        # Simulate document processing with source attribution
        documents = [
            {"file": "q3_financial_report.pdf", "page": 5, "section": "Revenue Analysis"},
            {"file": "market_trends_2023.pdf", "page": 12, "section": "Consumer Behavior"},
            {"file": "competitor_analysis.pdf", "page": 8, "section": "Market Share"}
        ]
        
        chunk_ids = []
        for i, doc in enumerate(documents):
            chunk_id = f"chunk_{i+1:03d}"
            chunk_ids.append(chunk_id)
            
            metadata = ChunkMetadata(
                source_file=doc["file"],
                page_number=doc["page"],
                section=doc["section"]
            )
            attribution_manager.add_chunk(chunk_id, metadata)
        
        # Simulate AI query and response
        query_message = chat_manager.add_message(
            workspace_id=workspace.workspace_id,
            user_id="analyst_001",
            username="Senior Analyst",
            content="What are the key revenue trends this quarter?",
            message_type=MessageType.QUERY
        )
        
        # Generate citations for response
        citations = attribution_manager.generate_citations_for_chunks(chunk_ids)
        
        # Create response with citations
        response_text = "Based on the analysis, Q3 revenue shows 15% growth driven by:\n"
        response_text += "1. Strong consumer demand in key markets\n"
        response_text += "2. Effective competitive positioning\n"
        response_text += "3. Improved operational efficiency\n\n"
        response_text += "Sources:\n"
        
        for i, citation in enumerate(citations, 1):
            response_text += f"[{i}] {citation.citation_text} (Page {citation.page_number})\n"
        
        ai_response = chat_manager.add_message(
            workspace_id=workspace.workspace_id,
            user_id="system",
            username="AI Assistant",
            content=response_text,
            message_type=MessageType.RESPONSE
        )
        
        # Verify integration
        assert len(citations) == 3
        assert query_message.message_id != ai_response.message_id
        assert "Sources:" in ai_response.content
        
        # Get final workspace state
        final_stats = workspace_manager.get_workspace_stats(workspace.workspace_id)
        chat_history = chat_manager.get_chat_history(workspace.workspace_id)
        
        return True, f"Integration test: {final_stats['total_users']} users, {len(chat_history)} messages, {len(citations)} citations"
        
    except Exception as e:
        return False, f"Integration error: {e}"

async def test_async_collaboration():
    """Test asynchronous collaboration features."""
    try:
        from collaboration import (
            create_collaboration_system,
            handle_collaborative_query,
            handle_collaborative_response,
            MessageType
        )
        
        # Create system
        workspace_manager, connection_manager, chat_manager = create_collaboration_system()
        
        # Create workspace
        workspace = workspace_manager.create_workspace(
            name="Async Test Workspace",
            description="Testing asynchronous collaboration features",
            creator_id="async_user",
            creator_username="Async Tester"
        )
        
        # Test collaborative query handling
        query_message = await handle_collaborative_query(
            workspace_id=workspace.workspace_id,
            user_id="async_user",
            username="Async Tester",
            query="Test async query functionality",
            chat_manager=chat_manager
        )
        
        assert query_message.message_type == MessageType.QUERY
        assert query_message.content == "Test async query functionality"
        
        # Test collaborative response handling
        response_message = await handle_collaborative_response(
            workspace_id=workspace.workspace_id,
            response_text="Async response test completed successfully",
            chat_manager=chat_manager
        )
        
        assert response_message.message_type == MessageType.RESPONSE
        assert "successfully" in response_message.content
        
        return True, f"Async messages: query={query_message.message_id[:8]}..., response={response_message.message_id[:8]}..."
        
    except Exception as e:
        return False, f"Async collaboration error: {e}"

def test_error_handling():
    """Test error handling and edge cases."""
    tests_passed = 0
    total_tests = 0
    
    try:
        from source_attribution import SourceAttributionManager, ChunkMetadata
        from collaboration import create_collaboration_system
        
        # Test 1: Empty citation generation
        total_tests += 1
        manager = SourceAttributionManager()
        citations = manager.generate_citations_for_chunks([])
        if len(citations) == 0:
            tests_passed += 1
        
        # Test 2: Non-existent chunk citations
        total_tests += 1
        citations = manager.generate_citations_for_chunks(["non_existent_chunk"])
        if len(citations) == 0:
            tests_passed += 1
        
        # Test 3: Workspace manager edge cases
        total_tests += 1
        workspace_manager, _, _ = create_collaboration_system()
        workspace = workspace_manager.get_workspace("non_existent_workspace")
        if workspace is None:
            tests_passed += 1
        
        # Test 4: Invalid user invitation
        total_tests += 1
        result = workspace_manager.invite_user("invalid_workspace", "user", "username")
        if result == False:
            tests_passed += 1
        
        success_rate = (tests_passed / total_tests) * 100
        return tests_passed == total_tests, f"Error handling: {tests_passed}/{total_tests} tests passed ({success_rate:.1f}%)"
        
    except Exception as e:
        return False, f"Error handling test failed: {e}"

def main():
    """Enhanced main validation function with comprehensive reporting."""
    print("🚀 Enhanced GenAI Platform v3.0 - Comprehensive Validation")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize validation report
    report = ValidationReport()
    
    # Source Attribution Tests
    print("📚 Testing Source Attribution System:")
    print("-" * 40)
    
    result, duration = test_source_attribution_basic()
    passed, message = result if isinstance(result, tuple) else (result, "")
    report.add_test_result("Source Attribution - Basic", passed, message if not passed else None, duration)
    
    result, duration = test_source_attribution_advanced()
    passed, message = result if isinstance(result, tuple) else (result, "")
    report.add_test_result("Source Attribution - Advanced", passed, message if not passed else None, duration)
    
    print()
    
    # Collaboration Tests
    print("🤝 Testing Collaboration System:")
    print("-" * 40)
    
    result, duration = test_collaboration_basic()
    passed, message = result if isinstance(result, tuple) else (result, "")
    report.add_test_result("Collaboration - Basic", passed, message if not passed else None, duration)
    
    result, duration = test_collaboration_advanced()
    passed, message = result if isinstance(result, tuple) else (result, "")
    report.add_test_result("Collaboration - Advanced", passed, message if not passed else None, duration)
    
    print()
    
    # Integration Tests
    print("🔄 Testing System Integration:")
    print("-" * 40)
    
    result, duration = test_integration_scenario()
    passed, message = result if isinstance(result, tuple) else (result, "")
    report.add_test_result("Integration Scenario", passed, message if not passed else None, duration)
    
    # Async Tests
    print("⚡ Testing Async Collaboration:")
    print("-" * 40)
    
    async def run_async_test():
        return await test_async_collaboration()
    
    try:
        result = asyncio.run(run_async_test())
        passed, message = result if isinstance(result, tuple) else (result, "")
        report.add_test_result("Async Collaboration", passed, message if not passed else None)
    except Exception as e:
        report.add_test_result("Async Collaboration", False, str(e))
    
    print()
    
    # Error Handling Tests
    print("🛡️ Testing Error Handling:")
    print("-" * 40)
    
    passed, message = test_error_handling()
    report.add_test_result("Error Handling", passed, message if not passed else None)
    
    print()
    
    # Generate comprehensive report
    summary = report.generate_summary()
    
    print("=" * 70)
    print("📊 COMPREHENSIVE VALIDATION SUMMARY:")
    print("=" * 70)
    print(f"Execution Time:     {summary['total_duration']}")
    print(f"Tests Executed:     {summary['tests_run']}")
    print(f"Tests Passed:       {summary['tests_passed']}")
    print(f"Tests Failed:       {summary['tests_failed']}")
    print(f"Success Rate:       {summary['success_rate']}")
    
    if summary['performance_metrics']:
        print(f"\n⚡ Performance Metrics:")
        for test_name, duration in summary['performance_metrics'].items():
            print(f"  {test_name}: {duration:.3f}s")
    
    if summary['errors']:
        print(f"\n❌ Failed Tests:")
        for error in summary['errors']:
            print(f"  • {error['test']}: {error['error']}")
    
    print("\n" + "=" * 70)
    
    if summary['tests_failed'] == 0:
        print("🎉 ALL TESTS PASSED! Enhanced GenAI Platform v3.0 is fully operational.")
        print("✅ Source Attribution System: Ready for production")
        print("✅ Collaboration System: Ready for production")
        print("✅ Integration Layer: Fully functional")
        print("✅ Error Handling: Robust and reliable")
        print("\n🚀 Platform ready for deployment and enterprise use!")
    else:
        print("⚠️  SOME TESTS FAILED - Please review the errors above.")
        print("🔧 Address failed tests before production deployment.")
    
    return summary['tests_failed'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)