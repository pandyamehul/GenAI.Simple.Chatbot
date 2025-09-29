# � GenAI Enterprise Document Intelligence v3.0 - Multi-Format, Multi-Language, Multi-Provider Platform

A **revolutionary enterprise-grade** document intelligence platform that has evolved from a simple PDF chatbot into a **comprehensive multi-format, multi-language, multi-AI provider system** with **secure REST API** and **JWT authentication**. Built with **FastAPI**, **Streamlit**, and **LangChain** for maximum scalability and security.

## 🎯 What's New in v3.0

🔥 **Enterprise Transformation**: Complete evolution into a multi-format, multi-language, multi-provider document intelligence platform!

### 🌟 Revolutionary Features

- **� Universal Document Support**: PDF, Word (.docx), Excel (.xlsx), PowerPoint (.pptx), and text files
- **🌍 12-Language Intelligence**: English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Hindi
- **🤖 Multi-AI Provider Ecosystem**: OpenAI, Anthropic Claude, Google AI, and local models
- **🔐 Enterprise Security**: JWT authentication with 24-hour token expiry and secure API access
- **🔌 Production REST API**: FastAPI server with comprehensive endpoints and interactive documentation
- **� Dual Interface**: Simultaneous Web UI (Streamlit) and REST API access

### 🔒 Security & Authentication

- **JWT Token System**: Industry-standard JSON Web Token authentication
- **Bearer Token Security**: Secure API access with Authorization headers
- **User Management**: Built-in admin and user role authentication
- **Environment Security**: Configurable secret keys and secure token validation
- **CORS Protection**: Secure cross-origin resource sharing configuration

## ✨ Core Enterprise Features

### Document Management

- 📄 **Multi-Format Support**: Process PDF, Word, Excel, PowerPoint, and text files
- 🔍 **Smart Validation**: Comprehensive file validation with detailed error reporting
- 📊 **Processing Statistics**: Real-time document processing metrics
- ⚒️ **Incremental Building**: Add documents to existing knowledge base over time
- 🌍 **Language Detection**: Automatic detection of document languages (12+ supported)

### AI-Powered Chat

- 🧠 **Intelligent Q&A**: Natural language queries with context-aware responses
- 💭 **Conversation Memory**: Persistent chat history across sessions
- 📥 **Export Conversations**: Download chat transcripts for future reference
- 🎯 **Grounded Responses**: AI answers only based on uploaded document content
- 🤖 **Multi-Model Support**: Choose from OpenAI, Anthropic, Google AI, or local models

### Vector Database Options

- ⚡ **FAISS**: Lightning-fast similarity search, perfect for speed-critical applications
- 🔥 **ChromaDB**: Advanced vector database with metadata support and filtering
- 🔄 **Real-time Switching**: Toggle between databases without losing data
- 💾 **Persistent Storage**: Both databases support long-term storage

### 🔌 Enterprise REST API

- **FastAPI Backend**: High-performance async API server with comprehensive endpoints
- **JWT Authentication**: Secure bearer token system with 24-hour expiry
- **Interactive Documentation**: OpenAPI docs at `http://localhost:8000/docs`
- **Multi-Session Support**: Concurrent conversation management for multiple users
- **Comprehensive Endpoints**: Document upload, chat, authentication, configuration, health monitoring

#### 🔐 API Authentication

1. **Get Access Token**:

   ```bash
   curl -X POST "http://localhost:8000/auth/token" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password123"}'
   ```

2. **Use Token for API Calls**:

   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/status"
   ```

#### 📡 Key Endpoints

- `POST /auth/token` - Authenticate and get JWT token
- `POST /upload` - Upload multi-format documents
- `POST /chat` - Chat with documents (session-based)
- `GET /status` - System health and configuration
- `GET /docs` - Interactive API documentation

### 🌐 Dual Interface Support

## 🏗️ Architecture

### Technology Stack

- **Frontend**: Streamlit (Web UI)
- **Backend API**: FastAPI (REST API)
- **AI Framework**: LangChain
- **Language Models**:
  - OpenAI (GPT-3.5, GPT-4, GPT-4 Turbo)
  - Anthropic (Claude 3 Haiku, Sonnet, Opus)
  - Google AI (Gemini Pro, Gemini Pro Vision)
  - Local Models (Ollama)
- **Embeddings**: OpenAI text-embedding-ada-002, multilingual models
- **Vector Databases**: FAISS + ChromaDB (with compatibility fixes)
- **Document Processing**:
  - PDF: PyPDF, PDFplumber
  - Word: docx2txt
  - Excel: unstructured, openpyxl
  - PowerPoint: unstructured
  - Text: TextLoader
- **Language Support**: langdetect, sentence-transformers, translate
- **Environment Management**: python-dotenv

### Enhanced RAG Pipeline

1. **Document Ingestion**: Extract text from multiple formats (PDF, DOCX, XLSX, PPTX, TXT)
2. **Language Detection**: Automatically detect document language from 12+ supported languages
3. **Text Chunking**: Split documents into manageable chunks (1000 chars, 200 overlap)
4. **Vectorization**: Create embeddings using multilingual embedding models
5. **Storage**: Store vectors in FAISS or ChromaDB with metadata support
6. **Retrieval**: Find relevant document chunks with cross-language capabilities
7. **Generation**: Generate contextual responses using selected AI provider (OpenAI/Anthropic/Google/Local)

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
# OpenAI API Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Anthropic API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Google AI API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Default AI Provider (openai, anthropic, google, local)
DEFAULT_AI_PROVIDER=openai

# Optional: Set OpenAI model (default is gpt-3.5-turbo)
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Set embedding model (default is text-embedding-ada-002)
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Optional: API Configuration
API_SECRET_KEY=your_secret_key_for_jwt_tokens
```

#### Get API Keys

##### OpenAI API Key (Required)

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the key and paste it in your `.env` file

##### Anthropic API Key (Optional)

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up for access to Claude API
3. Generate an API key
4. Add to your `.env` file as `ANTHROPIC_API_KEY`

##### Google AI API Key (Optional)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env` file as `GOOGLE_API_KEY`

##### Local Models (Optional)

For local models, install [Ollama](https://ollama.com/) and pull desired models:

```bash
# Install Ollama first, then pull models
ollama pull llama2
ollama pull codellama
```

⚠️ **Important**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

### 5. Run the Application

#### 🚀 Option A: Using the Runner Script (Recommended)

```bash
# Run the Streamlit Web UI
python run_app.py

# Or with streamlit directly
streamlit run run_app.py
```

#### 🔧 Option B: Direct Module Execution

```bash
# From the project root directory
streamlit run Modular_App/app.py
```

#### 📡 Option C: API Server Only

```bash
# Run the FastAPI server
python run_api.py

# Or with uvicorn directly
uvicorn Modular_App.api:app --reload --host 0.0.0.0 --port 8000
```

#### 🔄 Option D: Both Interfaces Simultaneously

```bash
# Terminal 1: Start the Web UI
python run_app.py

# Terminal 2: Start the API server
python run_api.py
```

> 💡 **Note**: The runner scripts (`run_app.py` and `run_api.py`) automatically handle Python path configuration and avoid import issues.

**Access Points**:

- **Web Interface**: `http://localhost:8501`
- **API Server**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

### 6. Choose Your Database

In the sidebar, select between:

- **FAISS**: Fast, lightweight vector database (recommended for most users)
- **ChromaDB**: Advanced vector database with enhanced features (for power users)

## 🔌 API Usage

### 🔌 Running the FastAPI Server

#### 🚀 Recommended Method (Using Runner Scripts)

```bash
# Start API server with proper path configuration
python run_api.py
```

#### 🔧 Alternative Methods

```bash
# Start both Web UI and API server in separate terminals
# Terminal 1: Web Interface
python run_app.py

# Terminal 2: API Server
python run_api.py

# Or use uvicorn directly (if no import issues)
uvicorn Modular_App.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`

### 🔐 API Authentication (oAuth Token)

The API uses JWT (JSON Web Token) authentication with default test credentials:

**Default Credentials**:

```json
{
  "admin": {
    "username": "admin",
    "password": "password123"
  },
  "user": {
    "username": "user",
    "password": "userpass"
  }
}

- **Admin**: username: `admin`, password: `password123`
- **User**: username: `user`, password: `userpass`

**Get Authentication Token**:

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

**Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

> ⚠️ **Security Note**: Change default credentials in production by modifying the `authenticate_user` function in `api.py`

### 📡 API Endpoints

#### Upload Documents

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document.pdf" \
  -F "files=@document.docx" \
  -F "database_type=faiss"
```

#### Chat with Documents

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the main topic of the documents?",
    "session_id": "default",
    "provider": "openai",
    "model": "gpt-3.5-turbo"
  }'
```

#### Get System Status

```bash
curl -X GET "http://localhost:8000/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Supported Providers and Models

- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo-preview`
- **Anthropic**: `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`, `claude-3-opus-20240229`
- **Google**: `gemini-pro`, `gemini-pro-vision`
- **Local**: Any Ollama-compatible model

## 🚧 Compatibility & Troubleshooting

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

### Using the Enhanced Chatbot

1. **Login** with the provided credentials
2. **Choose AI Provider**: Select from OpenAI, Anthropic, Google AI, or Local models
3. **Select Model**: Choose the specific model within your selected provider
4. **Choose Storage Option**:
   - **Memory only**: Temporary storage, data lost on restart
   - **Save to disk**: Persistent storage, builds cumulative knowledge base
5. **Upload Documents**: Select files in multiple formats:
   - **PDF files** (.pdf) - Standard PDF documents
   - **Word documents** (.docx) - Microsoft Word files
   - **Excel spreadsheets** (.xlsx) - Excel workbooks
   - **PowerPoint presentations** (.pptx) - PowerPoint slides
   - **Text files** (.txt) - Plain text documents
6. **Language Detection**: System automatically detects document languages
7. **Wait for Processing**: The system will extract, process, and index the content
8. **Ask Questions**: Type your questions about the document content in any supported language
9. **Get Answers**: Receive AI-generated responses based on your documents

### Switching Between Interfaces

- **Web Interface**: Access via `http://localhost:8501`
- **API Interface**: Access via `http://localhost:8000`
- **API Documentation**: Interactive docs at `http://localhost:8000/docs`

## 📁 Project Structure

```pwsh
GenAI.Chatbot.FromPDF/
├── Modular_App/                    # 🧩 Enhanced Modular Application
│   ├── app.py                      # Main Streamlit application entry
│   ├── main.py                     # Application orchestration
│   ├── config.py                   # Multi-provider configuration system
│   ├── auth.py                     # Authentication system
│   ├── document_processor.py       # Multi-format document processing
│   ├── vector_store.py             # Vector database abstraction
│   ├── chat_engine.py              # Enhanced chat management
│   ├── ui_components.py            # Streamlit UI components
│   ├── multi_model_provider.py     # Multi-AI provider system
│   ├── api.py                      # FastAPI REST API server
│   └── GenAI.Chatbot.AnsFromPDF.v2.py  # Legacy v2 compatibility
├── Docs/                           # 📚 Documentation
│   ├── ARCHITECTURE.md             # Enhanced system architecture
│   ├── FEATURES.md                 # Comprehensive feature documentation
│   ├── MIGRATION.md                # Migration guide v1→v2→v3
│   ├── TROUBLESHOOTING.md          # Multi-format troubleshooting
│   ├── API_GUIDE.md               # REST API documentation
│   └── CHANGELOG.md                # Version history
├── GenAI.Chatbot.AnsFromPDF.py    # 🔄 Original application
├── requirements.txt                # Enhanced Python dependencies
├── .env                            # Environment variables (create this)
├── .gitignore                      # Git ignore rules
├── README.md                       # This comprehensive file
├── venv/                           # Virtual environment (auto-created)
├── vector_db/                      # FAISS database storage (auto-created)
├── chroma_db/                      # ChromaDB storage (auto-created)
└── uploads/                        # Temporary document storage (auto-created)
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

```pwsh
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

- **[Architecture Guide](/Docs/ARCHITECTURE.md)**: Detailed system architecture and module descriptions
- **[Features Documentation](/Docs/FEATURES.md)**: Comprehensive feature overview and comparisons
- **[Migration Guide](/Docs/MIGRATION.md)**: Upgrade instructions from v1.0 to v2.0
- **[Troubleshooting Guide](/Docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[Change Log](/Docs/CHANGELOG.md)**: Version history and release notes

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

## 🚀 New Advanced Features

### 📄 Multi-Document Format Support

- ✅ **PDF Documents** - Full PDF processing with metadata extraction
- ✅ **Word Documents (.docx)** - Microsoft Word document support
- ✅ **Excel Spreadsheets (.xlsx)** - Excel file processing and data extraction
- ✅ **PowerPoint Presentations (.pptx)** - Slide content extraction
- ✅ **Text Files (.txt)** - Plain text document support

### 🌍 Multi-Language Support

- ✅ **12 Languages Supported** - English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Hindi
- ✅ **Automatic Language Detection** - Detects document language automatically
- ✅ **Multilingual Embeddings** - Advanced cross-language document understanding
- ✅ **Language-Aware Processing** - Optimized processing for each language

### 🤖 Multi-Model Provider Support

- ✅ **OpenAI** - GPT-3.5, GPT-4, GPT-4 Turbo + Advanced embeddings
- ✅ **Anthropic** - Claude 3 (Haiku, Sonnet, Opus) models
- ✅ **Google AI** - Gemini Pro and Gemini Pro Vision
- ✅ **Local Models** - Ollama support for privacy-focused deployments
- ✅ **Dynamic Model Switching** - Change models without restarting

### 🔌 REST API Interface

- ✅ **FastAPI Backend** - High-performance async API server
- ✅ **Document Upload API** - Programmatic document processing
- ✅ **Chat API** - RESTful chat interactions
- ✅ **Multi-Session Support** - Concurrent conversation management
- ✅ **Authentication** - Token-based API security
- ✅ **OpenAPI Documentation** - Interactive API docs at `/docs`

## 🚀 Future Enhancements

- [ ] Advanced authentication systems (OAuth, SAML)
- [ ] Document source attribution in responses
- [ ] Real-time collaborative features
- [ ] Docker containerization
- [ ] Cloud deployment guides
- [ ] Webhook integrations

---

Note* - **Built using OpenAI, LangChain, and Streamlit**

## Git Repo Status

[![GitHub Contributors](https://img.shields.io/github/contributors/pandyamehul/pandyamehul)](https://github.com/pandyamehul/GenAI.Simple.Chatbot/graphs/contributors)
[![Tests Coverage](https://codecov.io/gh/pandyamehul/pandyamehul/branch/master/graph/badge.svg)](https://codecov.io/gh/pandyamehul/GenAI.Simple.Chatbot)
[![Issues](https://img.shields.io/github/issues/pandyamehul/pandyamehul?color=0088ff)](https://github.com/pandyamehul/GenAI.Simple.Chatbot/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/pandyamehul/pandyamehul?color=0088ff)](https://github.com/pandyamehul/GenAI.Simple.Chatbot/pulls)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/pandyamehul/pandyamehul/badge)](https://securityscorecards.dev/viewer/?uri=github.com/pandyamehul/GenAI.Simple.Chatbot)
