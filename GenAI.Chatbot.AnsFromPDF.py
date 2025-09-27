# Import necessary libraries and modules
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

    # Storage option selection
    storage_option = st.radio(
        "Choose storage option:",
        ("Memory only (temporary)", "Save to disk (persistent)"),
        help="Memory only: Data lost when app restarts. Save to disk: Data persists between sessions."
    )
    
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        st.success("PDFs uploaded successfully. Processing...")

        documents = load_documents(uploaded_files)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)

        # Initialize OpenAI components with API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            st.error("⚠️ OpenAI API key not found! Please set OPENAI_API_KEY in your .env file")
            st.stop()
        
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        if storage_option == "Save to disk (persistent)":
            # Create a directory for storing vector database
            vector_db_dir = "vector_db"
            os.makedirs(vector_db_dir, exist_ok=True)
            vector_db_path = os.path.join(vector_db_dir, "faiss_index")
            
            # Check if saved vector database exists
            if os.path.exists(vector_db_path):
                st.info("Loading existing vector database from disk...")
                db = FAISS.load_local(vector_db_path, embeddings)
                # Add new documents to existing database
                new_db = FAISS.from_documents(docs, embeddings)
                db.merge_from(new_db)
                st.success("New documents added to existing database!")
            else:
                st.info("Creating new vector database...")
                db = FAISS.from_documents(docs, embeddings)
            
            # Save the updated database to disk
            db.save_local(vector_db_path)
            st.success("Vector database saved to disk!")
        else:
            # Memory-only storage (original behavior)
            st.info("Creating vector database in memory...")
            db = FAISS.from_documents(docs, embeddings)
            st.success("Vector database created in memory (temporary)!")

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

        st.subheader("Ask a question about your PDFs")
        user_question = st.text_input("Your question:")
        if user_question:
            response = qa_chain.run(user_question)
            st.write("**Answer:**", response)

if __name__ == "__main__":
    main()

