"""
Enhanced GenAI Platform Demo
Demonstrates document source attribution and real-time collaborative features
"""

import asyncio
from source_attribution import SourceAttributionManager, ChunkMetadata, CitationStyle
from collaboration import (
    create_collaboration_system, 
    UserRole, 
    MessageType,
    handle_collaborative_query,
    handle_collaborative_response
)

def demo_source_attribution():
    """Demonstrate source attribution features."""
    print("🔍 Source Attribution Demo")
    print("-" * 40)
    
    # Initialize source attribution manager
    attribution_manager = SourceAttributionManager()
    
    # Add some sample document chunks with metadata
    chunk1_metadata = ChunkMetadata(
        source_file="financial_report_2023.pdf",
        page_number=5,
        section="Revenue Analysis"
    )
    
    chunk2_metadata = ChunkMetadata(
        source_file="market_research.pdf", 
        page_number=12,
        section="Consumer Trends"
    )
    
    # Register chunks
    attribution_manager.add_chunk("chunk_001", chunk1_metadata)
    attribution_manager.add_chunk("chunk_002", chunk2_metadata)
    
    print("✅ Added 2 document chunks with metadata")
    
    # Generate citations for chunks used in a response
    chunks_used = ["chunk_001", "chunk_002"]
    citations = attribution_manager.generate_citations_for_chunks(chunks_used)
    
    print(f"📋 Generated {len(citations)} citations:")
    for i, citation in enumerate(citations, 1):
        print(f"  [{i}] {citation.citation_text} (Page {citation.page_number})")
    
    print()

def demo_collaboration():
    """Demonstrate collaboration features."""
    print("🤝 Collaboration Demo")
    print("-" * 40)
    
    # Create collaboration system
    workspace_manager, connection_manager, chat_manager = create_collaboration_system()
    
    # Create a workspace
    workspace = workspace_manager.create_workspace(
        name="Financial Analysis Team",
        description="Collaborative workspace for Q4 financial document analysis",
        creator_id="alice_123",
        creator_username="Alice Chen"
    )
    
    print(f"✅ Created workspace: '{workspace.name}'")
    print(f"   Workspace ID: {workspace.workspace_id}")
    
    # Invite another user
    workspace_manager.invite_user(
        workspace_id=workspace.workspace_id,
        user_id="bob_456", 
        username="Bob Smith",
        role=UserRole.COLLABORATOR
    )
    
    print("✅ Invited Bob Smith as collaborator")
    
    # Add some chat messages
    message1 = chat_manager.add_message(
        workspace_id=workspace.workspace_id,
        user_id="alice_123",
        username="Alice Chen",
        content="Hi team! I've uploaded the Q4 financial reports. Let's analyze the revenue trends.",
        message_type=MessageType.TEXT
    )
    
    message2 = chat_manager.add_message(
        workspace_id=workspace.workspace_id,
        user_id="bob_456", 
        username="Bob Smith",
        content="Great! I'll start with the market research data from pages 10-15.",
        message_type=MessageType.TEXT
    )
    
    # Simulate AI query and response
    query_message = chat_manager.add_message(
        workspace_id=workspace.workspace_id,
        user_id="alice_123",
        username="Alice Chen", 
        content="What were the key revenue drivers in Q4?",
        message_type=MessageType.QUERY
    )
    
    # Simulate AI response with source attribution
    ai_response = """Based on the financial reports, the key Q4 revenue drivers were:

1. **Product Sales Growth**: 23% increase in core product revenue
2. **Service Expansion**: New consulting services contributed $2.3M
3. **Market Penetration**: Entry into 3 new geographic markets

Sources:
[1] Source: financial_report_2023.pdf (Page 5)
[2] Source: market_research.pdf (Page 12)"""
    
    response_message = chat_manager.add_message(
        workspace_id=workspace.workspace_id,
        user_id="system",
        username="AI Assistant",
        content=ai_response,
        message_type=MessageType.RESPONSE
    )
    
    print(f"💬 Added {len(chat_manager.get_chat_history(workspace.workspace_id))} messages to workspace chat")
    
    # Show recent chat history
    recent_messages = chat_manager.get_chat_history(workspace.workspace_id, limit=3)
    print("\n📝 Recent Chat Messages:")
    for msg in recent_messages[-3:]:
        print(f"   {msg.username}: {msg.content[:60]}...")
    
    # Show workspace stats
    stats = workspace_manager.get_workspace_stats(workspace.workspace_id)
    print(f"\n📊 Workspace Stats:")
    print(f"   Total Users: {stats['total_users']}")
    print(f"   Total Messages: {stats['total_messages']}")
    
    print()

async def demo_realtime_collaboration():
    """Demonstrate real-time collaboration workflow."""
    print("⚡ Real-time Collaboration Demo")
    print("-" * 40)
    
    # Create collaboration system
    workspace_manager, connection_manager, chat_manager = create_collaboration_system()
    
    # Create workspace
    workspace = workspace_manager.create_workspace(
        name="Document Analysis Session",
        description="Real-time collaborative document analysis",
        creator_id="user1",
        creator_username="Analyst1"
    )
    
    print(f"✅ Created real-time workspace: {workspace.workspace_id}")
    
    # Simulate collaborative query
    query_msg = await handle_collaborative_query(
        workspace_id=workspace.workspace_id,
        user_id="user1",
        username="Analyst1", 
        query="Analyze the revenue trends from the uploaded documents",
        chat_manager=chat_manager
    )
    
    print(f"📤 Collaborative query broadcasted: {query_msg.message_id}")
    
    # Simulate AI response
    response_msg = await handle_collaborative_response(
        workspace_id=workspace.workspace_id,
        response_text="Revenue analysis complete. Key insights: 15% growth in Q4, driven by new product launches.",
        chat_manager=chat_manager
    )
    
    print(f"📥 AI response broadcasted: {response_msg.message_id}")
    print("✅ Real-time collaboration workflow completed")

def main():
    """Main demo function."""
    print("🚀 Enhanced GenAI Platform Demo")
    print("=" * 50)
    print()
    
    # Demo source attribution
    demo_source_attribution()
    
    # Demo collaboration features  
    demo_collaboration()
    
    # Demo real-time collaboration
    print("Running async real-time demo...")
    asyncio.run(demo_realtime_collaboration())
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("Enhanced GenAI platform with source attribution and")
    print("real-time collaboration features is fully operational.")

if __name__ == "__main__":
    main()