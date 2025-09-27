"""
Document processing module for PDF handling and text extraction.
"""
import tempfile
import os
from typing import List, Optional
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config import config_manager


class DocumentProcessor:
    """Handles PDF document loading, processing, and text splitting."""
    
    def __init__(self):
        self.config = config_manager.app_config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )
    
    def load_documents(self, uploaded_files: List) -> List[Document]:
        """
        Load and extract text from uploaded PDF files.
        
        Args:
            uploaded_files (List): List of uploaded Streamlit file objects
            
        Returns:
            List[Document]: List of LangChain Document objects
            
        Raises:
            Exception: If document processing fails
        """
        if not uploaded_files:
            return []
        
        all_docs = []
        
        for uploaded_file in uploaded_files:
            try:
                docs = self._process_single_file(uploaded_file)
                all_docs.extend(docs)
                st.success(f"✅ Processed: {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ Failed to process {uploaded_file.name}: {str(e)}")
                continue
        
        return all_docs
    
    def _process_single_file(self, uploaded_file) -> List[Document]:
        """
        Process a single PDF file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            List[Document]: Extracted documents from the PDF
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        try:
            # Load PDF content
            loader = PyPDFLoader(tmp_file_path)
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata.update({
                    "source_file": uploaded_file.name,
                    "file_size": len(uploaded_file.getvalue()),
                    "processed_at": str(st.session_state.get('processing_time', 'unknown'))
                })
            
            return docs
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better processing.
        
        Args:
            documents (List[Document]): List of documents to split
            
        Returns:
            List[Document]: List of split document chunks
        """
        if not documents:
            return []
        
        try:
            split_docs = self.text_splitter.split_documents(documents)
            
            # Add chunk metadata
            for i, doc in enumerate(split_docs):
                doc.metadata.update({
                    "chunk_id": i,
                    "total_chunks": len(split_docs)
                })
            
            return split_docs
            
        except Exception as e:
            st.error(f"Error splitting documents: {str(e)}")
            return documents
    
    def get_document_stats(self, documents: List[Document]) -> dict:
        """
        Get statistics about processed documents.
        
        Args:
            documents (List[Document]): List of documents
            
        Returns:
            dict: Document statistics
        """
        if not documents:
            return {
                "total_docs": 0,
                "total_chars": 0,
                "avg_doc_length": 0,
                "sources": []
            }
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        sources = list(set(doc.metadata.get("source_file", "unknown") for doc in documents))
        
        return {
            "total_docs": len(documents),
            "total_chars": total_chars,
            "avg_doc_length": total_chars // len(documents) if documents else 0,
            "sources": sources
        }
    
    def validate_file(self, uploaded_file) -> tuple[bool, str]:
        """
        Validate uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Check file type
        if uploaded_file.type != "application/pdf":
            return False, "Only PDF files are supported"
        
        # Check file size (convert MB to bytes)
        max_size_bytes = self.config.MAX_FILE_SIZE_MB * 1024 * 1024
        if uploaded_file.size > max_size_bytes:
            return False, f"File size exceeds {self.config.MAX_FILE_SIZE_MB}MB limit"
        
        # Check if file is empty
        if uploaded_file.size == 0:
            return False, "File is empty"
        
        return True, ""
    
    def validate_files(self, uploaded_files: List) -> tuple[List, List[str]]:
        """
        Validate multiple uploaded files.
        
        Args:
            uploaded_files (List): List of uploaded files
            
        Returns:
            tuple[List, List[str]]: (valid_files, error_messages)
        """
        valid_files = []
        errors = []
        
        for file in uploaded_files:
            is_valid, error = self.validate_file(file)
            if is_valid:
                valid_files.append(file)
            else:
                errors.append(f"{file.name}: {error}")
        
        return valid_files, errors


# Global document processor instance
document_processor = DocumentProcessor()