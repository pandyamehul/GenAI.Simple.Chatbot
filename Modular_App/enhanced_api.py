"""
Enhanced REST API with Source Attribution and Collaborative Features
Extends the GenAI API to support workspaces, real-time collaboration, and source attribution.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import os
import tempfile
import json
import uuid
from datetime import datetime, timedelta
import logging
import asyncio

# Import existing API components
from .api import (
    LoginRequest, TokenResponse, ChatMessage, ChatResponse, 
    DocumentUploadResponse, SystemStatus, app
)

# Import new collaborative components
from .source_attribution import CitationStyle, SourceAttributionManager
from .collaboration import (
    workspace_manager, connection_manager, chat_manager,
    WorkspaceRole, PresenceStatus, Workspace
)
from .attributed_chat_engine import (
    attributed_chat_engine, collaborative_attributed_chat_manager
)
from .enhanced_vector_store import enhanced_vector_store_manager

logger = logging.getLogger(__name__)

# Enhanced API Models for Collaboration and Attribution

class AttributedChatMessage(BaseModel):
    """Enhanced chat message with attribution options."""
    message: str
    workspace_id: Optional[str] = None
    session_id: Optional[str] = "default"
    provider: Optional[str] = "openai"
    model: Optional[str] = "gpt-3.5-turbo"
    language: Optional[str] = "en"
    citation_style: Optional[str] = "apa"
    max_sources: Optional[int] = 5
    include_confidence: Optional[bool] = True

class AttributedChatResponse(BaseModel):
    """Enhanced chat response with source attribution."""
    response: str
    response_id: str
    session_id: str
    workspace_id: Optional[str] = None
    timestamp: datetime
    sources: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    confidence_score: float
    model_used: str
    processing_time: float
    ai_provider: str

class WorkspaceCreateRequest(BaseModel):
    """Workspace creation request."""
    name: str
    description: str = ""
    is_public: bool = False
    allow_file_upload: bool = True
    allow_chat: bool = True
    max_members: int = 50

class WorkspaceJoinRequest(BaseModel):
    """Workspace join request."""
    invite_code: str

class WorkspaceResponse(BaseModel):
    """Workspace response model."""
    id: str
    name: str
    description: str
    owner_id: str
    member_count: int
    document_count: int
    created_at: datetime
    invite_code: str
    role: str

class ChatMessageRequest(BaseModel):
    """Chat message request for workspaces."""
    content: str
    message_type: str = "text"
    reply_to: Optional[str] = None

class DocumentAttributionUpload(BaseModel):
    """Document upload with attribution tracking."""
    workspace_id: Optional[str] = None
    enable_attribution: bool = True
    extraction_method: str = "default"

# Mock user for demonstration (replace with real authentication)
class MockUser:
    def __init__(self, user_id: str, username: str, email: str):
        self.id = user_id
        self.username = username
        self.email = email

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> MockUser:
    """Get current authenticated user (mock implementation)."""
    # In production, validate JWT token and get real user
    return MockUser(
        user_id="user_123",
        username="demo_user", 
        email="demo@example.com"
    )

# Source Attribution Endpoints

@app.post("/api/chat/attributed", response_model=AttributedChatResponse)
async def chat_with_attribution(
    chat_request: AttributedChatMessage,
    current_user: MockUser = Depends(get_current_user)
):
    """Chat endpoint with complete source attribution."""
    try:
        # Set database type and load database
        db_type = "faiss"  # or get from config
        enhanced_vector_store_manager.set_database_type(db_type)
        vector_db = enhanced_vector_store_manager.load_database()
        
        if not vector_db:
            raise HTTPException(
                status_code=404,
                detail="No vector database found. Please upload documents first."
            )
        
        # Set attribution options
        attributed_chat_engine.set_citation_style(CitationStyle(chat_request.citation_style))
        attributed_chat_engine.set_max_sources(chat_request.max_sources)
        
        # Generate attributed response
        attributed_response = attributed_chat_engine.get_response_with_attribution(
            question=chat_request.message,
            vector_db=vector_db,
            workspace_id=chat_request.workspace_id
        )
        
        return AttributedChatResponse(
            response=attributed_response.response_text,
            response_id=attributed_response.response_id,
            session_id=chat_request.session_id,
            workspace_id=chat_request.workspace_id,
            timestamp=attributed_response.generated_at,
            sources=[
                {
                    "chunk_id": source.chunk_id,
                    "document_name": source.document_name,
                    "page_number": source.page_number,
                    "section_title": source.section_title,
                    "confidence_score": source.confidence_score,
                    "text_preview": source.text_content[:200] + "..." if len(source.text_content) > 200 else source.text_content
                }
                for source in attributed_response.sources
            ],
            citations=[citation.to_dict() for citation in attributed_response.citations],
            confidence_score=attributed_response.overall_confidence,
            model_used=attributed_response.model_used,
            processing_time=attributed_response.processing_time,
            ai_provider=attributed_response.ai_provider
        )
        
    except Exception as e:
        logger.error(f"Attribution chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/api/documents/upload-with-attribution", response_model=DocumentUploadResponse)
async def upload_document_with_attribution(
    file: UploadFile = File(...),
    workspace_id: Optional[str] = None,
    current_user: MockUser = Depends(get_current_user)
):
    """Upload document with source attribution tracking."""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.xlsx', '.pptx'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}"
            )
        
        start_time = datetime.utcnow()
        
        # Read file content
        file_content = await file.read()
        
        # Process document with attribution
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Process document
            documents = document_processor.process_document(temp_file_path)
            
            if not documents:
                raise HTTPException(status_code=400, detail="Failed to process document")
            
            # Set database type
            db_type = "faiss"  # or get from config
            enhanced_vector_store_manager.set_database_type(db_type)
            
            # Generate document ID
            document_id = enhanced_vector_store_manager.attribution_manager.generate_document_id(temp_file_path)
            
            # Check if database exists
            if enhanced_vector_store_manager.database_exists():
                # Load existing database
                vector_db = enhanced_vector_store_manager.load_database()
                if vector_db:
                    # Merge with attribution
                    vector_db = enhanced_vector_store_manager.merge_with_attribution(
                        vector_db, documents, file.filename, temp_file_path, document_id
                    )
                else:
                    # Create new database with attribution
                    vector_db = enhanced_vector_store_manager.create_database_with_attribution(
                        documents, file.filename, temp_file_path, document_id
                    )
            else:
                # Create new database with attribution
                vector_db = enhanced_vector_store_manager.create_database_with_attribution(
                    documents, file.filename, temp_file_path, document_id
                )
            
            # Save database
            enhanced_vector_store_manager.save_database(vector_db)
            
            # Add to workspace if specified
            if workspace_id:
                workspace = workspace_manager.get_workspace(workspace_id)
                if workspace and workspace_manager.verify_workspace_access(workspace_id, current_user.id):
                    workspace.documents.append(document_id)
                    workspace.updated_at = datetime.utcnow()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            document_count = enhanced_vector_store_manager.get_document_count(vector_db)
            
            return DocumentUploadResponse(
                filename=file.filename,
                status="success",
                message=f"Document processed successfully with source attribution. Document ID: {document_id}",
                document_count=document_count,
                processing_time=processing_time
            )
            
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Document upload with attribution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/documents/{document_id}/sources")
async def get_document_sources(
    document_id: str,
    current_user: MockUser = Depends(get_current_user)
):
    """Get all source chunks for a document."""
    try:
        sources = enhanced_vector_store_manager.attribution_manager.get_document_sources(document_id)
        
        return {
            "document_id": document_id,
            "total_chunks": len(sources),
            "sources": [
                {
                    "chunk_id": source.chunk_id,
                    "page_number": source.page_number,
                    "section_title": source.section_title,
                    "confidence_score": source.confidence_score,
                    "word_count": source.word_count,
                    "extraction_timestamp": source.extraction_timestamp.isoformat(),
                    "text_preview": source.text_content[:150] + "..." if len(source.text_content) > 150 else source.text_content
                }
                for source in sources
            ]
        }
        
    except Exception as e:
        logger.error(f"Get document sources error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sources: {str(e)}")

# Workspace Management Endpoints

@app.post("/api/workspaces", response_model=WorkspaceResponse)
async def create_workspace(
    workspace_data: WorkspaceCreateRequest,
    current_user: MockUser = Depends(get_current_user)
):
    """Create a new collaborative workspace."""
    try:
        workspace = workspace_manager.create_workspace(
            owner_id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            name=workspace_data.name,
            description=workspace_data.description
        )
        
        return WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            owner_id=workspace.owner_id,
            member_count=len(workspace.members),
            document_count=len(workspace.documents),
            created_at=workspace.created_at,
            invite_code=workspace.invite_code,
            role="owner"
        )
        
    except Exception as e:
        logger.error(f"Create workspace error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create workspace: {str(e)}")

@app.get("/api/workspaces")
async def list_user_workspaces(
    current_user: MockUser = Depends(get_current_user)
):
    """List all workspaces for the current user."""
    try:
        workspaces = workspace_manager.get_user_workspaces(current_user.id)
        
        return {
            "workspaces": [
                {
                    "id": ws.id,
                    "name": ws.name,
                    "description": ws.description,
                    "role": next(m.role.value for m in ws.members if m.user_id == current_user.id),
                    "member_count": len(ws.members),
                    "document_count": len(ws.documents),
                    "last_activity": ws.updated_at.isoformat(),
                    "invite_code": ws.invite_code if ws.owner_id == current_user.id else None
                }
                for ws in workspaces
            ]
        }
        
    except Exception as e:
        logger.error(f"List workspaces error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list workspaces: {str(e)}")

@app.post("/api/workspaces/{workspace_id}/join")
async def join_workspace(
    workspace_id: str,
    join_data: WorkspaceJoinRequest,
    current_user: MockUser = Depends(get_current_user)
):
    """Join workspace using invite code."""
    try:
        joined_workspace_id = workspace_manager.join_workspace_by_invite(
            join_data.invite_code,
            current_user.id,
            current_user.username,
            current_user.email
        )
        
        if joined_workspace_id:
            return {"message": "Successfully joined workspace", "workspace_id": joined_workspace_id}
        else:
            raise HTTPException(status_code=400, detail="Invalid invite code or unable to join")
        
    except Exception as e:
        logger.error(f"Join workspace error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to join workspace: {str(e)}")

@app.get("/api/workspaces/{workspace_id}")
async def get_workspace_details(
    workspace_id: str,
    current_user: MockUser = Depends(get_current_user)
):
    """Get detailed workspace information."""
    try:
        if not workspace_manager.verify_workspace_access(workspace_id, current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        workspace = workspace_manager.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        return workspace.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace details error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workspace: {str(e)}")

# Real-time Chat Endpoints

@app.get("/api/workspaces/{workspace_id}/chat/history")
async def get_chat_history(
    workspace_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    current_user: MockUser = Depends(get_current_user)
):
    """Get chat history for workspace."""
    try:
        if not workspace_manager.verify_workspace_access(workspace_id, current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        messages = chat_manager.get_chat_history(workspace_id, limit, before)
        
        return {
            "workspace_id": workspace_id,
            "messages": [message.to_dict() for message in messages]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chat history error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@app.post("/api/workspaces/{workspace_id}/chat/query")
async def collaborative_query(
    workspace_id: str,
    chat_request: AttributedChatMessage,
    current_user: MockUser = Depends(get_current_user)
):
    """Process query in collaborative workspace with attribution."""
    try:
        if not workspace_manager.verify_workspace_access(workspace_id, current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Load vector database
        db_type = "faiss"
        enhanced_vector_store_manager.set_database_type(db_type)
        vector_db = enhanced_vector_store_manager.load_database()
        
        if not vector_db:
            raise HTTPException(status_code=404, detail="No documents found in workspace")
        
        # Process collaborative query
        attributed_response = await collaborative_attributed_chat_manager.process_collaborative_query(
            workspace_id=workspace_id,
            user_id=current_user.id,
            username=current_user.username,
            query=chat_request.message,
            vector_db=vector_db
        )
        
        return attributed_response.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Collaborative query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# WebSocket Endpoint for Real-time Collaboration

@app.websocket("/ws/collaborate/{workspace_id}")
async def websocket_collaborate(websocket: WebSocket, workspace_id: str, user_id: str):
    """WebSocket endpoint for real-time collaboration."""
    try:
        # In production, verify user authentication from WebSocket headers
        username = f"user_{user_id}"  # Mock username
        
        # Verify workspace access
        if not workspace_manager.verify_workspace_access(workspace_id, user_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Connect to collaboration system
        await connection_manager.connect(websocket, workspace_id, user_id, username)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_websocket_message(message, workspace_id, user_id, username)
                
        except WebSocketDisconnect:
            # Handle user disconnect
            disconnect_info = connection_manager.disconnect(websocket)
            if disconnect_info:
                await connection_manager.broadcast_to_workspace(workspace_id, {
                    "type": "user_left",
                    "data": {
                        "user_id": user_id,
                        "username": username,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
        
    except Exception as e:
        logger.error(f"WebSocket collaboration error: {str(e)}")
        await websocket.close()

async def handle_websocket_message(message: dict, workspace_id: str, user_id: str, username: str):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")
    data = message.get("data", {})
    
    if message_type == "chat_message":
        await chat_manager.send_chat_message(
            workspace_id=workspace_id,
            user_id=user_id,
            username=username,
            content=data.get("content", ""),
            message_type=data.get("message_type", "text")
        )
    
    elif message_type == "typing_indicator":
        await connection_manager.handle_typing_indicator(
            workspace_id, user_id, data.get("is_typing", False)
        )
    
    elif message_type == "presence_update":
        # Handle presence updates
        await connection_manager.broadcast_to_workspace(workspace_id, {
            "type": "presence_update",
            "data": {
                "user_id": user_id,
                "status": data.get("status", "active"),
                "timestamp": datetime.utcnow().isoformat()
            }
        })

# Attribution Analytics Endpoint

@app.get("/api/analytics/attribution")
async def get_attribution_analytics(
    workspace_id: Optional[str] = None,
    current_user: MockUser = Depends(get_current_user)
):
    """Get source attribution analytics."""
    try:
        # Load database
        db_type = "faiss"
        enhanced_vector_store_manager.set_database_type(db_type)
        vector_db = enhanced_vector_store_manager.load_database()
        
        if not vector_db:
            return {"message": "No database found"}
        
        # Get attribution summary
        summary = enhanced_vector_store_manager.get_attribution_summary(vector_db)
        
        # Get validation results
        validation = enhanced_vector_store_manager.validate_attribution_integrity(vector_db)
        
        return {
            "summary": summary,
            "validation": validation,
            "workspace_id": workspace_id,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Attribution analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

# Enhanced system status with collaboration features
@app.get("/api/system/status", response_model=Dict[str, Any])
async def enhanced_system_status():
    """Get enhanced system status including collaboration features."""
    try:
        # Get basic system status
        basic_status = {
            "version": "3.0.0-enhanced",
            "features": {
                "source_attribution": True,
                "collaborative_workspaces": True,
                "real_time_chat": True,
                "websocket_support": True,
                "multi_citation_formats": True
            },
            "database_type": enhanced_vector_store_manager.current_db_type,
            "supported_formats": {
                "pdf": "Portable Document Format",
                "docx": "Microsoft Word Document", 
                "txt": "Plain Text",
                "xlsx": "Microsoft Excel Spreadsheet",
                "pptx": "Microsoft PowerPoint Presentation"
            },
            "citation_styles": [style.value for style in CitationStyle],
            "collaboration": {
                "active_workspaces": len(workspace_manager.workspaces),
                "online_users": len(connection_manager.user_connections),
                "websocket_connections": sum(len(connections) for connections in connection_manager.workspace_connections.values())
            }
        }
        
        # Add database info if available
        db_type = "faiss"
        enhanced_vector_store_manager.set_database_type(db_type)
        if enhanced_vector_store_manager.database_exists():
            vector_db = enhanced_vector_store_manager.load_database()
            if vector_db:
                basic_status["document_count"] = enhanced_vector_store_manager.get_document_count(vector_db)
                basic_status["attribution_summary"] = enhanced_vector_store_manager.get_attribution_summary(vector_db)
        
        return basic_status
        
    except Exception as e:
        logger.error(f"Enhanced system status error: {str(e)}")
        return {
            "version": "3.0.0-enhanced",
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)