# 📚 GenAI PDF Chatbot v2.0 - Modular Architecture with ChromaDB Support

A **production-ready**, **modular** Retrieval-Augmented Generation (RAG) chatbot built with **Streamlit** and **LangChain**. Now featuring **dual vector database support** (FAISS + ChromaDB) and a completely refactored, maintainable architecture.

## 🎯 What's New in v2.0

🔥 **Major Update**: Complete architectural overhaul with modular design and ChromaDB support!

### 🚀 New Features

- **🔄 Dual Database Support**: Toggle between FAISS and ChromaDB vector databases
- **🧩 Modular Architecture**: Clean, maintainable code structure with separated concerns
- **💬 Enhanced Chat Interface**: Professional chat UI with conversation history and export
- **⚙️ Advanced Configuration**: Centralized settings management and validation
- **📊 Real-time Statistics**: Monitor processing stats and database information
- **🛠️ Developer-Friendly**: Full type annotations, comprehensive documentation

### ⚡ Performance Improvements

- **Faster Loading**: Optimized module loading and caching
- **Better Memory Management**: Efficient resource handling
- **Smart Error Recovery**: Comprehensive error handling with user-friendly messages

## ✨ Core Features

### Document Management

- 📄 **Multiple PDF Upload**: Process multiple PDF files simultaneously
- 🔍 **Smart Validation**: Comprehensive file validation with detailed error reporting
- 📊 **Processing Statistics**: Real-time document processing metrics
- �️ **Incremental Building**: Add documents to existing knowledge base over time

### AI-Powered Chat

- 🧠 **Intelligent Q&A**: Natural language queries with context-aware responses
- 💭 **Conversation Memory**: Persistent chat history across sessions
- � **Export Conversations**: Download chat transcripts for future reference
- 🎯 **Grounded Responses**: AI answers only based on uploaded document content

### Vector Database Options

- ⚡ **FAISS**: Lightning-fast similarity search, perfect for speed-critical applications
- 🔥 **ChromaDB**: Advanced vector database with metadata support and filtering
- 🔄 **Real-time Switching**: Toggle between databases without losing data
- 💾 **Persistent Storage**: Both databases support long-term storage

## 🏗️ Architecture

### Technology Stack

- **Frontend**: Streamlit (Web UI)
- **AI Framework**: LangChain
- **Language Model**: OpenAI GPT-3.5-turbo
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Databases**: FAISS + ChromaDB (with compatibility fixes)
- **PDF Processing**: PyPDF
- **Environment Management**: python-dotenv

### RAG Pipeline

1. **Document Ingestion**: Extract text from uploaded PDFs
2. **Text Chunking**: Split documents into manageable chunks (1000 chars, 200 overlap)
3. **Vectorization**: Create embeddings using OpenAI's embedding model
4. **Storage**: Store vectors in FAISS database (memory or persistent)
5. **Retrieval**: Find relevant document chunks for user queries
6. **Generation**: Generate contextual responses using GPT model

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ installed on your system
- OpenAI API key
- Git (optional, for cloning)

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd GenAI.Chatbot.FromPDF
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

#### Create `.env` file

Create a `.env` file in the project root directory:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Set OpenAI model (default is gpt-3.5-turbo)
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Set embedding model (default is text-embedding-ada-002)
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
```

#### Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the key and paste it in your `.env` file

⚠️ **Important**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

### 5. Run the Application

#### Option A: New Modular Application (Recommended)

```bash
streamlit run app.py
```

#### Option B: Direct Main Module

```bash
streamlit run main.py
```

#### Option C: Legacy Entry Point (Compatibility)

```bash
streamlit run GenAI.Chatbot.AnsFromPDF.py
```

The application will open in your default web browser at `http://localhost:8501`

### 6. Choose Your Database

In the sidebar, select between:

- **FAISS**: Fast, lightweight vector database (recommended for most users)
- **ChromaDB**: Advanced vector database with enhanced features (for power users)

## � Compatibility & Troubleshooting

### Version Compatibility

The application includes **automatic compatibility fixes** for different LangChain and FAISS versions:

- **FAISS Compatibility**: Automatic fallback for `allow_dangerous_deserialization` parameter
- **LangChain Versions**: Supports both older and newer LangChain versions
- **Dependency Management**: Flexible requirements without strict version pinning

### Common Issues & Solutions

#### FAISS Loading Error

**Error**: `FAISS.__init__() got an unexpected keyword argument 'allow_dangerous_deserialization'`

**Solution**: The application now includes automatic compatibility handling. If you still experience issues:

```bash
pip install --upgrade langchain faiss-cpu
```

#### ChromaDB Installation Issues

**Error**: ChromaDB installation failures

**Solution**: Install ChromaDB dependencies:

```bash
pip install chromadb --upgrade
```

#### OpenAI API Errors

**Error**: API key not found or invalid

**Solution**:

1. Ensure your `.env` file contains: `OPENAI_API_KEY=your_api_key_here`
2. Verify your OpenAI API key is valid and has credits
3. Check that the `.env` file is in the project root directory

### Legacy Support

- **Full Backward Compatibility**: v1.0 functionality preserved
- **Multiple Entry Points**: Run via `app.py`, `main.py`, or legacy file
- **Data Migration**: Existing FAISS databases work without changes

## �📖 Usage Guide

### Authentication

- **Username**: `admin`
- **Password**: `password123`

### Using the Chatbot

1. **Login** with the provided credentials
2. **Choose Storage Option**:
   - **Memory only**: Temporary storage, data lost on restart
   - **Save to disk**: Persistent storage, builds cumulative knowledge base
3. **Upload PDFs**: Select one or multiple PDF files
4. **Wait for Processing**: The system will extract and index the content
5. **Ask Questions**: Type your questions about the document content
6. **Get Answers**: Receive AI-generated responses based on your documents

## 📁 Project Structure

```txt
GenAI.Chatbot.FromPDF/
├── GenAI.Chatbot.AnsFromPDF.py    # Main application file
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── venv/                          # Virtual environment (auto-created)
└── vector_db/                     # Vector database storage (auto-created)
    ├── index.faiss               # FAISS index file
    └── index.pkl                 # Metadata pickle file
```

## 🔧 Configuration Options

### Storage Modes

#### Memory-Only Storage

- Faster processing
- No disk usage
- Data lost on restart
- Suitable for one-time use

#### Persistent Storage

- Slower initial processing
- Builds cumulative knowledge base
- Data persists between sessions
- Ideal for building a permanent knowledge repository

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | GPT model to use | `gpt-3.5-turbo` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-ada-002` |

## 🛠️ Customization

### Modify Authentication

Update the `authenticate()` function in the main file to change login credentials or integrate with external auth systems.

### Adjust Chunk Settings

Modify text splitting parameters in the main function:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,    # Adjust chunk size
    chunk_overlap=200   # Adjust overlap
)
```

### Change AI Behavior

Edit the custom prompt template to modify AI responses:

```python
template="""
Your custom instructions here...
Context: {context}
Question: {question}
Answer:"""
```

## 🚨 Troubleshooting

### Common Issues

#### API Key Error

```txt
⚠️ OpenAI API key not found!
```

**Solution**: Ensure your `.env` file exists and contains a valid `OPENAI_API_KEY`.

#### Import Errors

```txt
ModuleNotFoundError: No module named 'streamlit'
```

**Solution**: Activate your virtual environment and install dependencies:

```pwsh
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### PDF Processing Issues

- Ensure PDFs are not password-protected
- Check that PDFs contain extractable text (not just images)
- Try with smaller PDF files first

#### Memory Issues

- Use "Memory only" mode for large documents
- Reduce chunk size if processing large PDFs
- Consider upgrading system RAM

## 📋 Dependencies

### Core Libraries

```txt
streamlit==1.28.0          # Web framework
langchain==0.0.335         # AI framework
openai==0.28.1             # OpenAI API client
faiss-cpu==1.7.4           # Vector database
pypdf==3.17.0              # PDF processing
python-dotenv==1.0.0       # Environment variables
tiktoken==0.5.1            # Token counting
numpy==1.24.3              # Numerical operations
pandas==2.0.3              # Data manipulation
```

## 🔐 Security Considerations

### Production Deployment

- Replace hardcoded authentication with proper user management
- Use HTTPS for secure communication
- Implement rate limiting for API calls
- Add input validation and sanitization
- Use environment-specific configuration files
- Monitor API usage and costs

### Data Privacy

- Documents are processed locally or in your chosen environment
- Vector embeddings are stored locally (if persistent storage is chosen)
- No document content is sent to third parties except OpenAI for processing

## 📚 Additional Documentation

- **[Architecture Guide](ARCHITECTURE.md)**: Detailed system architecture and module descriptions
- **[Features Documentation](FEATURES.md)**: Comprehensive feature overview and comparisons  
- **[Migration Guide](MIGRATION.md)**: Upgrade instructions from v1.0 to v2.0
- **[Troubleshooting Guide](TROUBLESHOOTING.md)**: Common issues and solutions
- **[Changelog](CHANGELOG.md)**: Version history and release notes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For issues, questions, or contributions:

- Create an issue in the repository
- Check existing documentation and troubleshooting guide
- Ensure you're using the latest version of dependencies

## 🚀 Future Enhancements

- [ ] Support for additional document formats (Word, Excel, etc.)
- [ ] Multi-language support
- [ ] Advanced authentication systems
- [ ] Document source attribution in responses
- [ ] Batch processing capabilities
- [ ] RESTful API interface
- [ ] Docker containerization
- [ ] Cloud deployment guides

---

Note* - **Built using OpenAI, LangChain, and Streamlit**
