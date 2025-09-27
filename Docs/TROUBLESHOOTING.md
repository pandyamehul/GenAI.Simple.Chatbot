# 🔧 Troubleshooting Guide - GenAI PDF Chatbot

This guide covers common issues and their solutions for the GenAI PDF Chatbot application.

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

## 🚀 Performance Optimization

### For Better Performance

1. **Use FAISS**: Generally faster than ChromaDB for most use cases
2. **Smaller Chunks**: Reduce chunk size for faster processing
3. **Fewer Documents**: Process documents in smaller batches
4. **SSD Storage**: Use SSD for database storage if possible
5. **More RAM**: Ensure sufficient system memory for large documents

This troubleshooting guide is regularly updated based on user feedback and common issues. If you encounter a problem not covered here, please contribute by documenting your solution!
