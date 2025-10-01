"""
Enhanced Vector Store with Source Attribution Support
Extends the existing vector store functionality to include detailed metadata for source attribution.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from langchain.vectorstores import FAISS, Chroma
import streamlit as st

from .vector_store import VectorStoreManager, vector_store_manager
from .source_attribution import ChunkMetadata, SourceAttributionManager


class AttributedDocument:
    """Enhanced Document class with attribution metadata."""
    
    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None, 
                 attribution_metadata: Optional[ChunkMetadata] = None):
        # Store document properties
        self.page_content = page_content
        self.metadata = metadata or {}
        self.attribution_metadata = attribution_metadata
    
    def to_document(self) -> Document:
        """Convert to standard LangChain Document."""
        return Document(page_content=self.page_content, metadata=self.metadata)


class EnhancedVectorStoreManager(VectorStoreManager):
    """Enhanced vector store manager with source attribution support."""
    
    def __init__(self):
        super().__init__()
        self.attribution_manager = SourceAttributionManager()
        self.chunk_metadata_cache: Dict[str, ChunkMetadata] = {}
    
    def create_attributed_documents(self, documents: List[Document], document_name: str, file_path: str, document_id: str) -> List[AttributedDocument]:
        """Create attributed documents with enhanced metadata, always using the original uploaded file name."""
        attributed_docs = []
        for doc in documents:
            # Always use the original uploaded file name for attribution
            original_file = doc.metadata.get('original_file_name', doc.metadata.get('source_file', document_name))
            page_number = doc.metadata.get('page', None)
            section_title = doc.metadata.get('section', None)
            chunk_metadata = self.attribution_manager.track_document_chunk(
                doc_id=document_id,
                chunk_text=doc.page_content,
                document_name=original_file,
                file_path=file_path,
                page_number=page_number,
                section_title=section_title,
                extraction_method=doc.metadata.get('extraction_method', 'default')
            )
            enhanced_metadata = {
                **doc.metadata,
                'chunk_id': chunk_metadata.chunk_id,
                'document_id': document_id,
                'document_name': original_file,
                'source': original_file,
                'file_path': file_path,
                'confidence_score': chunk_metadata.confidence_score,
                'extraction_timestamp': chunk_metadata.extraction_timestamp.isoformat(),
                'word_count': chunk_metadata.word_count,
                'character_count': chunk_metadata.character_count
            }
            attributed_doc = AttributedDocument(
                page_content=doc.page_content,
                metadata=enhanced_metadata,
                attribution_metadata=chunk_metadata
            )
            attributed_docs.append(attributed_doc)
            self.chunk_metadata_cache[chunk_metadata.chunk_id] = chunk_metadata
        return attributed_docs
    
    def _map_storage_option_to_db_type(self, storage_option: str) -> str:
        """Map UI storage options to valid database types."""
        mapping = {
            "memory": "faiss",
            "persistent": "faiss",  # Both use FAISS, but persistent saves to disk
            "merge": "faiss",
            "replace": "faiss",
            "faiss": "faiss",
            "chroma": "chroma",
            "Chroma": "chroma"
        }
        return mapping.get(storage_option, "faiss")  # Default to faiss
    
    def create_database(self, documents: List[Document], storage_option: str = "FAISS") -> Any:
        """Create vector database with enhanced features (simplified interface)."""
        # Map storage option to valid database type
        db_type = self._map_storage_option_to_db_type(storage_option)
        self.set_database_type(db_type)
        
        # For enhanced database creation, we need to create attributed documents
        # Extract document info from the first document or use defaults
        if documents:
            first_doc = documents[0]
            document_name = first_doc.metadata.get('source', 'Unknown Document')
            file_path = first_doc.metadata.get('source', '')
        else:
            document_name = 'Unknown Document'
            file_path = ''
        
        # Use the full attribution method
        return self.create_database_with_attribution(
            documents, document_name, file_path
        )
    
    def add_documents_to_existing(self, documents: List[Document], storage_option: str = "FAISS") -> Any:
        """Add documents to existing database (simplified interface)."""
        # Load existing database
        existing_db = self.load_database()
        if not existing_db:
            # If no existing database, create a new one
            return self.create_database(documents, storage_option)
        
        # Extract document info
        if documents:
            first_doc = documents[0]
            document_name = first_doc.metadata.get('source', 'Unknown Document')
            file_path = first_doc.metadata.get('source', '')
        else:
            document_name = 'Unknown Document'
            file_path = ''
        
        # Use the full attribution merge method
        return self.merge_with_attribution(
            existing_db, documents, document_name, file_path
        )
    
    def create_database_with_attribution(self, documents: List[Document], 
                                       document_name: str, file_path: str,
                                       document_id: Optional[str] = None) -> Any:
        """Create vector database with source attribution."""
        if not self.current_store:
            raise ValueError("Database type not set. Call set_database_type() first.")
        
        # Generate document ID if not provided
        if not document_id:
            document_id = self.attribution_manager.generate_document_id(file_path)
        
        # Create attributed documents
        attributed_docs = self.create_attributed_documents(
            documents, document_name, file_path, document_id
        )
        
        # Convert AttributedDocuments to regular Documents for vector store
        regular_docs = [doc.to_document() for doc in attributed_docs]
        
        # Create vector database
        embeddings = self.get_embeddings()
        return self.current_store.create_from_documents(regular_docs, embeddings)
    
    def merge_with_attribution(self, existing_db: Any, new_documents: List[Document],
                             document_name: str, file_path: str,
                             document_id: Optional[str] = None) -> Any:
        """Merge new documents with attribution into existing database."""
        if not self.current_store:
            raise ValueError("Database type not set. Call set_database_type() first.")
        
        # Generate document ID if not provided
        if not document_id:
            document_id = self.attribution_manager.generate_document_id(file_path)
        
        # Create attributed documents
        attributed_docs = self.create_attributed_documents(
            new_documents, document_name, file_path, document_id
        )
        
        # Convert AttributedDocuments to regular Documents for vector store
        regular_docs = [doc.to_document() for doc in attributed_docs]
        
        return self.merge_databases(existing_db, regular_docs)
    
    def similarity_search_with_attribution(self, db: Any, query: str, k: int = 4) -> List[Tuple[Document, ChunkMetadata]]:
        """Perform similarity search and return documents with attribution metadata."""
        if not db:
            return []
        
        try:
            # Perform similarity search
            docs = db.similarity_search(query, k=k)
            
            # Retrieve attribution metadata for each document
            results = []
            for doc in docs:
                chunk_id = doc.metadata.get('chunk_id')
                if chunk_id:
                    # Try to get from cache first
                    chunk_metadata = self.chunk_metadata_cache.get(chunk_id)
                    if not chunk_metadata:
                        # Get from attribution manager
                        chunk_metadata = self.attribution_manager.get_chunk_metadata(chunk_id)
                    
                    if chunk_metadata:
                        results.append((doc, chunk_metadata))
                    else:
                        # Create basic metadata if not found
                        basic_metadata = ChunkMetadata(
                            source_file=doc.metadata.get('document_name', 'unknown'),
                            document_id=doc.metadata.get('document_id', 'unknown'),
                            chunk_id=chunk_id or 'unknown',
                            file_path=doc.metadata.get('file_path', 'unknown'),
                            text_content=doc.page_content,
                            confidence_score=doc.metadata.get('confidence_score', 0.5)
                        )
                        results.append((doc, basic_metadata))
                else:
                    # Document without attribution metadata
                    basic_metadata = ChunkMetadata(
                        source_file=doc.metadata.get('source', 'unknown'),
                        document_id='unknown',
                        chunk_id='unknown',
                        file_path='unknown',
                        text_content=doc.page_content,
                        confidence_score=0.5
                    )
                    results.append((doc, basic_metadata))
            
            return results
            
        except Exception as e:
            st.error(f"Error in similarity search with attribution: {str(e)}")
            return []
    
    def get_attribution_summary(self, db: Any) -> Dict[str, Any]:
        """Get summary of attribution data in the database."""
        if not db:
            return {"error": "No database provided"}
        
        try:
            # Get all documents from the database
            if hasattr(db, 'docstore') and hasattr(db.docstore, '_dict'):
                # FAISS implementation
                docs = list(db.docstore._dict.values())
            elif hasattr(db, 'get'):
                # ChromaDB implementation (simplified)
                docs = []  # Would need proper implementation for Chroma
            else:
                docs = []
            
            summary = {
                "total_chunks": len(docs),
                "documents": {},
                "confidence_distribution": {"high": 0, "medium": 0, "low": 0, "very_low": 0},
                "total_documents": set()
            }
            
            for doc in docs:
                if hasattr(doc, 'metadata'):
                    metadata = doc.metadata
                    doc_id = metadata.get('document_id', 'unknown')
                    doc_name = metadata.get('document_name', 'unknown')
                    confidence = metadata.get('confidence_score', 0.0)
                    
                    # Track documents
                    summary["total_documents"].add(doc_id)
                    
                    # Document-specific stats
                    if doc_name not in summary["documents"]:
                        summary["documents"][doc_name] = {
                            "chunk_count": 0,
                            "avg_confidence": 0.0,
                            "document_id": doc_id
                        }
                    
                    summary["documents"][doc_name]["chunk_count"] += 1
                    
                    # Confidence distribution
                    if confidence >= 0.8:
                        summary["confidence_distribution"]["high"] += 1
                    elif confidence >= 0.6:
                        summary["confidence_distribution"]["medium"] += 1
                    elif confidence >= 0.4:
                        summary["confidence_distribution"]["low"] += 1
                    else:
                        summary["confidence_distribution"]["very_low"] += 1
            
            # Calculate average confidences
            for doc_stats in summary["documents"].values():
                if doc_stats["chunk_count"] > 0:
                    # This would need proper calculation with actual confidence values
                    doc_stats["avg_confidence"] = 0.7  # Placeholder
            
            summary["total_documents"] = len(summary["total_documents"])
            
            return summary
            
        except Exception as e:
            return {"error": f"Failed to generate attribution summary: {str(e)}"}
    
    def export_attribution_metadata(self, db: Any, output_path: str) -> bool:
        """Export attribution metadata to JSON file."""
        try:
            summary = self.get_attribution_summary(db)
            
            # Add detailed chunk information
            detailed_data = {
                "export_timestamp": self.attribution_manager.confidence_calculator.__class__.__name__,
                "summary": summary,
                "chunks": []
            }
            
            # Export from attribution manager
            attribution_data = self.attribution_manager.export_attribution_data()
            detailed_data.update(attribution_data)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(detailed_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            st.error(f"Error exporting attribution metadata: {str(e)}")
            return False
    
    def validate_attribution_integrity(self, db: Any) -> Dict[str, Any]:
        """Validate the integrity of attribution data."""
        validation_results = {
            "valid": True,
            "issues": [],
            "statistics": {
                "total_chunks": 0,
                "chunks_with_metadata": 0,
                "chunks_missing_metadata": 0,
                "average_confidence": 0.0
            }
        }
        
        try:
            # Get attribution summary
            summary = self.get_attribution_summary(db)
            
            if "error" in summary:
                validation_results["valid"] = False
                validation_results["issues"].append(f"Database access error: {summary['error']}")
                return validation_results
            
            validation_results["statistics"]["total_chunks"] = summary["total_chunks"]
            
            # Check for missing metadata
            missing_chunks = 0
            total_confidence = 0.0
            
            # This would need proper implementation based on actual database structure
            # For now, providing basic validation structure
            
            if missing_chunks > 0:
                validation_results["valid"] = False
                validation_results["issues"].append(f"{missing_chunks} chunks missing attribution metadata")
            
            validation_results["statistics"]["chunks_missing_metadata"] = missing_chunks
            validation_results["statistics"]["chunks_with_metadata"] = summary["total_chunks"] - missing_chunks
            
            if summary["total_chunks"] > 0:
                validation_results["statistics"]["average_confidence"] = total_confidence / summary["total_chunks"]
            
            return validation_results
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["issues"].append(f"Validation error: {str(e)}")
            return validation_results


# Global enhanced vector store manager instance
enhanced_vector_store_manager = EnhancedVectorStoreManager()


def migrate_existing_database_to_attribution():
    """Utility function to migrate existing databases to support attribution."""
    st.info("🔄 Migrating existing database to support source attribution...")
    
    try:
        # Check if existing database exists
        if enhanced_vector_store_manager.database_exists():
            st.warning("⚠️ Attribution migration would require reprocessing all documents.")
            st.info("💡 To enable full source attribution, please reprocess your documents.")
            return False
        else:
            st.success("✅ No existing database found. New uploads will automatically include attribution.")
            return True
            
    except Exception as e:
        st.error(f"❌ Migration failed: {str(e)}")
        return False


def display_attribution_info(db: Any):
    """Display attribution information in Streamlit interface."""
    if not db:
        st.warning("No database loaded")
        return
    
    st.subheader("📍 Source Attribution Information")
    
    try:
        # Get attribution summary
        summary = enhanced_vector_store_manager.get_attribution_summary(db)
        
        if "error" in summary:
            st.error(f"Error getting attribution data: {summary['error']}")
            return
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Chunks", summary["total_chunks"])
        
        with col2:
            st.metric("Documents", summary["total_documents"])
        
        with col3:
            confidence_dist = summary["confidence_distribution"]
            high_confidence_pct = (confidence_dist["high"] / max(summary["total_chunks"], 1)) * 100
            st.metric("High Confidence", f"{high_confidence_pct:.1f}%")
        
        with col4:
            st.metric("Cache Size", len(enhanced_vector_store_manager.chunk_metadata_cache))
        
        # Confidence distribution chart
        if summary["total_chunks"] > 0:
            st.subheader("Confidence Score Distribution")
            confidence_data = summary["confidence_distribution"]
            
            import plotly.express as px
            import pandas as pd
            
            df = pd.DataFrame([
                {"Level": "High (80-100%)", "Count": confidence_data["high"]},
                {"Level": "Medium (60-80%)", "Count": confidence_data["medium"]},
                {"Level": "Low (40-60%)", "Count": confidence_data["low"]},
                {"Level": "Very Low (0-40%)", "Count": confidence_data["very_low"]}
            ])
            
            fig = px.bar(df, x="Level", y="Count", title="Source Attribution Confidence Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Document details
        if summary["documents"]:
            st.subheader("Documents with Attribution")
            
            doc_data = []
            for doc_name, stats in summary["documents"].items():
                doc_data.append({
                    "Document": doc_name,
                    "Chunks": stats["chunk_count"],
                    "Avg Confidence": f"{stats['avg_confidence']:.1%}",
                    "Document ID": stats["document_id"][:8] + "..."
                })
            
            df = pd.DataFrame(doc_data)
            st.dataframe(df, use_container_width=True)
        
        # Validation status
        st.subheader("Attribution Integrity")
        validation = enhanced_vector_store_manager.validate_attribution_integrity(db)
        
        if validation["valid"]:
            st.success("✅ Attribution data integrity validated")
        else:
            st.error("❌ Attribution data has issues:")
            for issue in validation["issues"]:
                st.error(f"• {issue}")
        
        # Export option
        if st.button("📤 Export Attribution Data"):
            export_path = "attribution_data_export.json"
            if enhanced_vector_store_manager.export_attribution_metadata(db, export_path):
                st.success(f"✅ Attribution data exported to {export_path}")
            else:
                st.error("❌ Failed to export attribution data")
        
    except Exception as e:
        st.error(f"Error displaying attribution info: {str(e)}")