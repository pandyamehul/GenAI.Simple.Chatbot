# 🔧 Troubleshooting Guide - GenAI Enterprise Document Intelligence v3.0

This comprehensive guide covers common issues and solutions for the multi-format, multi-provider GenAI Enterprise Document Intelligence platform.

## 🚨 Common Installation Issues

### FAISS Loading Errors

#### Problem: `FAISS.__init__() got an unexpected keyword argument 'allow_dangerous_deserialization'`

**Cause**: Version incompatibility between LangChain and FAISS packages.

**Solution**: The application now includes automatic compatibility handling. The error should be resolved automatically. If it persists:

```bash
# Update to compatible versions
pip install --upgrade langchain faiss-cpu

# Or reinstall from requirements
pip install -r requirements.txt --upgrade
```

**Technical Details**: The application now uses a try-catch approach that attempts the newer API first, then falls back to the older method if the parameter is not supported.

### ChromaDB Installation Issues

#### Problem: ChromaDB installation failures or import errors

**Cause**: ChromaDB has additional system dependencies.

**Solutions**:

1. **Standard Installation**:

   ```bash
   pip install chromadb --upgrade
   ```

2. **Windows-specific Issues**:

   ```bash
   # Install Visual C++ Build Tools if needed
   pip install --upgrade setuptools wheel
   pip install chromadb
   ```

3. **macOS Issues**:

   ```bash
   # Install Xcode command line tools if needed
   xcode-select --install
   pip install chromadb
   ```

## 🔑 API Key Issues

### OpenAI API Key Problems

#### Problem: "OpenAI API key not found" or authentication errors

**Solutions**:

1. **Check .env file**:

   - Ensure `.env` file exists in project root
   - Verify format: `OPENAI_API_KEY=your_actual_key_here`
   - No quotes around the key value
   - No spaces around the equals sign

2. **Verify API Key**:

   - Test your key at: [Open AI API Keys](https://platform.openai.com/api-keys)
   - Check if you have available credits
   - Ensure the key has appropriate permissions

3. **File Location**:

    ```pwsh
    GenAI.Chatbot.FromPDF/
    ├── .env                 # Must be here (project root)
    └── Modular_App/
        ├── app.py
        └── main.py
    ```

4. **Environment Variable Alternative**:

   ```pwsh
   # Set directly in environment (Windows PowerShell)
   $env:OPENAI_API_KEY="your_key_here"
   
   # Set directly in environment (macOS/Linux)
   export OPENAI_API_KEY="your_key_here"
   ```

## 💾 Database Issues

### Vector Database Problems

#### Problem: Database creation or loading failures

**Solutions**:

1. **Clear Existing Databases**:

   ```bash
   # Remove existing databases and start fresh
   rm -rf vector_db/                # macOS/Linux
   Remove-Item -Recurse vector_db/  # Windows PowerShell
   ```

2. **Check Permissions**:
   - Ensure write permissions in project directory
   - Run application from project root directory

3. **Disk Space**:
   - Verify sufficient disk space for database storage
   - Large PDFs can create substantial vector databases

### FAISS vs ChromaDB Switching Issues

#### Problem: Data not appearing after switching databases

**Cause**: Each database type stores data separately.

**Solutions**:

1. **Understand Database Separation**: FAISS and ChromaDB maintain separate storage
2. **Migrate Data**: Use the application to rebuild your knowledge base with the new database
3. **Keep Both**: You can maintain both database types with the same documents

## 🖥️ Application Runtime Issues

### Streamlit Problems

#### Problem: Application won't start or crashes

**Solutions**:

1. **Check Python Version**:

   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Clear Streamlit Cache**:

   ```bash
   # Clear Streamlit cache
   streamlit cache clear
   ```

3. **Virtual Environment**:

   ```bash
   # Ensure virtual environment is activated
   # Windows:
   .\venv\Scripts\Activate.ps1
   # macOS/Linux:
   source venv/bin/activate
   ```

4. **Port Issues**:

   ```bash
   # Try different port if 8501 is busy
   streamlit run Modular_App/app.py --server.port 8502
   ```

### Memory Issues

#### Problem: Out of memory errors with large PDFs

**Solutions**:

1. **Reduce Chunk Size**:
   - Edit `Modular_App/config.py`
   - Reduce `CHUNK_SIZE` from 1000 to 500 or 250

2. **Process Fewer Documents**:
   - Upload PDFs in smaller batches
   - Process large documents individually

3. **Use FAISS Instead of ChromaDB**:
   - FAISS typically uses less memory
   - Switch database type in sidebar

## 🐛 Development Issues

### Import Errors

#### Problem: Module import errors

**Solutions**:

1. **Check Virtual Environment**:

   ```PWSH
   # Ensure you're in the virtual environment
   which python  # Should point to venv folder
   ```

2. **Reinstall Dependencies**:

   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Python Path Issues**:

   ```bash
   # Run from project root directory
   cd GenAI.Chatbot.FromPDF
   streamlit run Modular_App/app.py
   ```

### Configuration Errors

#### Problem: Configuration validation failures

**Solutions**:

1. **Check Modular_App/config.py**: Ensure all required settings are present
2. **Validate Environment**: Check all environment variables are set
3. **Reset Configuration**: Delete any cached configuration and restart

## 🔍 Debugging Tips

### Enable Debug Mode

1. **Streamlit Debug Mode**:

   ```bash
   streamlit run Modular_App/app.py --logger.level debug
   ```

2. **Check Browser Console**: Look for JavaScript errors in browser developer tools

3. **Check Terminal Output**: Monitor the terminal for Python error messages

### Log Analysis

1. **Streamlit Logs**: Check `~/.streamlit/logs/` for detailed logs
2. **Application Logs**: Monitor terminal output for custom log messages
3. **Browser Network Tab**: Check for failed API calls

## 📞 Getting Additional Help

### Information to Collect

When seeking help, please provide:

1. **System Information**:
   - Operating System (Windows/macOS/Linux)
   - Python version (`python --version`)
   - Package versions (`pip list`)

2. **Error Details**:
   - Complete error message
   - Steps to reproduce
   - Expected vs actual behavior

3. **Configuration**:
   - Are you using FAISS or ChromaDB?
   - Size and number of PDF files
   - Custom configuration changes

### Support Resources

- **Documentation**: Check README.md, FEATURES.md, and ARCHITECTURE.md
- **Common Issues**: Review this troubleshooting guide
- **Updates**: Check CHANGELOG.md for recent fixes

## 🔧 Quick Fixes Checklist

Before diving deep into troubleshooting:

- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file exists with valid OpenAI API key
- [ ] Running from project root directory
- [ ] Sufficient disk space available
- [ ] No other applications using port 8501
- [ ] Python version 3.8 or higher

## � Multi-Format Document Issues

### Document Processing Errors

#### Problem: "Unsupported file format" error

**Cause**: File format not in the supported list or corrupted file.

**Supported Formats**: PDF (.pdf), Word (.docx), Excel (.xlsx), PowerPoint (.pptx), Text (.txt)

**Solutions**:

1. **Verify file format**: Ensure the file extension matches the actual format
2. **Check file integrity**: Try opening the file in its native application
3. **Convert format**: Convert unsupported formats to supported ones
4. **File size**: Ensure files are under the size limit (default: 10MB per file)

#### Problem: Excel/PowerPoint processing fails

**Cause**: Missing dependencies for complex Office formats.

**Solution**:

```bash
# Reinstall with all dependencies
pip install unstructured[local-inference] --upgrade
pip install openpyxl python-pptx --upgrade
```

#### Problem: Word document content extraction incomplete

**Cause**: Complex Word formatting or embedded objects.

**Solutions**:

1. **Save as newer format**: Ensure .docx (not .doc)
2. **Remove complex formatting**: Simplify formatting before upload
3. **Check for embedded objects**: Images and tables may not extract fully

### Language Detection Issues

#### Problem: Wrong language detected for documents

**Cause**: Automatic language detection may fail with mixed languages or small text samples.

**Solutions**:

1. **Increase text content**: More text improves detection accuracy
2. **Manual specification**: Specify language if known (future feature)
3. **Clean text**: Remove excessive formatting or special characters

## 🤖 Multi-Provider AI Issues

### Provider Authentication Errors

#### Problem: "Provider authentication failed" for Anthropic/Google

**Cause**: Missing or invalid API keys in `.env` file.

**Solution**:

```bash
# Add to .env file
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

#### Problem: "Model not available" error

**Cause**: Selected model not available for the provider or region.

**Solutions**:

1. **Check model availability**: Verify model exists for your region
2. **Switch models**: Try different models within the same provider
3. **Provider fallback**: Switch to a different provider temporarily

### Local Model Issues

#### Problem: Ollama models not working

**Cause**: Ollama not installed or not running.

**Solutions**:

1. **Install Ollama**: Download from [Ollama.com](https://ollama.com/)
2. **Start Ollama service**: Ensure Ollama is running in background
3. **Pull models**: Use `ollama pull llama2` to download models
4. **Check connectivity**: Verify Ollama API is accessible at localhost:11434

#### Problem: Local models slow or out of memory

**Cause**: Insufficient system resources for local inference.

**Solutions**:

1. **Use smaller models**: Choose lighter models like llama2:7b
2. **Increase RAM**: Ensure sufficient system memory
3. **GPU acceleration**: Use GPU-enabled Ollama if available
4. **Reduce context**: Process smaller document chunks

## 🔌 REST API Issues

### API Server Problems

#### Problem: "Connection refused" when accessing API

**Cause**: FastAPI server not running or wrong port.

**Solutions**:

1. **Check server status**: Ensure API server is running
2. **Verify port**: Default is 8000, check for conflicts
3. **Start manually**: Use `uvicorn Modular_App.api:app --reload`
4. **Check logs**: Look for startup errors in console

## 🔐 Authentication & Security Issues

### JWT Authentication Problems

#### Problem: `POST /auth/token HTTP/1.1 404 Not Found`

**Cause**: Authentication endpoint missing or API server not configured properly.

**Solutions**:

1. **Verify endpoint**: Check that `/auth/token` endpoint is defined in api.py
2. **Server restart**: Restart API server after authentication updates
3. **Check imports**: Ensure all FastAPI dependencies are imported correctly

#### Problem: `401 Unauthorized` when accessing protected endpoints

**Cause**: Invalid, expired, or missing authentication token.

**Solutions**:

1. **Get new token**: Re-authenticate using correct credentials:

   ```bash
   curl -X POST "http://localhost:8000/auth/token" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password123"}'
   ```

2. **Check token format**: Ensure proper Bearer token format:

   ```bash
   Authorization: Bearer your_jwt_token_here
   ```

3. **Verify credentials**: Default credentials are:
   - Username: `admin`, Password: `password123`
   - Username: `user`, Password: `userpass`

4. **Token expiry**: Tokens expire after 24 hours - get a new one if expired

#### Problem: JWT import errors or JWT not available

**Cause**: PyJWT library not installed or import issues.

**Solutions**:

1. **Install PyJWT**:

   ```bash
   pip install PyJWT
   ```

2. **Fallback mode**: System automatically uses simple token authentication when JWT unavailable

3. **Environment token**: Set API_TOKEN environment variable for fallback:

   ```bash
   export API_TOKEN=your-secure-token-here
   ```

#### Problem: "Invalid token" errors with correct credentials

**Cause**: Token corruption, encoding issues, or secret key mismatch.

**Solutions**:

1. **Check secret key**: Ensure API_SECRET_KEY is consistent:

   ```bash
   export API_SECRET_KEY=your-secret-key-change-in-production
   ```

2. **Token encoding**: Verify token is properly encoded and not truncated

3. **Server restart**: Restart API server to refresh token validation

4. **Debug mode**: Check server logs for specific JWT decode errors

### CORS and Browser Issues

#### Problem: CORS errors when accessing API from web browser

**Cause**: Cross-origin request blocking by browser security.

**Solutions**:

1. **Development**: CORS is configured for "*" origins in development
2. **Production**: Update CORS settings in api.py for specific domains
3. **Preflight**: Ensure OPTIONS requests are handled correctly

#### Problem: Browser network errors with valid tokens

**Cause**: Browser security policies or network configuration.

**Solutions**:

1. **Use curl**: Test API directly to isolate browser issues
2. **Check network**: Verify no proxy or firewall blocking requests
3. **HTTPS**: Use HTTPS in production for secure token transmission

### File Upload Issues

#### Problem: "File too large" error in API

**Cause**: File exceeds maximum upload size.

**Solutions**:

1. **Reduce file size**: Compress or split large documents
2. **Increase limit**: Modify `MAX_FILE_SIZE` in configuration
3. **Use chunks**: Upload large files in smaller parts
4. **Check format**: Some formats are more efficient than others

## 🌍 Multi-Language Issues

### Encoding Problems

#### Problem: Special characters not displaying correctly

**Cause**: Text encoding issues with non-Latin scripts.

**Solutions**:

1. **UTF-8 encoding**: Ensure documents are saved with UTF-8 encoding
2. **System locale**: Check system language settings
3. **Font support**: Ensure system has fonts for the target language

#### Problem: Poor results with non-English documents

**Cause**: Model limitations with specific languages.

**Solutions**:

1. **Switch providers**: Different providers excel with different languages
2. **Use multilingual models**: Some models are better for specific languages
3. **Increase context**: Provide more text for better understanding

## �🚀 Performance Optimization

### For Better Performance

1. **Document Format Choice**: PDF and TXT process fastest, PPTX slowest
2. **Use FAISS**: Generally faster than ChromaDB for most use cases
3. **Smaller Chunks**: Reduce chunk size for faster processing
4. **Provider Selection**: OpenAI typically fastest, local models slowest
5. **Batch Processing**: Process documents in smaller batches
6. **SSD Storage**: Use SSD for database storage if possible
7. **More RAM**: Ensure sufficient system memory for large documents

### Memory Management

#### High Memory Usage

**Solutions**:

1. **Smaller batch sizes**: Process fewer documents at once
2. **Clear unused data**: Regularly clear conversation history
3. **Restart application**: Periodic restarts help memory cleanup
4. **Use FAISS**: Generally more memory efficient than ChromaDB

## 📊 Monitoring and Debugging

### Enable Debug Logging

Add to `.env` file:

```bash
LOG_LEVEL=DEBUG
VERBOSE_LOGGING=true
```

### Health Check Endpoints

- **Web UI**: `http://localhost:8501`
- **API Health**: `http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs`

This troubleshooting guide is regularly updated based on user feedback and common issues. If you encounter a problem not covered here, please contribute by documenting your solution!
