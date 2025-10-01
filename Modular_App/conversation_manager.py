"""
Enhanced Conversation Manager with Source Attribution
Manages conversation history and state for the GenAI chatbot with attribution support.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .source_attribution import AttributedResponse, ChunkMetadata


class ConversationManager:
    """Manages conversation history and state with source attribution."""
    
    def __init__(self):
        self.session_key_chat_history = "chat_history"
        self.session_key_attributed_history = "chat_history_with_sources"
        self.session_key_conversation_state = "conversation_state"
    
    def initialize_session_state(self) -> None:
        """Initialize Streamlit session state for conversations."""
        if self.session_key_chat_history not in st.session_state:
            st.session_state[self.session_key_chat_history] = []
        
        if self.session_key_attributed_history not in st.session_state:
            st.session_state[self.session_key_attributed_history] = []
        
        if self.session_key_conversation_state not in st.session_state:
            st.session_state[self.session_key_conversation_state] = {
                "session_id": self._generate_session_id(),
                "started_at": datetime.utcnow().isoformat(),
                "total_messages": 0,
                "total_sources_cited": 0
            }
    
    def add_attributed_message(self, question: str, attributed_response: AttributedResponse) -> None:
        """Add a message with source attribution to history."""
        message_entry = {
            'question': question,
            'response': attributed_response.response_text,
            'sources': [source.to_dict() for source in attributed_response.sources],
            'citations': [citation.to_dict() for citation in attributed_response.citations],
            'confidence': attributed_response.overall_confidence,
            'timestamp': attributed_response.generated_at.isoformat(),
            'response_id': attributed_response.response_id,
            'ai_provider': attributed_response.ai_provider,
            'model_used': attributed_response.model_used,
            'processing_time': attributed_response.processing_time
        }
        
        # Add to attributed history
        st.session_state[self.session_key_attributed_history].append(message_entry)
        
        # Add to regular history for backward compatibility
        st.session_state[self.session_key_chat_history].append({
            'question': question,
            'answer': attributed_response.response_text
        })
        
        # Update conversation state
        st.session_state[self.session_key_conversation_state]["total_messages"] += 1
        st.session_state[self.session_key_conversation_state]["total_sources_cited"] += len(attributed_response.sources)
    
    def add_regular_message(self, question: str, answer: str) -> None:
        """Add a regular message without attribution to history."""
        message_entry = {
            'question': question,
            'answer': answer,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        st.session_state[self.session_key_chat_history].append(message_entry)
        st.session_state[self.session_key_conversation_state]["total_messages"] += 1
    
    def get_attributed_history(self) -> List[Dict[str, Any]]:
        """Get chat history with source attribution."""
        return st.session_state.get(self.session_key_attributed_history, [])
    
    def get_regular_history(self) -> List[Dict[str, Any]]:
        """Get regular chat history."""
        return st.session_state.get(self.session_key_chat_history, [])
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state."""
        return st.session_state.get(self.session_key_conversation_state, {})
    
    def clear_history(self) -> None:
        """Clear all conversation history."""
        st.session_state[self.session_key_chat_history] = []
        st.session_state[self.session_key_attributed_history] = []
        st.session_state[self.session_key_conversation_state] = {
            "session_id": self._generate_session_id(),
            "started_at": datetime.utcnow().isoformat(),
            "total_messages": 0,
            "total_sources_cited": 0
        }
    
    def export_conversation(self, include_attribution: bool = True) -> Dict[str, Any]:
        """Export conversation history."""
        export_data = {
            "session_info": self.get_conversation_state(),
            "exported_at": datetime.utcnow().isoformat(),
            "message_count": len(self.get_regular_history())
        }
        
        if include_attribution:
            export_data["attributed_messages"] = self.get_attributed_history()
        else:
            export_data["messages"] = self.get_regular_history()
        
        return export_data
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary statistics."""
        attributed_history = self.get_attributed_history()
        regular_history = self.get_regular_history()
        
        if attributed_history:
            total_sources = sum(len(msg.get('sources', [])) for msg in attributed_history)
            avg_confidence = sum(msg.get('confidence', 0) for msg in attributed_history) / len(attributed_history)
            unique_documents = len(set(
                source['document_name'] 
                for msg in attributed_history 
                for source in msg.get('sources', [])
            ))
            
            return {
                "total_messages": len(attributed_history),
                "total_sources_cited": total_sources,
                "average_confidence": avg_confidence,
                "unique_documents_referenced": unique_documents,
                "session_duration": self._calculate_session_duration(),
                "has_attribution": True
            }
        else:
            return {
                "total_messages": len(regular_history),
                "total_sources_cited": 0,
                "average_confidence": 0,
                "unique_documents_referenced": 0,
                "session_duration": self._calculate_session_duration(),
                "has_attribution": False
            }
    
    def find_messages_by_source(self, document_name: str) -> List[Dict[str, Any]]:
        """Find all messages that cite a specific document."""
        attributed_history = self.get_attributed_history()
        matching_messages = []
        
        for msg in attributed_history:
            sources = msg.get('sources', [])
            if any(source['document_name'] == document_name for source in sources):
                matching_messages.append(msg)
        
        return matching_messages
    
    def get_most_cited_sources(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most frequently cited sources."""
        attributed_history = self.get_attributed_history()
        source_counts = {}
        
        for msg in attributed_history:
            for source in msg.get('sources', []):
                doc_name = source['document_name']
                if doc_name not in source_counts:
                    source_counts[doc_name] = {
                        'count': 0,
                        'avg_confidence': 0,
                        'total_confidence': 0,
                        'document_name': doc_name
                    }
                
                source_counts[doc_name]['count'] += 1
                source_counts[doc_name]['total_confidence'] += source.get('confidence_score', 0)
        
        # Calculate average confidence
        for source_data in source_counts.values():
            if source_data['count'] > 0:
                source_data['avg_confidence'] = source_data['total_confidence'] / source_data['count']
        
        # Sort by count and return top results
        sorted_sources = sorted(source_counts.values(), key=lambda x: x['count'], reverse=True)
        return sorted_sources[:limit]
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return f"session_{uuid.uuid4().hex[:8]}"
    
    def _calculate_session_duration(self) -> str:
        """Calculate session duration."""
        state = self.get_conversation_state()
        started_at = state.get('started_at')
        
        if started_at:
            try:
                start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                duration = datetime.utcnow() - start_time.replace(tzinfo=None)
                
                hours = duration.seconds // 3600
                minutes = (duration.seconds % 3600) // 60
                
                if hours > 0:
                    return f"{hours}h {minutes}m"
                else:
                    return f"{minutes}m"
            except:
                return "Unknown"
        
        return "Unknown"


# Global instance
conversation_manager = ConversationManager()