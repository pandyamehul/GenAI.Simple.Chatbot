"""
Document Source Attribution System
Provides source tracking and citation generation for the GenAI platform.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class CitationStyle(Enum):
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"


class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ChunkMetadata:
    source_file: str  # Always the original uploaded file name
    page_number: Optional[int] = None
    section: Optional[str] = None
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    document_id: Optional[str] = None
    confidence_score: float = 1.0
    extraction_method: str = "default"
    extraction_timestamp: datetime = field(default_factory=datetime.utcnow)
    word_count: int = 0
    character_count: int = 0
    text_content: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert ChunkMetadata to dictionary format, always including 'document_name' and 'text_content' for UI compatibility."""
        return {
            'source_file': self.source_file,
            'document_name': self.source_file,  # Always the original file name
            'page_number': self.page_number,
            'section': self.section,
            'chunk_id': self.chunk_id,
            'created_at': self.created_at.isoformat(),
            'document_id': self.document_id,
            'confidence_score': self.confidence_score,
            'extraction_method': self.extraction_method,
            'extraction_timestamp': self.extraction_timestamp.isoformat(),
            'word_count': self.word_count,
            'character_count': self.character_count,
            'text_content': self.text_content
        }


@dataclass  
class Citation:
    citation_id: str
    source_file: str
    citation_text: str
    style: CitationStyle
    page_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Citation to dictionary format, always including 'source_reference' for UI compatibility."""
        return {
            'citation_id': self.citation_id,
            'source_file': self.source_file,
            'citation_text': self.citation_text,
            'source_reference': self.citation_text,  # For UI compatibility
            'style': self.style.value,  # Convert enum to string
            'page_number': self.page_number
        }


@dataclass
class AttributedResponse:
    """Response with source attribution information."""
    response_text: str
    sources: List[ChunkMetadata]
    citations: List[Citation]
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    overall_confidence: float = 0.0
    generated_at: datetime = field(default_factory=datetime.utcnow)
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class SourceAttributionManager:
    def __init__(self):
        self.chunk_metadata: Dict[str, ChunkMetadata] = {}
        self.citations: Dict[str, Citation] = {}
        
    def add_chunk(self, chunk_id: str, metadata: ChunkMetadata):
        metadata.chunk_id = chunk_id
        self.chunk_metadata[chunk_id] = metadata
    
    def generate_citations_for_chunks(self, chunk_ids: List[str]) -> List[Citation]:
        citations = []
        for chunk_id in chunk_ids:
            metadata = self.chunk_metadata.get(chunk_id)
            if metadata:
                # Always use original_file_name if present in metadata
                original_file_name = getattr(metadata, 'original_file_name', None) or getattr(metadata, 'source_file', None)
                citation = Citation(
                    citation_id=str(uuid.uuid4()),
                    source_file=original_file_name,
                    citation_text=f"Source: {original_file_name}",
                    style=CitationStyle.APA,
                    page_number=metadata.page_number
                )
                citations.append(citation)
        return citations
    
    def export_attribution_data(self) -> Dict[str, Any]:
        """Export all attribution data for analysis or backup."""
        return {
            "chunk_metadata": {
                chunk_id: {
                    "source_file": metadata.source_file,
                    "page_number": metadata.page_number,
                    "section": metadata.section,
                    "chunk_id": metadata.chunk_id,
                    "created_at": metadata.created_at.isoformat()
                }
                for chunk_id, metadata in self.chunk_metadata.items()
            },
            "citations": {
                citation_id: {
                    "citation_id": citation.citation_id,
                    "source_file": citation.source_file,
                    "citation_text": citation.citation_text,
                    "style": citation.style.value,
                    "page_number": citation.page_number
                }
                for citation_id, citation in self.citations.items()
            },
            "export_timestamp": datetime.utcnow().isoformat(),
            "total_chunks": len(self.chunk_metadata),
            "total_citations": len(self.citations)
        }
    
    def generate_document_id(self, source_file: str) -> str:
        """Generate a unique document ID for a source file."""
        import hashlib
        # Create a hash-based ID using the source file path and timestamp
        file_hash = hashlib.md5(source_file.encode()).hexdigest()[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"doc_{file_hash}_{timestamp}"
    
    def track_document_chunk(self, doc_id: str, chunk_text: str, 
                           document_name: str, file_path: str,
                           page_number: Optional[int] = None, 
                           section_title: Optional[str] = None,
                           extraction_method: str = "default") -> ChunkMetadata:
        """Track a document chunk and return its metadata."""
        chunk_id = str(uuid.uuid4())
        
        # Calculate text statistics
        word_count = len(chunk_text.split()) if chunk_text else 0
        character_count = len(chunk_text) if chunk_text else 0
        
        metadata = ChunkMetadata(
            source_file=document_name,
            page_number=page_number,
            section=section_title,
            chunk_id=chunk_id,
            document_id=doc_id,
            extraction_method=extraction_method,
            word_count=word_count,
            character_count=character_count,
            text_content=chunk_text
        )
        self.add_chunk(chunk_id, metadata)
        return metadata
    
    def update_chunk_confidence(self, chunk_id: str, confidence_score: float) -> None:
        """Update the confidence score for a specific chunk."""
        if chunk_id in self.chunk_metadata:
            self.chunk_metadata[chunk_id].confidence_score = confidence_score
    
    def create_attributed_response(self, response_text: str, source_chunk_ids: List[str], 
                                 citation_style: CitationStyle = CitationStyle.APA) -> 'AttributedResponse':
        """Create an attributed response with citations and source metadata."""
        # Get source metadata for the chunks
        sources = [self.chunk_metadata[chunk_id] for chunk_id in source_chunk_ids if chunk_id in self.chunk_metadata]
        
        # Generate citations
        citations = self.generate_citations_for_chunks(source_chunk_ids)
        
        # Calculate overall confidence
        if sources:
            avg_confidence = sum(source.confidence_score for source in sources) / len(sources)
            if avg_confidence >= 0.8:
                confidence_level = ConfidenceLevel.HIGH
            elif avg_confidence >= 0.6:
                confidence_level = ConfidenceLevel.MEDIUM
            else:
                confidence_level = ConfidenceLevel.LOW
        else:
            avg_confidence = 0.0
            confidence_level = ConfidenceLevel.LOW
        
        return AttributedResponse(
            response_text=response_text,
            sources=sources,
            citations=citations,
            confidence_level=confidence_level,
            overall_confidence=avg_confidence
        )
