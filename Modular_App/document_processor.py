"""
Document processing module for multi-format document handling and text extraction.
Supports PDF, Word (DOCX), Excel (XLSX), PowerPoint (PPTX), and Text files.
"""
import tempfile
import os
from typing import List, Optional, Dict, Any
import streamlit as st
from pathlib import Path

# Document loaders for different formats
from langchain.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader, 
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from .config import config_manager


class DocumentProcessor:
    """Handles multi-format document loading, processing, and text splitting."""
    
    # Supported file formats and their corresponding loaders
    SUPPORTED_FORMATS = {
        '.pdf': {'loader': PyPDFLoader, 'description': 'PDF documents'},
        '.docx': {'loader': Docx2txtLoader, 'description': 'Word documents'},
        '.xlsx': {'loader': UnstructuredExcelLoader, 'description': 'Excel spreadsheets'},
        '.pptx': {'loader': UnstructuredPowerPointLoader, 'description': 'PowerPoint presentations'},
        '.txt': {'loader': TextLoader, 'description': 'Text files'},
    }
    
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
        Process a single document file (PDF, DOCX, XLSX, PPTX, or TXT).
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            List[Document]: Extracted documents from the file
        """
        # Get file extension
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        # Validate file format
        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: {', '.join(self.SUPPORTED_FORMATS.keys())}")
        
        # Create temporary file with appropriate suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        try:
            # Get appropriate loader for the file type
            loader_class = self.SUPPORTED_FORMATS[file_extension]['loader']
            
            # Handle different loader initialization patterns
            if file_extension == '.txt':
                # TextLoader needs encoding parameter for better compatibility
                loader = loader_class(tmp_file_path, encoding='utf-8')
            else:
                loader = loader_class(tmp_file_path)
            
            # Load document content
            docs = loader.load()
            
            # Add enhanced metadata (always store original file name as 'original_file_name')
            for doc in docs:
                doc.metadata.update({
                    "source_file": uploaded_file.name,
                    "original_file_name": uploaded_file.name,
                    "file_type": file_extension,
                    "file_description": self.SUPPORTED_FORMATS[file_extension]['description'],
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
        Split documents into smaller chunks for better processing, and force all chunks to use the original uploaded file name for all relevant metadata fields.
        Args:
            documents (List[Document]): List of documents to split
        Returns:
            List[Document]: List of split document chunks
        """
        if not documents:
            return []
        try:
            split_docs = self.text_splitter.split_documents(documents)
            for i, doc in enumerate(split_docs):
                # Find the original file name from the parent doc (if present)
                original_file_name = doc.metadata.get('original_file_name') or doc.metadata.get('source_file') or doc.metadata.get('source') or doc.metadata.get('document_name')
                # Overwrite all relevant fields to ensure temp file name is never used
                doc.metadata.update({
                    "chunk_id": i,
                    "total_chunks": len(split_docs),
                    "source": original_file_name,
                    "source_file": original_file_name,
                    "document_name": original_file_name,
                    "original_file_name": original_file_name
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
    
    @classmethod
    def get_supported_formats(cls) -> Dict[str, str]:
        """
        Get dictionary of supported file formats and their descriptions.
        
        Returns:
            Dict[str, str]: Format extensions mapped to descriptions
        """
        return {ext: info['description'] for ext, info in cls.SUPPORTED_FORMATS.items()}
    
    @classmethod
    def is_supported_format(cls, filename: str) -> bool:
        """
        Check if a file format is supported.
        
        Args:
            filename (str): Name of the file to check
            
        Returns:
            bool: True if format is supported
        """
        file_extension = Path(filename).suffix.lower()
        return file_extension in cls.SUPPORTED_FORMATS
    
    def get_format_description(self, filename: str) -> str:
        """
        Get description for a file format.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            str: Description of the file format
        """
        file_extension = Path(filename).suffix.lower()
        if file_extension in self.SUPPORTED_FORMATS:
            return self.SUPPORTED_FORMATS[file_extension]['description']
        return f"Unsupported format: {file_extension}"

    def validate_file(self, uploaded_file) -> tuple[bool, str]:
        """
        Validate uploaded file for format and size constraints.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Check file format
        if not self.is_supported_format(uploaded_file.name):
            supported = ', '.join(self.SUPPORTED_FORMATS.keys())
            return False, f"Unsupported format. Supported formats: {supported}"
        
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