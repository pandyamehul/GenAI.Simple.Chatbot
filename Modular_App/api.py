"""
REST API interface for the GenAI PDF Chatbot.
Provides endpoints for document upload, chat interactions, and system management.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import tempfile
import uvicorn
from datetime import datetime, timedelta
import logging

# JWT is optional - will use fallback if not available
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# Import our modular components
from .config import config_manager
from .document_processor import document_processor
from .vector_store import vector_store_manager
from .chat_engine import chat_engine
from .multi_model_provider import multi_model_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Models
class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int

class ChatMessage(BaseModel):
    """Chat message model."""
    message: str
    session_id: Optional[str] = "default"
    provider: Optional[str] = "openai"
    model: Optional[str] = "gpt-3.5-turbo"
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str
    timestamp: datetime
    sources: Optional[List[str]] = None
    model_used: str
    processing_time: float

class DocumentUploadResponse(BaseModel):
    """Document upload response model."""
    filename: str
    status: str
    message: str
    document_count: Optional[int] = None
    processing_time: Optional[float] = None

class SystemStatus(BaseModel):
    """System status model."""
    version: str
    available_providers: List[str]
    database_type: str
    document_count: int
    supported_formats: Dict[str, str]
    supported_languages: Dict[str, str]

class DatabaseConfig(BaseModel):
    """Database configuration model."""
    database_type: str  # "faiss" or "chromadb"

class ModelConfig(BaseModel):
    """Model configuration model."""
    provider: str
    model: str
    embedding_model: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="GenAI PDF Chatbot API",
    description="REST API for the GenAI PDF Chatbot with multi-format document support",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Authentication constants
SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    try:
        if JWT_AVAILABLE:
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        else:
            # Fallback if JWT not available - use simple token
            return f"simple_token_{data.get('sub', 'user')}_{int(expire.timestamp())}"
    except:
        # Fallback if JWT not available - use simple token
        return f"simple_token_{data.get('sub', 'user')}_{int(expire.timestamp())}"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify API token."""
    token = credentials.credentials
    
    # Try JWT verification first
    try:
        if JWT_AVAILABLE:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return username
    except:
        pass
    
    # Fallback to simple token verification
    expected_token = os.getenv("API_TOKEN", "admin-token")
    if token == expected_token:
        return "admin"
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API token"
    )

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials."""
    # Simple authentication - enhance for production
    valid_users = {
        "admin": "password123",
        "user": "userpass"
    }
    return valid_users.get(username) == password

# API Endpoints

@app.post("/auth/token", response_model=TokenResponse)
async def login_for_access_token(login_request: LoginRequest):
    """Authenticate user and return access token."""
    if not authenticate_user(login_request.username, login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": login_request.username}, 
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600  # in seconds
    )

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "GenAI PDF Chatbot API",
        "version": "2.1.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": str(datetime.now())}

@app.get("/status", response_model=SystemStatus)
async def get_system_status(token: str = Depends(verify_token)):
    """Get system status and configuration."""
    try:
        # Get document count from current vector database
        db = vector_store_manager.load_database()
        doc_count = vector_store_manager.get_document_count(db) if db else 0
        
        return SystemStatus(
            version=config_manager.app_config.APP_VERSION,
            available_providers=multi_model_manager.get_available_providers(),
            database_type=vector_store_manager.current_db_type or "not_set",
            document_count=doc_count,
            supported_formats=document_processor.get_supported_formats(),
            supported_languages=config_manager.get_supported_languages()
        )
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=List[DocumentUploadResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    database_type: str = "faiss",
    token: str = Depends(verify_token)
):
    """Upload and process documents."""
    responses = []
    start_time = datetime.now()
    
    try:
        # Set database type
        vector_store_manager.set_database_type(database_type)
        
        for file in files:
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
                    content = await file.read()
                    tmp_file.write(content)
                    tmp_file_path = tmp_file.name
                
                # Create UploadFile-like object for processing
                class MockUploadedFile:
                    def __init__(self, filename, content):
                        self.name = filename
                        self.size = len(content)
                        self._content = content
                    
                    def read(self):
                        return self._content
                    
                    def getvalue(self):
                        return self._content
                
                mock_file = MockUploadedFile(file.filename, content)
                
                # Validate file
                is_valid, error_msg = document_processor.validate_file(mock_file)
                if not is_valid:
                    responses.append(DocumentUploadResponse(
                        filename=file.filename,
                        status="error",
                        message=error_msg
                    ))
                    continue
                
                # Process document
                docs = document_processor._process_single_file(mock_file)
                split_docs = document_processor.split_documents(docs)
                
                # Load existing database or create new one
                existing_db = vector_store_manager.load_database()
                
                if existing_db:
                    # Add to existing database
                    vector_store_manager.merge_databases(existing_db, split_docs)
                    final_db = existing_db
                else:
                    # Create new database
                    final_db = vector_store_manager.create_database(split_docs)
                
                # Save database
                vector_store_manager.save_database(final_db)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                responses.append(DocumentUploadResponse(
                    filename=file.filename,
                    status="success",
                    message=f"Successfully processed {len(split_docs)} document chunks",
                    document_count=len(split_docs),
                    processing_time=processing_time
                ))
                
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                responses.append(DocumentUploadResponse(
                    filename=file.filename,
                    status="error",
                    message=str(e)
                ))
        
        return responses
        
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_with_documents(
    message: ChatMessage,
    token: str = Depends(verify_token)
):
    """Chat with uploaded documents."""
    start_time = datetime.now()
    
    try:
        # Load vector database
        db = vector_store_manager.load_database()
        if not db:
            raise HTTPException(
                status_code=404, 
                detail="No documents found. Please upload documents first."
            )
        
        # Initialize chat engine with specified provider and model
        chat_engine.initialize_conversation_chain(
            vectorstore=db,
            provider=message.provider,
            model=message.model
        )
        
        # Get response
        response = chat_engine.get_response(
            query=message.message,
            session_id=message.session_id
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            response=response,
            session_id=message.session_id,
            timestamp=datetime.now(),
            model_used=f"{message.provider}:{message.model}",
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{session_id}")
async def get_conversation_history(
    session_id: str,
    token: str = Depends(verify_token)
):
    """Get conversation history for a session."""
    try:
        history = chat_engine.get_conversation_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversations/{session_id}")
async def clear_conversation(
    session_id: str,
    token: str = Depends(verify_token)
):
    """Clear conversation history for a session."""
    try:
        chat_engine.clear_conversation_memory(session_id)
        return {"message": f"Conversation {session_id} cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/configure/database")
async def configure_database(
    config: DatabaseConfig,
    token: str = Depends(verify_token)
):
    """Configure vector database type."""
    try:
        vector_store_manager.set_database_type(config.database_type)
        return {"message": f"Database type set to {config.database_type}"}
    except Exception as e:
        logger.error(f"Error configuring database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/providers")
async def get_available_providers(token: str = Depends(verify_token)):
    """Get available model providers and their status."""
    try:
        providers_status = {}
        for provider in ["openai", "anthropic", "google", "local"]:
            providers_status[provider] = multi_model_manager.validate_provider_setup(provider)
        
        return providers_status
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/{provider}")
async def get_provider_models(
    provider: str,
    token: str = Depends(verify_token)
):
    """Get available models for a specific provider."""
    try:
        chat_models = config_manager.get_available_models(provider)
        embedding_models = config_manager.get_available_embedding_models(provider)
        
        return {
            "provider": provider,
            "chat_models": chat_models,
            "embedding_models": embedding_models
        }
    except Exception as e:
        logger.error(f"Error getting models for provider {provider}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents")
async def clear_all_documents(token: str = Depends(verify_token)):
    """Clear all documents from the vector database."""
    try:
        # Delete vector databases
        paths = config_manager.get_vector_db_paths()
        
        success_messages = []
        if vector_store_manager.current_store:
            if vector_store_manager.current_store.delete(paths["faiss_path"]):
                success_messages.append("FAISS database cleared")
            if vector_store_manager.current_store.delete(paths["chroma_dir"]):
                success_messages.append("ChromaDB database cleared")
        
        return {"message": "Documents cleared", "details": success_messages}
    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": str(datetime.now())}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": str(datetime.now())}
    )

# Run the API server
if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )