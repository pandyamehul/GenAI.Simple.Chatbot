"""
GenAI PDF Chatbot - Legacy Entry Point

This file is kept for backward compatibility.
The application has been refactored into a modular structure.
Use main.py for the new modular version.
"""

# Import the new modular application
# from main import mainssary libraries and modules
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Load and Process PDFs ---
def load_documents(uploaded_files):
    all_docs = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()
        all_docs.extend(docs)
        os.remove(tmp_file_path)
    return all_docs

# --- Basic Authentication ---
def authenticate():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if username == "admin" and password == "password123":
        return True
    else:
        st.sidebar.warning("Enter valid credentials")
        return False

# --- Main App ---
def main():
    st.title("📚 Gen AI Chatbot with PDF Knowledge Base")

    if not authenticate():
        st.stop()

    # Sidebar for knowledge base management
    st.sidebar.header("📚 Knowledge Base Management")
    
    # Check if existing vector database exists
    vector_db_dir = "vector_db"
    vector_db_path = os.path.join(vector_db_dir, "faiss_index")
    has_existing_db = os.path.exists(vector_db_path)

    # Initialize OpenAI components with API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("⚠️ OpenAI API key not found! Please set OPENAI_API_KEY in your .env file")
        st.stop()
    
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Sidebar - Display existing database status and management options
    if has_existing_db:
        st.sidebar.success("✅ Knowledge base available")
        
        # Show basic stats if we can load the database
        try:
            temp_embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
            temp_db = FAISS.load_local(vector_db_path, temp_embeddings)
            if hasattr(temp_db, 'index') and temp_db.index is not None:
                doc_count = temp_db.index.ntotal
                st.sidebar.metric("📄 Document Chunks", doc_count)
        except:
            st.sidebar.info("📊 Stats unavailable")
        
        # Knowledge base management in sidebar
        if st.sidebar.button("🗑️ Delete Knowledge Base", help="Permanently delete the stored knowledge base"):
            if os.path.exists(vector_db_path):
                import shutil
                shutil.rmtree(vector_db_dir)
                st.sidebar.success("Knowledge base deleted!")
                st.experimental_rerun()
    else:
        st.sidebar.info("📂 No knowledge base found")
    
    # Main area - Display status and options
    if has_existing_db:
        st.success("🗃️ Existing knowledge base found! You can chat directly or add more documents.")
        
        # Option to use existing database or add new documents
        action_choice = st.radio(
            "Choose an action:",
            ("💬 Chat with existing knowledge base", "📚 Add new PDFs to knowledge base", "🆕 Start fresh (replace existing data)"),
            help="You can chat with existing documents or add more PDFs to expand the knowledge base."
        )
    else:
        st.info("📂 No existing knowledge base found. Please upload PDF files to get started.")
        action_choice = "📚 Add new PDFs to knowledge base"

    # Handle file upload based on user choice
    if action_choice == "💬 Chat with existing knowledge base":
        # Load existing database without requiring new uploads
        st.info("Loading existing knowledge base...")
        db = FAISS.load_local(vector_db_path, embeddings)
        st.success("✅ Knowledge base loaded successfully!")
        uploaded_files = None  # No new files needed
        
    elif action_choice == "🆕 Start fresh (replace existing data)":
        # User wants to replace existing data
        st.warning("⚠️ This will replace your existing knowledge base!")
        uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
        
    else:  # Add new PDFs to knowledge base
        uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

    # Storage option selection (only show if uploading new files)
    if action_choice != "💬 Chat with existing knowledge base":
        storage_option = st.radio(
            "Choose storage option:",
            ("Memory only (temporary)", "Save to disk (persistent)"),
            help="Memory only: Data lost when app restarts. Save to disk: Data persists between sessions.",
            index=1 if has_existing_db else 0  # Default to persistent if DB exists
        )
    else:
        storage_option = "Save to disk (persistent)"  # Always persistent when using existing DB

    # Process uploaded files or use existing database
    if uploaded_files or action_choice == "💬 Chat with existing knowledge base":
        
        # Only process new files if they were uploaded
        if uploaded_files and action_choice != "💬 Chat with existing knowledge base":
            st.success("PDFs uploaded successfully. Processing...")
            documents = load_documents(uploaded_files)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            docs = text_splitter.split_documents(documents)
        else:
            docs = []  # No new documents to process
        
        # Handle vector database creation/loading based on user choice
        if action_choice == "💬 Chat with existing knowledge base":
            # Database already loaded above, no additional processing needed
            pass
            
        elif storage_option == "Save to disk (persistent)":
            # Create a directory for storing vector database
            os.makedirs(vector_db_dir, exist_ok=True)
            
            if action_choice == "🆕 Start fresh (replace existing data)":
                # Replace existing database
                if docs:
                    st.info("Creating new vector database (replacing existing)...")
                    db = FAISS.from_documents(docs, embeddings)
                    db.save_local(vector_db_path)
                    st.success("✅ New knowledge base created!")
                else:
                    st.warning("Please upload PDF files to create a new knowledge base.")
                    st.stop()
            else:
                # Add to existing or create new
                if has_existing_db and docs:
                    st.info("Adding new documents to existing knowledge base...")
                    db = FAISS.load_local(vector_db_path, embeddings)
                    new_db = FAISS.from_documents(docs, embeddings)
                    db.merge_from(new_db)
                    st.success("✅ New documents added to existing knowledge base!")
                elif docs:
                    st.info("Creating new vector database...")
                    db = FAISS.from_documents(docs, embeddings)
                    st.success("✅ New knowledge base created!")
                else:
                    st.warning("Please upload PDF files to add to the knowledge base.")
                    st.stop()
                
                # Save the updated database to disk
                db.save_local(vector_db_path)
                
        else:
            # Memory-only storage (original behavior)
            if docs:
                st.info("Creating vector database in memory...")
                db = FAISS.from_documents(docs, embeddings)
                st.success("✅ Vector database created in memory (temporary)!")
            else:
                st.warning("Please upload PDF files for memory-only mode.")
                st.stop()

        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # ✅ Fixed prompt template with proper variables for ConversationalRetrievalChain
        custom_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
                You are Gen AI, a helpful assistant that answers questions based on the uploaded PDF documents.
                Use the following pieces of context to answer the question at the end.
                If the answer is not in the documents, respond with "I don't know".
                Be concise and to the point.

                Context: {context}
                Question: {question}

                Answer:"""
        )

        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(openai_api_key=openai_api_key, model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")),
            retriever=db.as_retriever(),
            memory=memory,
            combine_docs_chain_kwargs={"prompt": custom_prompt}
        )

        # Display knowledge base info
        if hasattr(db, 'index') and db.index is not None:
            doc_count = db.index.ntotal
            st.info(f"📊 Knowledge base contains {doc_count} document chunks")
        
        st.subheader("💬 Ask a question about your documents")
        user_question = st.text_input("Your question:", placeholder="What would you like to know about your documents?")
        
        if user_question:
            with st.spinner("🤔 Thinking..."):
                response = qa_chain.run(user_question)
            st.write("**Answer:**", response)
            
        # Add some helpful tips
        with st.expander("💡 Tips for better results"):
            st.write("""
            - Be specific in your questions
            - Ask about topics covered in your uploaded documents
            - Try rephrasing if you don't get the expected answer
            - The AI will only answer based on document content
            """)

if __name__ == "__main__":
    main()

