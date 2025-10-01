# 🚀 Implementation Guide: API Endpoints for Collaborative Features

This guide provides step-by-step implementation of REST API endpoints and WebSocket handlers for collaborative features.

---

## 📍 Source Attribution API Endpoints

### Document Upload with Attribution Tracking

```python
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List, Optional
import uuid
from datetime import datetime

@app.post("/api/documents/upload-with-attribution")
async def upload_document_with_attribution(
    file: UploadFile = File(...),
    workspace_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Upload document with complete source attribution tracking."""
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.docx', '.txt', '.xlsx', '.pptx')):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        file_content = await file.read()
        
        # Process with enhanced attribution
        attribution_manager = SourceAttributionManager()
        processed_doc = await attribution_manager.process_document_with_attribution(
            file_content=file_content,
            filename=file.filename,
            uploaded_by=current_user.id,
            workspace_id=workspace_id
        )
        
        return {
            "document_id": processed_doc.document_id,
            "filename": file.filename,
            "chunks_processed": len(processed_doc.chunks),
            "metadata_extracted": processed_doc.metadata_count,
            "attribution_enabled": True,
            "upload_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/documents/{document_id}/sources")
async def get_document_sources(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all source chunks for a document."""
    attribution_manager = SourceAttributionManager()
    sources = await attribution_manager.get_document_sources(document_id)
    
    return {
        "document_id": document_id,
        "total_chunks": len(sources),
        "sources": [
            {
                "chunk_id": source.chunk_id,
                "page_number": source.page_number,
                "section_title": source.section_title,
                "confidence_score": source.confidence_score,
                "text_preview": source.text_content[:100] + "..." if len(source.text_content) > 100 else source.text_content
            }
            for source in sources
        ]
    }
```

### Query with Source Attribution

```python
@app.post("/api/chat/query-with-sources")
async def query_with_source_attribution(
    query_data: QueryWithAttributionRequest,
    current_user: User = Depends(get_current_user)
):
    """Process query and return response with complete source attribution."""
    
    # Enhanced chat engine with attribution
    attributed_chat_engine = AttributedChatEngine()
    
    # Generate response with sources
    attributed_response = await attributed_chat_engine.generate_response_with_sources(
        query=query_data.query,
        workspace_id=query_data.workspace_id,
        citation_style=query_data.citation_style or CitationStyle.APA,
        max_sources=query_data.max_sources or 5
    )
    
    return {
        "response_id": attributed_response.response_id,
        "response_text": attributed_response.response_text,
        "confidence_score": attributed_response.overall_confidence,
        "sources": [
            {
                "source_id": source.chunk_id,
                "document_name": source.document_name,
                "page_number": source.page_number,
                "section_title": source.section_title,
                "confidence": source.confidence_score,
                "text_snippet": source.text_content[:200] + "..." if len(source.text_content) > 200 else source.text_content
            }
            for source in attributed_response.sources
        ],
        "citations": [
            {
                "citation_id": citation.citation_id,
                "formatted_citation": citation.source_reference,
                "clickable_link": citation.clickable_link,
                "page_reference": citation.page_reference
            }
            for citation in attributed_response.citations
        ],
        "metadata": {
            "generated_at": attributed_response.generated_at.isoformat(),
            "ai_provider": attributed_response.ai_provider,
            "model_used": attributed_response.model_used,
            "processing_time": attributed_response.processing_time
        }
    }

@app.get("/api/documents/view/{document_id}")
async def view_document_with_highlight(
    document_id: str,
    page: Optional[int] = None,
    chunk_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """View document with highlighted source chunks."""
    
    attribution_manager = SourceAttributionManager()
    document_viewer = DocumentViewer()
    
    # Get document metadata
    doc_metadata = await attribution_manager.get_document_metadata(document_id)
    
    if not doc_metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Generate document view with highlighting
    if chunk_id:
        highlighted_content = await document_viewer.render_with_highlight(
            document_id=document_id,
            chunk_id=chunk_id,
            page=page
        )
    else:
        highlighted_content = await document_viewer.render_document(
            document_id=document_id,
            page=page
        )
    
    return HTMLResponse(highlighted_content)
```

---

## 🤝 Collaborative Features API Endpoints

### Workspace Management

```python
@app.post("/api/workspaces")
async def create_workspace(
    workspace_data: WorkspaceCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new collaborative workspace."""
    
    workspace_manager = WorkspaceManager()
    
    workspace = await workspace_manager.create_workspace(
        owner_id=current_user.id,
        name=workspace_data.name,
        description=workspace_data.description,
        settings=workspace_data.settings or WorkspaceSettings()
    )
    
    return {
        "workspace_id": workspace.id,
        "name": workspace.name,
        "description": workspace.description,
        "owner_id": workspace.owner_id,
        "created_at": workspace.created_at.isoformat(),
        "member_count": len(workspace.members),
        "invite_code": await workspace_manager.generate_invite_code(workspace.id)
    }

@app.get("/api/workspaces")
async def list_user_workspaces(
    current_user: User = Depends(get_current_user)
):
    """List all workspaces user has access to."""
    
    workspace_manager = WorkspaceManager()
    workspaces = await workspace_manager.get_user_workspaces(current_user.id)
    
    return {
        "workspaces": [
            {
                "id": ws.id,
                "name": ws.name,
                "description": ws.description,
                "role": next(m.role.value for m in ws.members if m.user_id == current_user.id),
                "member_count": len(ws.members),
                "document_count": len(ws.documents),
                "last_activity": ws.updated_at.isoformat()
            }
            for ws in workspaces
        ]
    }

@app.post("/api/workspaces/{workspace_id}/join")
async def join_workspace(
    workspace_id: str,
    join_data: WorkspaceJoinRequest,
    current_user: User = Depends(get_current_user)
):
    """Join workspace using invite code."""
    
    workspace_manager = WorkspaceManager()
    
    # Verify invite code
    if not await workspace_manager.verify_invite_code(workspace_id, join_data.invite_code):
        raise HTTPException(status_code=400, detail="Invalid invite code")
    
    success = await workspace_manager.join_workspace(
        user_id=current_user.id,
        workspace_id=workspace_id,
        role=WorkspaceRole.MEMBER
    )
    
    if success:
        return {"message": "Successfully joined workspace", "workspace_id": workspace_id}
    else:
        raise HTTPException(status_code=400, detail="Failed to join workspace")

@app.get("/api/workspaces/{workspace_id}/members")
async def get_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all members of a workspace."""
    
    # Verify user access
    if not await verify_workspace_access(current_user.id, workspace_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    workspace_manager = WorkspaceManager()
    members = await workspace_manager.get_workspace_members(workspace_id)
    
    return {
        "workspace_id": workspace_id,
        "members": [
            {
                "user_id": member.user_id,
                "username": member.username,
                "email": member.email,
                "role": member.role.value,
                "joined_at": member.joined_at.isoformat(),
                "last_active": member.last_active.isoformat()
            }
            for member in members
        ]
    }
```

### Real-time Chat API

```python
@app.get("/api/workspaces/{workspace_id}/chat/history")
async def get_chat_history(
    workspace_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get chat history for workspace."""
    
    if not await verify_workspace_access(current_user.id, workspace_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    chat_manager = CollaborativeChatManager()
    messages = await chat_manager.get_chat_history(
        workspace_id=workspace_id,
        limit=limit,
        before_timestamp=before
    )
    
    return {
        "workspace_id": workspace_id,
        "messages": [
            {
                "id": msg.id,
                "user_id": msg.user_id,
                "username": msg.username,
                "content": msg.content,
                "message_type": msg.message_type,
                "timestamp": msg.timestamp.isoformat(),
                "reply_to": msg.reply_to,
                "reactions": msg.reactions
            }
            for msg in messages
        ]
    }

@app.post("/api/workspaces/{workspace_id}/chat/message")
async def send_chat_message(
    workspace_id: str,
    message_data: ChatMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Send chat message to workspace."""
    
    if not await verify_workspace_access(current_user.id, workspace_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    chat_manager = CollaborativeChatManager()
    
    message = await chat_manager.send_chat_message(
        workspace_id=workspace_id,
        user_id=current_user.id,
        content=message_data.content,
        message_type=message_data.message_type or 'text',
        reply_to=message_data.reply_to
    )
    
    return {
        "message_id": message.id,
        "timestamp": message.timestamp.isoformat(),
        "status": "sent"
    }

@app.post("/api/workspaces/{workspace_id}/chat/reaction")
async def add_message_reaction(
    workspace_id: str,
    reaction_data: MessageReactionRequest,
    current_user: User = Depends(get_current_user)
):
    """Add reaction to chat message."""
    
    if not await verify_workspace_access(current_user.id, workspace_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    chat_manager = CollaborativeChatManager()
    
    success = await chat_manager.add_message_reaction(
        message_id=reaction_data.message_id,
        user_id=current_user.id,
        reaction=reaction_data.reaction
    )
    
    if success:
        return {"status": "reaction_added"}
    else:
        raise HTTPException(status_code=400, detail="Failed to add reaction")
```

### Document Collaboration API

```python
@app.post("/api/workspaces/{workspace_id}/documents/upload")
async def upload_document_to_workspace(
    workspace_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload document to collaborative workspace."""
    
    if not await verify_workspace_access(current_user.id, workspace_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check upload permissions
    permissions = await get_user_workspace_permissions(current_user.id, workspace_id)
    if 'upload_documents' not in permissions:
        raise HTTPException(status_code=403, detail="Upload permission denied")
    
    file_content = await file.read()
    
    collaborative_doc_manager = CollaborativeDocumentManager()
    
    doc_id = await collaborative_doc_manager.upload_document_to_workspace(
        workspace_id=workspace_id,
        user_id=current_user.id,
        file_data=file_content,
        filename=file.filename
    )
    
    return {
        "document_id": doc_id,
        "filename": file.filename,
        "workspace_id": workspace_id,
        "uploaded_by": current_user.id,
        "uploaded_at": datetime.utcnow().isoformat()
    }

@app.get("/api/workspaces/{workspace_id}/documents")
async def get_workspace_documents(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all documents in workspace."""
    
    if not await verify_workspace_access(current_user.id, workspace_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    collaborative_doc_manager = CollaborativeDocumentManager()
    documents = await collaborative_doc_manager.get_workspace_documents(workspace_id)
    
    return {
        "workspace_id": workspace_id,
        "documents": documents
    }

@app.delete("/api/workspaces/{workspace_id}/documents/{document_id}")
async def delete_workspace_document(
    workspace_id: str,
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete document from workspace."""
    
    if not await verify_workspace_access(current_user.id, workspace_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check delete permissions
    permissions = await get_user_workspace_permissions(current_user.id, workspace_id)
    if 'delete_documents' not in permissions:
        raise HTTPException(status_code=403, detail="Delete permission denied")
    
    collaborative_doc_manager = CollaborativeDocumentManager()
    
    success = await collaborative_doc_manager.delete_workspace_document(
        workspace_id=workspace_id,
        document_id=document_id,
        deleted_by=current_user.id
    )
    
    if success:
        return {"status": "document_deleted", "document_id": document_id}
    else:
        raise HTTPException(status_code=400, detail="Failed to delete document")
```

---

## 🔌 WebSocket Implementation

### Main WebSocket Handler

```python
from fastapi import WebSocket, WebSocketDisconnect
import json
from typing import Dict, List

class WebSocketConnectionManager:
    """Manages WebSocket connections for real-time collaboration."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, workspace_id: str, user_id: str):
        """Connect user to workspace WebSocket."""
        await websocket.accept()
        
        # Add to workspace connections
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)
        
        # Track user connection
        self.user_connections[user_id] = websocket
        
        # Notify others of user joining
        await self.broadcast_to_workspace(workspace_id, {
            "type": "user_joined",
            "data": {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }, exclude_user=user_id)
    
    def disconnect(self, websocket: WebSocket, workspace_id: str, user_id: str):
        """Disconnect user from workspace."""
        # Remove from workspace connections
        if workspace_id in self.active_connections:
            if websocket in self.active_connections[workspace_id]:
                self.active_connections[workspace_id].remove(websocket)
        
        # Remove user connection
        if user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def broadcast_to_workspace(self, workspace_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in workspace."""
        if workspace_id in self.active_connections:
            for connection in self.active_connections[workspace_id]:
                try:
                    # Skip excluded user if specified
                    if exclude_user and connection == self.user_connections.get(exclude_user):
                        continue
                    
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove failed connections
                    self.active_connections[workspace_id].remove(connection)

# Global connection manager
connection_manager = WebSocketConnectionManager()

@app.websocket("/ws/collaborate/{workspace_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    workspace_id: str,
    user_id: str
):
    """Main WebSocket endpoint for collaboration."""
    
    # Verify user access to workspace
    if not await verify_workspace_access(user_id, workspace_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await connection_manager.connect(websocket, workspace_id, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            await handle_websocket_message(message, workspace_id, user_id)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, workspace_id, user_id)
        
        # Notify others of user leaving
        await connection_manager.broadcast_to_workspace(workspace_id, {
            "type": "user_left",
            "data": {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        })

async def handle_websocket_message(message: dict, workspace_id: str, user_id: str):
    """Handle incoming WebSocket messages."""
    
    message_type = message.get("type")
    data = message.get("data", {})
    
    if message_type == "chat_message":
        await handle_websocket_chat_message(workspace_id, user_id, data)
    
    elif message_type == "typing_indicator":
        await handle_typing_indicator(workspace_id, user_id, data)
    
    elif message_type == "document_query":
        await handle_document_query(workspace_id, user_id, data)
    
    elif message_type == "presence_update":
        await handle_presence_update(workspace_id, user_id, data)
    
    else:
        # Unknown message type
        pass

async def handle_websocket_chat_message(workspace_id: str, user_id: str, data: dict):
    """Handle chat message via WebSocket."""
    
    chat_manager = CollaborativeChatManager()
    
    message = await chat_manager.send_chat_message(
        workspace_id=workspace_id,
        user_id=user_id,
        content=data.get("content", ""),
        message_type=data.get("message_type", "text")
    )
    
    # Message is automatically broadcasted by chat_manager

async def handle_typing_indicator(workspace_id: str, user_id: str, data: dict):
    """Handle typing indicator."""
    
    is_typing = data.get("is_typing", False)
    
    # Broadcast typing indicator to others
    await connection_manager.broadcast_to_workspace(workspace_id, {
        "type": "typing_indicator",
        "data": {
            "user_id": user_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        }
    }, exclude_user=user_id)

async def handle_document_query(workspace_id: str, user_id: str, data: dict):
    """Handle collaborative document query."""
    
    query = data.get("query", "")
    
    # Process query with attribution
    attributed_chat_engine = AttributedChatEngine()
    response = await attributed_chat_engine.generate_response_with_sources(
        query=query,
        workspace_id=workspace_id
    )
    
    # Broadcast query and response to workspace
    await connection_manager.broadcast_to_workspace(workspace_id, {
        "type": "document_query_response",
        "data": {
            "query": query,
            "response": response.response_text,
            "sources": [
                {
                    "document_name": source.document_name,
                    "page_number": source.page_number,
                    "confidence": source.confidence_score
                }
                for source in response.sources
            ],
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    })
```

---

## 🔧 Request/Response Models

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

# Source Attribution Models
class QueryWithAttributionRequest(BaseModel):
    query: str
    workspace_id: Optional[str] = None
    citation_style: Optional[str] = "apa"
    max_sources: Optional[int] = 5
    include_confidence: bool = True

# Collaborative Feature Models
class WorkspaceCreateRequest(BaseModel):
    name: str
    description: str
    settings: Optional[Dict[str, Any]] = None

class WorkspaceJoinRequest(BaseModel):
    invite_code: str

class ChatMessageRequest(BaseModel):
    content: str
    message_type: Optional[str] = "text"
    reply_to: Optional[str] = None

class MessageReactionRequest(BaseModel):
    message_id: str
    reaction: str  # emoji or reaction type

class DocumentUploadRequest(BaseModel):
    workspace_id: str
    tags: Optional[List[str]] = None
    description: Optional[str] = None

# Response Models
class AttributedResponseModel(BaseModel):
    response_id: str
    response_text: str
    confidence_score: float
    sources: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class WorkspaceModel(BaseModel):
    id: str
    name: str
    description: str
    owner_id: str
    member_count: int
    document_count: int
    created_at: str
    last_activity: str

class ChatMessageModel(BaseModel):
    id: str
    user_id: str
    username: str
    content: str
    message_type: str
    timestamp: str
    reply_to: Optional[str] = None
    reactions: Dict[str, List[str]] = {}
```

---

## 🚀 Testing Implementation

```python
import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

class TestSourceAttribution:
    """Test source attribution features."""
    
    def test_upload_with_attribution(self, client: TestClient, auth_headers):
        """Test document upload with attribution tracking."""
        with open("test_document.pdf", "rb") as f:
            response = client.post(
                "/api/documents/upload-with-attribution",
                files={"file": ("test.pdf", f, "application/pdf")},
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["attribution_enabled"] is True
    
    def test_query_with_sources(self, client: TestClient, auth_headers):
        """Test query with source attribution."""
        query_data = {
            "query": "What is the main topic?",
            "citation_style": "apa",
            "max_sources": 3
        }
        
        response = client.post(
            "/api/chat/query-with-sources",
            json=query_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response_text" in data
        assert "sources" in data
        assert "citations" in data

class TestCollaboration:
    """Test collaborative features."""
    
    def test_create_workspace(self, client: TestClient, auth_headers):
        """Test workspace creation."""
        workspace_data = {
            "name": "Test Workspace",
            "description": "A test workspace"
        }
        
        response = client.post(
            "/api/workspaces",
            json=workspace_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Workspace"
        assert "workspace_id" in data
    
    def test_websocket_connection(self):
        """Test WebSocket connection for collaboration."""
        with client.websocket_connect("/ws/collaborate/test-workspace?user_id=test-user") as websocket:
            # Test connection established
            data = websocket.receive_json()
            assert data["type"] == "connection_established"
            
            # Test sending chat message
            websocket.send_json({
                "type": "chat_message",
                "data": {"content": "Hello, workspace!"}
            })
            
            # Verify message received
            response = websocket.receive_json()
            assert response["type"] == "chat_message"
            assert response["data"]["content"] == "Hello, workspace!"
```

---

**This comprehensive API implementation guide provides everything needed to build robust source attribution and collaborative features into the GenAI platform!**