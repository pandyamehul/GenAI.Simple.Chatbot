"""
Real-time Collaborative Features System
Provides workspace management, real-time chat, and user collaboration features
for the GenAI Enterprise Document Intelligence Platform.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles in collaborative workspace."""
    OWNER = "owner"
    ADMIN = "admin"
    COLLABORATOR = "collaborator"
    VIEWER = "viewer"


class WorkspacePermission(Enum):
    """Workspace permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"


class MessageType(Enum):
    """Types of collaborative messages."""
    TEXT = "text"
    DOCUMENT_UPLOAD = "document_upload"
    QUERY = "query"
    RESPONSE = "response"
    SYSTEM = "system"
    NOTIFICATION = "notification"


class PresenceStatus(Enum):
    """User presence status."""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class WorkspaceUser:
    """Represents a user in a collaborative workspace."""
    user_id: str
    username: str
    role: UserRole
    permissions: Set[WorkspacePermission]
    joined_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    is_online: bool = False
    avatar_url: Optional[str] = None
    
    def has_permission(self, permission: WorkspacePermission) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions or WorkspacePermission.ADMIN in self.permissions


@dataclass
class CollaborativeMessage:
    """Represents a message in collaborative chat."""
    message_id: str
    workspace_id: str
    user_id: str
    username: str
    content: str
    message_type: MessageType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    replies: List['CollaborativeMessage'] = field(default_factory=list)
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji -> user_ids
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    
    def add_reaction(self, emoji: str, user_id: str):
        """Add reaction to message."""
        if emoji not in self.reactions:
            self.reactions[emoji] = []
        if user_id not in self.reactions[emoji]:
            self.reactions[emoji].append(user_id)
    
    def remove_reaction(self, emoji: str, user_id: str):
        """Remove reaction from message."""
        if emoji in self.reactions and user_id in self.reactions[emoji]:
            self.reactions[emoji].remove(user_id)
            if not self.reactions[emoji]:
                del self.reactions[emoji]


@dataclass
class Workspace:
    """Represents a collaborative workspace."""
    workspace_id: str
    name: str
    description: str
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    users: Dict[str, WorkspaceUser] = field(default_factory=dict)
    documents: List[str] = field(default_factory=list)  # Document IDs
    chat_history: List[CollaborativeMessage] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def add_user(self, user: WorkspaceUser):
        """Add user to workspace."""
        self.users[user.user_id] = user
    
    def remove_user(self, user_id: str):
        """Remove user from workspace."""
        if user_id in self.users:
            del self.users[user_id]
    
    def get_online_users(self) -> List[WorkspaceUser]:
        """Get list of online users."""
        return [user for user in self.users.values() if user.is_online]
    
    def add_message(self, message: CollaborativeMessage):
        """Add message to chat history."""
        self.chat_history.append(message)
    
    def get_recent_messages(self, limit: int = 50) -> List[CollaborativeMessage]:
        """Get recent messages."""
        return self.chat_history[-limit:] if self.chat_history else []


class WebSocketConnectionManager:
    """Manages WebSocket connections for real-time collaboration."""
    
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Any]] = {}  # user_id -> connection_info
        self.workspace_connections: Dict[str, Set[str]] = {}  # workspace_id -> user_ids
        self.message_handlers: Dict[str, Callable] = {}
        
    def connect(self, user_id: str, workspace_id: str, websocket: Any):
        """Connect user to workspace."""
        self.active_connections[user_id] = {
            'websocket': websocket,
            'workspace_id': workspace_id,
            'connected_at': datetime.utcnow()
        }
        
        if workspace_id not in self.workspace_connections:
            self.workspace_connections[workspace_id] = set()
        self.workspace_connections[workspace_id].add(user_id)
        
        logger.info(f"User {user_id} connected to workspace {workspace_id}")
    
    def disconnect(self, user_id: str):
        """Disconnect user."""
        if user_id in self.active_connections:
            workspace_id = self.active_connections[user_id]['workspace_id']
            del self.active_connections[user_id]
            
            if workspace_id in self.workspace_connections:
                self.workspace_connections[workspace_id].discard(user_id)
                if not self.workspace_connections[workspace_id]:
                    del self.workspace_connections[workspace_id]
            
            logger.info(f"User {user_id} disconnected from workspace {workspace_id}")
    
    async def broadcast_to_workspace(self, workspace_id: str, message: Dict[str, Any], 
                                   exclude_user: Optional[str] = None):
        """Broadcast message to all users in workspace."""
        if workspace_id not in self.workspace_connections:
            return
        
        for user_id in self.workspace_connections[workspace_id]:
            if exclude_user and user_id == exclude_user:
                continue
                
            if user_id in self.active_connections:
                try:
                    websocket = self.active_connections[user_id]['websocket']
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    # Remove disconnected user
                    self.disconnect(user_id)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user."""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]['websocket']
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                self.disconnect(user_id)
    
    def get_workspace_users(self, workspace_id: str) -> Set[str]:
        """Get connected users in workspace."""
        return self.workspace_connections.get(workspace_id, set())
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if user is connected."""
        return user_id in self.active_connections


class CollaborativeChatManager:
    """Manages collaborative chat functionality."""
    
    def __init__(self, connection_manager: WebSocketConnectionManager):
        self.connection_manager = connection_manager
        self.message_store: Dict[str, List[CollaborativeMessage]] = {}  # workspace_id -> messages
        
    def add_message(self, workspace_id: str, user_id: str, username: str, 
                   content: str, message_type: MessageType = MessageType.TEXT,
                   metadata: Optional[Dict[str, Any]] = None) -> CollaborativeMessage:
        """Add message to chat."""
        message = CollaborativeMessage(
            message_id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            user_id=user_id,
            username=username,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        
        if workspace_id not in self.message_store:
            self.message_store[workspace_id] = []
        
        self.message_store[workspace_id].append(message)
        return message
    
    async def broadcast_message(self, message: CollaborativeMessage):
        """Broadcast message to workspace users."""
        message_data = {
            'type': 'chat_message',
            'data': {
                'message_id': message.message_id,
                'user_id': message.user_id,
                'username': message.username,
                'content': message.content,
                'message_type': message.message_type.value,
                'timestamp': message.timestamp.isoformat(),
                'metadata': message.metadata
            }
        }
        
        await self.connection_manager.broadcast_to_workspace(
            message.workspace_id, message_data, exclude_user=message.user_id
        )
    
    def get_chat_history(self, workspace_id: str, limit: int = 50) -> List[CollaborativeMessage]:
        """Get chat history for workspace."""
        if workspace_id not in self.message_store:
            return []
        
        messages = self.message_store[workspace_id]
        return messages[-limit:] if messages else []


class WorkspaceManager:
    """Manages collaborative workspaces."""
    
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.user_workspaces: Dict[str, Set[str]] = {}  # user_id -> workspace_ids
        
    def create_workspace(self, name: str, description: str, creator_id: str, 
                        creator_username: str) -> Workspace:
        """Create new workspace."""
        workspace_id = str(uuid.uuid4())
        
        # Create workspace
        workspace = Workspace(
            workspace_id=workspace_id,
            name=name,
            description=description,
            created_by=creator_id
        )
        
        # Add creator as owner
        creator = WorkspaceUser(
            user_id=creator_id,
            username=creator_username,
            role=UserRole.OWNER,
            permissions={perm for perm in WorkspacePermission}
        )
        workspace.add_user(creator)
        
        # Store workspace
        self.workspaces[workspace_id] = workspace
        
        # Track user workspaces
        if creator_id not in self.user_workspaces:
            self.user_workspaces[creator_id] = set()
        self.user_workspaces[creator_id].add(workspace_id)
        
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID."""
        return self.workspaces.get(workspace_id)
    
    def get_user_workspaces(self, user_id: str) -> List[Workspace]:
        """Get workspaces for user."""
        if user_id not in self.user_workspaces:
            return []
        
        workspaces = []
        for workspace_id in self.user_workspaces[user_id]:
            if workspace_id in self.workspaces:
                workspaces.append(self.workspaces[workspace_id])
        
        return workspaces
    
    def invite_user(self, workspace_id: str, user_id: str, username: str, 
                   role: UserRole = UserRole.COLLABORATOR) -> bool:
        """Invite user to workspace."""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return False
        
        # Set permissions based on role
        permissions = set()
        if role == UserRole.OWNER:
            permissions = {perm for perm in WorkspacePermission}
        elif role == UserRole.ADMIN:
            permissions = {WorkspacePermission.READ, WorkspacePermission.WRITE, 
                          WorkspacePermission.DELETE, WorkspacePermission.SHARE}
        elif role == UserRole.COLLABORATOR:
            permissions = {WorkspacePermission.READ, WorkspacePermission.WRITE}
        elif role == UserRole.VIEWER:
            permissions = {WorkspacePermission.READ}
        
        user = WorkspaceUser(
            user_id=user_id,
            username=username,
            role=role,
            permissions=permissions
        )
        
        workspace.add_user(user)
        
        # Track user workspaces
        if user_id not in self.user_workspaces:
            self.user_workspaces[user_id] = set()
        self.user_workspaces[user_id].add(workspace_id)
        
        return True
    
    def get_workspace_stats(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace statistics."""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return {}
        
        online_users = workspace.get_online_users()
        
        return {
            'total_users': len(workspace.users),
            'online_users': len(online_users),
            'total_documents': len(workspace.documents),
            'total_messages': len(workspace.chat_history),
            'created_at': workspace.created_at.isoformat(),
            'last_activity': max([user.last_active for user in workspace.users.values()]).isoformat() if workspace.users else None
        }


# Factory functions
def create_workspace_manager() -> WorkspaceManager:
    """Factory function to create workspace manager."""
    return WorkspaceManager()


def create_collaboration_system():
    """Factory function to create complete collaboration system."""
    workspace_manager = WorkspaceManager()
    connection_manager = WebSocketConnectionManager()
    chat_manager = CollaborativeChatManager(connection_manager)
    
    return workspace_manager, connection_manager, chat_manager


# Utility functions
async def handle_collaborative_query(workspace_id: str, user_id: str, username: str,
                                   query: str, chat_manager: CollaborativeChatManager):
    """Handle collaborative query with broadcasting."""
    # Add query message
    query_message = chat_manager.add_message(
        workspace_id=workspace_id,
        user_id=user_id,
        username=username,
        content=query,
        message_type=MessageType.QUERY
    )
    
    # Broadcast query
    await chat_manager.broadcast_message(query_message)
    
    return query_message


async def handle_collaborative_response(workspace_id: str, response_text: str,
                                      chat_manager: CollaborativeChatManager,
                                      system_user_id: str = "system"):
    """Handle system response with broadcasting."""
    # Add response message
    response_message = chat_manager.add_message(
        workspace_id=workspace_id,
        user_id=system_user_id,
        username="AI Assistant",
        content=response_text,
        message_type=MessageType.RESPONSE
    )
    
    # Broadcast response
    await chat_manager.broadcast_message(response_message)
    
    return response_message