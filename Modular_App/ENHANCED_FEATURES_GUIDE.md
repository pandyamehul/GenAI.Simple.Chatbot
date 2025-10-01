# Enhanced GenAI Platform v3.0 - Features Documentation

## 📚 Source Attribution System

### Overview
The Source Attribution System provides comprehensive tracking and citation generation for all document sources used in AI responses, ensuring full transparency and compliance with academic and enterprise standards.

### Core Components

#### ChunkMetadata Class
```python
@dataclass
class ChunkMetadata:
    source_file: str                    # Required: Source document filename
    page_number: Optional[int] = None   # Page reference for citations
    section: Optional[str] = None       # Document section identifier
    chunk_id: str                      # Auto-generated UUID
    created_at: datetime               # Timestamp for audit trails
```

#### Citation Class
```python
@dataclass  
class Citation:
    citation_id: str           # Unique citation identifier
    source_file: str          # Source document reference
    citation_text: str        # Formatted citation text
    style: CitationStyle      # APA, MLA, Chicago, IEEE
    page_number: Optional[int] # Page reference
```

#### SourceAttributionManager
The main class for managing source attribution:
- `add_chunk()`: Register document chunks with metadata
- `generate_citations_for_chunks()`: Create formatted citations
- `track_response_sources()`: Link AI responses to source chunks
- `get_response_citations()`: Retrieve citations for responses

### Usage Examples

#### Basic Attribution
```python
from source_attribution import SourceAttributionManager, ChunkMetadata

manager = SourceAttributionManager()

# Add document chunk
metadata = ChunkMetadata(
    source_file="quarterly_report_2023.pdf",
    page_number=12,
    section="Financial Overview"
)
manager.add_chunk("chunk_001", metadata)

# Generate citations
citations = manager.generate_citations_for_chunks(["chunk_001"])
print(citations[0].citation_text)  # "Source: quarterly_report_2023.pdf"
```

#### Advanced Response Attribution
```python
# Track which chunks were used for a response
response_id = "resp_123"
chunks_used = ["chunk_001", "chunk_002", "chunk_003"]
manager.track_response_sources(response_id, chunks_used)

# Get formatted citations for the response
citations = manager.get_response_citations(response_id, CitationStyle.APA)
for citation in citations:
    print(citation.format_citation())
```

## 🤝 Real-time Collaboration System

### Overview
The Collaboration System enables multi-user workspaces with real-time messaging, role-based access control, and WebSocket-powered live updates.

### Core Components

#### User Management
```python
class UserRole(Enum):
    OWNER = "owner"           # Full workspace control
    ADMIN = "admin"           # Administrative permissions
    COLLABORATOR = "collaborator"  # Read/write access
    VIEWER = "viewer"         # Read-only access

class WorkspacePermission(Enum):
    READ = "read"             # View content
    WRITE = "write"           # Create/edit content
    DELETE = "delete"         # Remove content
    SHARE = "share"           # Invite users
    ADMIN = "admin"           # Administrative control
```

#### Workspace Management
```python
@dataclass
class Workspace:
    workspace_id: str         # Unique workspace identifier
    name: str                 # Workspace display name
    description: str          # Workspace description
    created_by: str          # Creator user ID
    users: Dict[str, WorkspaceUser]  # Workspace members
    chat_history: List[CollaborativeMessage]  # Message history
    is_active: bool = True    # Workspace status
```

#### Real-time Messaging
```python
@dataclass
class CollaborativeMessage:
    message_id: str           # Unique message identifier
    workspace_id: str         # Target workspace
    user_id: str             # Message author
    content: str             # Message content
    message_type: MessageType # TEXT, QUERY, RESPONSE, etc.
    timestamp: datetime       # Message creation time
    reactions: Dict[str, List[str]]  # Emoji reactions
```

### Usage Examples

#### Workspace Creation
```python
from collaboration import create_collaboration_system, UserRole

# Initialize collaboration system
workspace_manager, connection_manager, chat_manager = create_collaboration_system()

# Create workspace
workspace = workspace_manager.create_workspace(
    name="Data Analysis Team",
    description="Collaborative workspace for quarterly data analysis",
    creator_id="alice_123",
    creator_username="Alice Johnson"
)

print(f"Created workspace: {workspace.workspace_id}")
```

#### User Invitation and Permissions
```python
# Invite team members with different roles
workspace_manager.invite_user(
    workspace_id=workspace.workspace_id,
    user_id="bob_456",
    username="Bob Smith", 
    role=UserRole.COLLABORATOR  # Can read and write
)

workspace_manager.invite_user(
    workspace_id=workspace.workspace_id,
    user_id="carol_789",
    username="Carol Davis",
    role=UserRole.VIEWER  # Read-only access
)
```

#### Real-time Messaging
```python
# Add message to workspace
message = chat_manager.add_message(
    workspace_id=workspace.workspace_id,
    user_id="alice_123",
    username="Alice Johnson",
    content="Let's review the Q3 financial data together",
    message_type=MessageType.TEXT
)

# Broadcast to all workspace users (async)
await chat_manager.broadcast_message(message)

# Get chat history
recent_messages = chat_manager.get_chat_history(workspace.workspace_id, limit=10)
```

#### WebSocket Integration
```python
# Connect user to real-time updates
connection_manager.connect(
    user_id="alice_123",
    workspace_id=workspace.workspace_id,
    websocket=websocket_connection
)

# Broadcast message to all connected users
await connection_manager.broadcast_to_workspace(
    workspace_id=workspace.workspace_id,
    message={
        "type": "new_message",
        "data": {"content": "Hello team!", "user": "Alice"}
    }
)
```

## 🔄 Integration Patterns

### Combining Source Attribution with Collaboration

```python
async def process_collaborative_query(workspace_id: str, user_id: str, 
                                    username: str, query: str):
    """Process a query in collaborative workspace with source attribution."""
    
    # Add query message to workspace
    query_message = chat_manager.add_message(
        workspace_id=workspace_id,
        user_id=user_id,
        username=username,
        content=query,
        message_type=MessageType.QUERY
    )
    
    # Broadcast query to all users
    await chat_manager.broadcast_message(query_message)
    
    # Process query and get AI response with sources
    response_text, source_chunks = await process_ai_query(query)
    
    # Track source attribution
    response_id = str(uuid.uuid4())
    attribution_manager.track_response_sources(response_id, source_chunks)
    
    # Generate citations
    citations = attribution_manager.get_response_citations(response_id)
    
    # Format response with citations
    formatted_response = f"{response_text}\n\nSources:\n"
    for i, citation in enumerate(citations, 1):
        formatted_response += f"[{i}] {citation.citation_text}\n"
    
    # Add AI response to workspace
    response_message = chat_manager.add_message(
        workspace_id=workspace_id,
        user_id="system",
        username="AI Assistant",
        content=formatted_response,
        message_type=MessageType.RESPONSE
    )
    
    # Broadcast response to all users
    await chat_manager.broadcast_message(response_message)
    
    return response_message
```

### Database Persistence Integration

```python
# Example integration with SQLAlchemy
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class WorkspaceModel(Base):
    __tablename__ = 'workspaces'
    
    workspace_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

class MessageModel(Base):
    __tablename__ = 'messages'
    
    message_id = Column(String, primary_key=True)
    workspace_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)

def save_workspace_to_db(workspace: Workspace, session):
    """Save workspace to database."""
    db_workspace = WorkspaceModel(
        workspace_id=workspace.workspace_id,
        name=workspace.name,
        description=workspace.description,
        created_by=workspace.created_by,
        created_at=workspace.created_at
    )
    session.add(db_workspace)
    session.commit()

def save_message_to_db(message: CollaborativeMessage, session):
    """Save message to database."""
    db_message = MessageModel(
        message_id=message.message_id,
        workspace_id=message.workspace_id,
        user_id=message.user_id,
        content=message.content,
        created_at=message.timestamp
    )
    session.add(db_message)
    session.commit()
```

## 📊 Performance Optimization

### Memory Management
- **Lazy Loading**: Load workspace data only when needed
- **Message Chunking**: Paginate large chat histories
- **Connection Cleanup**: Automatic WebSocket disconnection handling
- **Garbage Collection**: Periodic cleanup of expired sessions

### Scalability Patterns
- **Horizontal Scaling**: Multiple worker processes for WebSocket handling
- **Caching Layer**: Redis for session and workspace data
- **Database Sharding**: Separate databases for different workspace clusters
- **Load Balancing**: Distribute WebSocket connections across servers

### Monitoring and Metrics
```python
# Example metrics collection
import time
from functools import wraps

def track_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log performance metrics
        logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
        return result
    return wrapper

@track_performance
def generate_citations_for_chunks(self, chunk_ids: List[str]) -> List[Citation]:
    # Citation generation with performance tracking
    pass
```

## 🔒 Security Considerations

### Data Protection
- **Input Sanitization**: Clean all user inputs before processing
- **SQL Injection Prevention**: Use parameterized queries
- **XSS Protection**: Escape HTML content in messages
- **Rate Limiting**: Prevent spam and abuse

### Access Control
```python
def check_workspace_permission(user_id: str, workspace_id: str, 
                             required_permission: WorkspacePermission) -> bool:
    """Check if user has required permission for workspace action."""
    workspace = workspace_manager.get_workspace(workspace_id)
    if not workspace or user_id not in workspace.users:
        return False
    
    user = workspace.users[user_id]
    return user.has_permission(required_permission)

# Usage in API endpoints
if not check_workspace_permission(user_id, workspace_id, WorkspacePermission.WRITE):
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```

### Audit Logging
```python
import logging

audit_logger = logging.getLogger('audit')

def log_user_action(user_id: str, action: str, workspace_id: str, details: Dict):
    """Log user actions for audit trails."""
    audit_logger.info(f"User {user_id} performed {action} in workspace {workspace_id}", 
                     extra={
                         'user_id': user_id,
                         'action': action,
                         'workspace_id': workspace_id,
                         'timestamp': datetime.utcnow().isoformat(),
                         'details': details
                     })

# Usage
log_user_action(
    user_id="alice_123",
    action="CREATE_MESSAGE", 
    workspace_id="ws_456",
    details={"message_type": "TEXT", "content_length": 45}
)
```

## 🧪 Testing Strategies

### Unit Testing
```python
import unittest
from source_attribution import SourceAttributionManager, ChunkMetadata

class TestSourceAttribution(unittest.TestCase):
    
    def setUp(self):
        self.manager = SourceAttributionManager()
        self.test_metadata = ChunkMetadata(
            source_file="test.pdf",
            page_number=1,
            section="Introduction"
        )
    
    def test_add_chunk(self):
        """Test adding chunk metadata."""
        self.manager.add_chunk("test_chunk", self.test_metadata)
        self.assertIn("test_chunk", self.manager.chunk_metadata)
        
    def test_citation_generation(self):
        """Test citation generation."""
        self.manager.add_chunk("test_chunk", self.test_metadata)
        citations = self.manager.generate_citations_for_chunks(["test_chunk"])
        
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0].source_file, "test.pdf")
        self.assertEqual(citations[0].page_number, 1)
```

### Integration Testing
```python
import asyncio
import pytest
from collaboration import create_collaboration_system

@pytest.mark.asyncio
async def test_collaborative_workflow():
    """Test complete collaborative workflow."""
    # Setup
    workspace_manager, connection_manager, chat_manager = create_collaboration_system()
    
    # Create workspace
    workspace = workspace_manager.create_workspace(
        name="Test Workspace",
        description="Integration test workspace",
        creator_id="test_user",
        creator_username="Test User"
    )
    
    # Add message
    message = chat_manager.add_message(
        workspace_id=workspace.workspace_id,
        user_id="test_user",
        username="Test User",
        content="Test message",
        message_type=MessageType.TEXT
    )
    
    # Verify message was added
    history = chat_manager.get_chat_history(workspace.workspace_id)
    assert len(history) == 1
    assert history[0].content == "Test message"
```

---

*This documentation covers the core enhanced features of the GenAI Platform v3.0. For additional implementation details, see the source code and inline documentation.*