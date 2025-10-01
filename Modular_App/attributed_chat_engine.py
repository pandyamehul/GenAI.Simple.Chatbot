"""
Attributed Chat Engine
Enhanced chat engine with source attribution capabilities for the GenAI platform.
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from .source_attribution import (
    SourceAttributionManager, AttributedResponse, ChunkMetadata, 
    CitationStyle, ConfidenceLevel
)

logger = logging.getLogger(__name__)

@dataclass
class AttributedQueryResult:
    """Result of an attributed query with sources."""
    response: AttributedResponse
    query: str
    processing_time: float
    model_used: str
    chunks_analyzed: int
    confidence_breakdown: Dict[str, Any]

class AttributedChatEngine:
    """Enhanced chat engine with source attribution capabilities."""
    
    def __init__(self, chat_engine, vector_store, attribution_manager: SourceAttributionManager):
        self.chat_engine = chat_engine
        self.vector_store = vector_store
        self.attribution_manager = attribution_manager
        self.conversation_history: List[AttributedResponse] = []
        
        # Default settings
        self.citation_style = CitationStyle.APA
        self.max_sources = 5
        
    async def process_attributed_query(self, query: str, 
                                     citation_style: CitationStyle = CitationStyle.APA,
                                     max_sources: int = 5,
                                     min_confidence: float = 0.3) -> AttributedQueryResult:
        """Process query with improved answer extraction and summarization."""
        import time
        start_time = time.time()
        try:
            # Get relevant documents with similarity scores
            if hasattr(self.vector_store, 'similarity_search_with_scores'):
                relevant_docs = self.vector_store.similarity_search_with_scores(query, k=max_sources)
            else:
                docs = self.vector_store.similarity_search(query, k=max_sources)
                relevant_docs = [(doc, 0.8) for doc in docs]

            # Filter by minimum confidence
            filtered_docs = [
                (doc, score) for doc, score in relevant_docs 
                if score >= min_confidence
            ]
            # Deduplicate by chunk text to ensure diversity
            seen_texts = set()
            diverse_docs = []
            for doc, score in filtered_docs:
                text = doc.page_content.strip()
                if text not in seen_texts:
                    diverse_docs.append((doc, score))
                    seen_texts.add(text)
                if len(diverse_docs) >= 3:
                    break

            if not diverse_docs:
                response_text = "I couldn't find relevant information in the available documents to answer your question."
                attributed_response = AttributedResponse(
                    response_text=response_text,
                    citations=[],
                    source_chunks=[],
                    confidence_score=0.0,
                    attribution_quality=ConfidenceLevel.VERY_LOW
                )
            else:
                chunk_ids = []
                contexts = []
                for doc, similarity_score in diverse_docs:
                    chunk_metadata = self.attribution_manager.track_document_chunk(
                        doc_id=getattr(doc, 'metadata', {}).get('document_id', 'unknown'),
                        chunk_text=doc.page_content,
                        document_name=getattr(doc, 'metadata', {}).get('source', 'Unknown Document'),
                        file_path=getattr(doc, 'metadata', {}).get('file_path', 'unknown'),
                        page_number=getattr(doc, 'metadata', {}).get('page', None),
                        section_title=getattr(doc, 'metadata', {}).get('section', None)
                    )
                    self.attribution_manager.update_chunk_confidence(
                        chunk_metadata.chunk_id, similarity_score
                    )
                    chunk_ids.append(chunk_metadata.chunk_id)
                    contexts.append(doc.page_content)
                # Compose focused prompt
                context_text = "\n\n".join(contexts)
                enhanced_query = f"""You are a helpful assistant. If the answer to the user's question is present in the context below, extract it exactly and return only the answer (not the whole chunk, not a summary). If the answer is not present, reply: 'Not found.'

Context:
{context_text}

Question: {query}

Answer:"""
                if hasattr(self.chat_engine, 'generate_response'):
                    response_text = await self.chat_engine.generate_response(enhanced_query)
                else:
                    response_text = self.chat_engine.get_response(enhanced_query)
                # Clean up LLM output
                cleaned = response_text.strip().replace('Answer:', '').replace('answer:', '').strip()
                # If LLM says Not found, try aggregating partial answers from each chunk
                if cleaned.lower() in ["not found.", "not found", "no answer found.", "no answer found"]:
                    partials = []
                    for i, context in enumerate(contexts):
                        single_context_prompt = f"""You are a helpful assistant. If the answer to the user's question is present in the context below, extract it exactly and return only the answer. If not, reply: 'Not found.'

Context:
{context}

Question: {query}

Answer:"""
                        if hasattr(self.chat_engine, 'generate_response'):
                            part = await self.chat_engine.generate_response(single_context_prompt)
                        else:
                            part = self.chat_engine.get_response(single_context_prompt)
                        part_clean = part.strip().replace('Answer:', '').replace('answer:', '').strip()
                        if part_clean and part_clean.lower() not in ["not found.", "not found", "no answer found.", "no answer found"]:
                            partials.append(part_clean)
                    if partials:
                        cleaned = "\n".join(partials)
                attributed_response = self.attribution_manager.create_attributed_response(
                    response_text=cleaned,
                    source_chunk_ids=chunk_ids,
                    citation_style=citation_style
                )
            self.conversation_history.append(attributed_response)
            processing_time = time.time() - start_time
            confidence_breakdown = {
                'overall_confidence': attributed_response.confidence_score,
                'attribution_quality': attributed_response.attribution_quality.value,
                'sources_used': len(attributed_response.source_chunks),
                'citations_generated': len(attributed_response.citations),
                'chunks_analyzed': len(diverse_docs)
            }
            return AttributedQueryResult(
                response=attributed_response,
                query=query,
                processing_time=processing_time,
                model_used=getattr(self.chat_engine, 'model_name', 'unknown'),
                chunks_analyzed=len(diverse_docs),
                confidence_breakdown=confidence_breakdown
            )
        except Exception as e:
            logger.error(f"Error in attributed query processing: {e}")
            error_response = AttributedResponse(
                response_text=f"An error occurred while processing your query: {str(e)}",
                citations=[],
                source_chunks=[],
                confidence_score=0.0,
                attribution_quality=ConfidenceLevel.VERY_LOW
            )
            return AttributedQueryResult(
                response=error_response,
                query=query,
                processing_time=time.time() - start_time,
                model_used="error",
                chunks_analyzed=0,
                confidence_breakdown={'error': str(e)}
            )
    
    def get_conversation_history(self, limit: int = 10) -> List[AttributedResponse]:
        """Get recent conversation history with attribution."""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def clear_conversation_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def get_attribution_stats(self) -> Dict[str, Any]:
        """Get attribution statistics for this session."""
        if not self.conversation_history:
            return {'total_responses': 0}
        
        total_responses = len(self.conversation_history)
        total_sources = sum(len(resp.source_chunks) for resp in self.conversation_history)
        avg_confidence = sum(resp.confidence_score for resp in self.conversation_history) / total_responses
        
        confidence_distribution = {level.value: 0 for level in ConfidenceLevel}
        for response in self.conversation_history:
            confidence_distribution[response.attribution_quality.value] += 1
        
        return {
            'total_responses': total_responses,
            'total_sources_used': total_sources,
            'average_confidence': avg_confidence,
            'confidence_distribution': confidence_distribution,
            'attribution_manager_stats': self.attribution_manager.get_attribution_stats()
        }
    
    def regenerate_response_with_style(self, response_id: str, 
                                     citation_style: CitationStyle) -> Optional[AttributedResponse]:
        """Regenerate response with different citation style."""
        # Find the response in history
        target_response = None
        for response in self.conversation_history:
            if response.response_id == response_id:
                target_response = response
                break
        
        if not target_response:
            return None
        
        # Regenerate with new citation style
        chunk_ids = [chunk.chunk_id for chunk in target_response.source_chunks]
        new_response = self.attribution_manager.create_attributed_response(
            response_text=target_response.response_text,
            source_chunk_ids=chunk_ids,
            citation_style=citation_style
        )
        
        # Replace in history
        for i, response in enumerate(self.conversation_history):
            if response.response_id == response_id:
                self.conversation_history[i] = new_response
                break
        
        return new_response
    
    def export_conversation_with_attribution(self, format_type: str = "json") -> str:
        """Export conversation history with full attribution data."""
        conversation_data = {
            'conversation_id': str(id(self)),
            'total_responses': len(self.conversation_history),
            'export_timestamp': datetime.utcnow().isoformat(),
            'responses': []
        }
        
        for response in self.conversation_history:
            response_data = {
                'response_id': response.response_id,
                'response_text': response.response_text,
                'generation_timestamp': response.generation_timestamp.isoformat(),
                'confidence_score': response.confidence_score,
                'attribution_quality': response.attribution_quality.value,
                'citations': [
                    {
                        'citation_text': citation.citation_text,
                        'style': citation.style.value,
                        'source_id': citation.source_id,
                        'page_number': citation.page_number
                    }
                    for citation in response.citations
                ],
                'source_chunks': [chunk.to_dict() for chunk in response.source_chunks]
            }
            conversation_data['responses'].append(response_data)
        
        if format_type == "json":
            import json
            return json.dumps(conversation_data, indent=2)
        else:
            return str(conversation_data)
    
    def get_response_with_attribution(self, question: str, vector_db=None, workspace_id: Optional[str] = None) -> AttributedResponse:
        """Get response with attribution (synchronous wrapper)."""
        # Update vector store if provided
        if vector_db:
            self.vector_store = vector_db
        
        # Use the current settings or defaults
        citation_style = getattr(self, 'citation_style', CitationStyle.APA)
        max_sources = getattr(self, 'max_sources', 5)
        
        try:
            # Get relevant documents with similarity scores
            if hasattr(self.vector_store, 'similarity_search_with_scores'):
                relevant_docs = self.vector_store.similarity_search_with_scores(question, k=max_sources)
            else:
                # Fallback for basic similarity search
                docs = self.vector_store.similarity_search(question, k=max_sources)
                relevant_docs = [(doc, 0.8) for doc in docs]  # Default confidence
            
            # Filter by minimum confidence
            min_confidence = 0.3
            filtered_docs = [
                (doc, score) for doc, score in relevant_docs 
                if score >= min_confidence
            ]
            
            if not filtered_docs:
                # No relevant sources found
                response_text = "I couldn't find relevant information in the available documents to answer your question."
                attributed_response = AttributedResponse(
                    response_text=response_text,
                    sources=[],
                    citations=[],
                    confidence_level=ConfidenceLevel.LOW
                )
            else:
                # Track chunks and get response
                chunk_ids = []
                contexts = []
                
                for doc, similarity_score in filtered_docs:
                    # Create or update chunk metadata
                    chunk_metadata = self.attribution_manager.track_document_chunk(
                        doc_id=getattr(doc, 'metadata', {}).get('document_id', 'unknown'),
                        chunk_text=doc.page_content,
                        document_name=getattr(doc, 'metadata', {}).get('source', 'Unknown Document'),
                        file_path=getattr(doc, 'metadata', {}).get('file_path', 'unknown'),
                        page_number=getattr(doc, 'metadata', {}).get('page', None),
                        section_title=getattr(doc, 'metadata', {}).get('section', None)
                    )
                    
                    chunk_ids.append(chunk_metadata.chunk_id)
                    contexts.append(doc.page_content)
                
                # Generate response using context
                context_text = "\n\n".join(contexts)
                enhanced_query = f"""Based on the following context, please answer the question. 
                Be specific and cite relevant information.

Context:
{context_text}

Question: {question}

Answer:"""
                
                # Simple response generation (could be enhanced with actual LLM call)
                response_text = f"Based on the provided documents, here's the answer to your question: {question}\n\n" + \
                               f"The relevant information suggests: {context_text[:200]}..."
                
                # Generate citations
                citations = self.attribution_manager.generate_citations_for_chunks(chunk_ids)
                source_metadata = [self.attribution_manager.chunk_metadata[chunk_id] for chunk_id in chunk_ids]
                
                # Create attributed response
                attributed_response = AttributedResponse(
                    response_text=response_text,
                    sources=source_metadata,
                    citations=citations,
                    confidence_level=ConfidenceLevel.MEDIUM
                )
            
            # Store in conversation history
            self.conversation_history.append(attributed_response)
            
            return attributed_response
            
        except Exception as e:
            # Return error response
            error_response = AttributedResponse(
                response_text=f"Error generating response: {str(e)}",
                sources=[],
                citations=[],
                confidence_level=ConfidenceLevel.LOW
            )
            return error_response
    
    def set_citation_style(self, citation_style: CitationStyle) -> None:
        """Set the citation style for responses."""
        self.citation_style = citation_style
    
    def set_max_sources(self, max_sources: int) -> None:
        """Set the maximum number of sources to include."""
        self.max_sources = max(1, min(max_sources, 10))  # Ensure between 1 and 10

# Factory function
def create_attributed_chat_engine(chat_engine, vector_store, 
                                attribution_manager: SourceAttributionManager) -> AttributedChatEngine:
    """Factory function to create attributed chat engine."""
    return AttributedChatEngine(chat_engine, vector_store, attribution_manager)


# Global manager instance
collaborative_attributed_chat_manager = None  # Will be initialized when needed