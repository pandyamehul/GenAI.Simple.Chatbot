"""
Authentication module for the GenAI Chatbot application.
"""
import streamlit as st
from config import config_manager


class AuthManager:
    """Handles user authentication for the application."""
    
    def __init__(self):
        self.config = config_manager.app_config
    
    def authenticate(self) -> bool:
        """
        Handle user authentication with username and password.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        st.sidebar.title("🔐 Login")
        
        # Create input fields
        username = st.sidebar.text_input(
            "Username", 
            placeholder="Enter username"
        )
        password = st.sidebar.text_input(
            "Password", 
            type="password",
            placeholder="Enter password"
        )
        
        # Authentication logic
        if username and password:
            if self._validate_credentials(username, password):
                st.sidebar.success("✅ Logged in successfully!")
                return True
            else:
                st.sidebar.error("❌ Invalid credentials")
                return False
        
        # Show instructions if no input
        if not username and not password:
            st.sidebar.info("👆 Please enter your credentials")
        
        return False
    
    def _validate_credentials(self, username: str, password: str) -> bool:
        """
        Validate user credentials.
        
        Args:
            username (str): Username to validate
            password (str): Password to validate
            
        Returns:
            bool: True if credentials are valid
        """
        return (
            username == self.config.DEFAULT_USERNAME and 
            password == self.config.DEFAULT_PASSWORD
        )
    
    def show_login_info(self) -> None:
        """Display login information for users."""
        with st.sidebar.expander("ℹ️ Login Info"):
            st.write(f"**Username:** {self.config.DEFAULT_USERNAME}")
            st.write(f"**Password:** {self.config.DEFAULT_PASSWORD}")
            st.caption("Note: This is a demo authentication system")
    
    def logout(self) -> None:
        """Handle user logout (clear session state)."""
        if hasattr(st.session_state, 'authenticated'):
            del st.session_state.authenticated
        st.sidebar.success("Logged out successfully!")
    
    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.
        
        Returns:
            bool: True if user is authenticated
        """
        return getattr(st.session_state, 'authenticated', False)
    
    def require_authentication(self) -> bool:
        """
        Require authentication and handle login flow.
        
        Returns:
            bool: True if authenticated, False if authentication required
        """
        if not self.authenticate():
            self.show_login_info()
            st.warning("🔒 Please login to access the application")
            st.stop()
        
        # Store authentication state
        st.session_state.authenticated = True
        return True


# Global authentication manager instance
auth_manager = AuthManager()