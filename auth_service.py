import streamlit as st
import re
from database_service import db_service
from typing import Optional, Dict


class AuthService:
    def __init__(self):
        self._init_session_state()

    def _init_session_state(self):
        """Initialize authentication-related session state"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'login'

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        return True, "Password is valid"

    def login_page(self) -> bool:
        """Display login page and handle authentication"""
        st.title("🔐 Login to Stock Tracker")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                login_button = st.form_submit_button("Login", use_container_width=True)
            with col2:
                if st.form_submit_button("Sign Up Instead", use_container_width=True):
                    st.session_state.current_page = 'signup'
                    st.rerun()
            with col3:
                guest_button = st.form_submit_button("Continue as Guest", use_container_width=True)

            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                    return False

                user = db_service.authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                    return True
                else:
                    st.error("Invalid username or password")
                    return False

            if guest_button:
                st.session_state.authenticated = True
                st.session_state.user = {"user_id": "guest", "username": "guest", "email": "guest@example.com"}
                st.success("Continuing as guest user")
                st.rerun()
                return True

        return False

    def signup_page(self) -> bool:
        """Display signup page and handle user registration"""
        st.title("📝 Sign Up for Stock Tracker")

        with st.form("signup_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email address")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

            # Password requirements
            st.markdown("""
            **Password Requirements:**
            - At least 8 characters long
            - One uppercase letter
            - One lowercase letter
            - One number
            """)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                signup_button = st.form_submit_button("Sign Up", use_container_width=True)
            with col2:
                if st.form_submit_button("Back to Login", use_container_width=True):
                    st.session_state.current_page = 'login'
                    st.rerun()
            with col3:
                guest_button = st.form_submit_button("Continue as Guest", use_container_width=True)

            if signup_button:
                # Validation
                if not username or not email or not password or not confirm_password:
                    st.error("Please fill in all fields")
                    return False

                if password != confirm_password:
                    st.error("Passwords do not match")
                    return False

                if not self.validate_email(email):
                    st.error("Please enter a valid email address")
                    return False

                is_valid_password, password_message = self.validate_password(password)
                if not is_valid_password:
                    st.error(password_message)
                    return False

                # Create user
                if db_service.create_user(username, email, password):
                    st.success("Account created successfully! Please login with your credentials.")
                    st.session_state.current_page = 'login'
                    st.rerun()
                    return False  # Don't authenticate yet, let them login
                else:
                    return False

            if guest_button:
                st.session_state.authenticated = True
                st.session_state.user = {"user_id": "guest", "username": "guest", "email": "guest@example.com"}
                st.success("Continuing as guest user")
                st.rerun()
                return True

        return False

    def logout(self):
        """Logout current user"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.current_page = 'login'
        # Clear all user data from session
        keys_to_clear = ['portfolio', 'watchlist', 'alerts', 'ai_analyses']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    def show_auth_page(self) -> bool:
        """Show appropriate authentication page based on current state"""
        page = st.session_state.get('current_page', 'login')
        if page == 'login':
            return self.login_page()
        elif page == 'signup':
            return self.signup_page()
        return False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)

    def get_current_user(self) -> Optional[Dict]:
        """Get current user information"""
        return st.session_state.get('user')

    def require_auth(self):
        """Require authentication to access the app"""
        # Ensure session state keys used by auth exist
        self._init_session_state()

        if not self.is_authenticated():
            auth_success = self.show_auth_page()
            if not auth_success:
                st.stop()  # Stop execution if not authenticated

    def show_user_menu(self):
        """Show user menu in sidebar"""
        if self.is_authenticated():
            user = self.get_current_user()
            if user:
                st.sidebar.markdown("---")
                st.sidebar.markdown(f"<div class=\"user-name\">**👤 {user['username']}**</div>", unsafe_allow_html=True)
                if user['user_id'] != 'guest':
                    st.sidebar.markdown(f"<div class=\"user-name\">📧 {user['email']}</div>", unsafe_allow_html=True)

                if st.sidebar.button("🚪 Logout", use_container_width=True):
                    self.logout()


# Global auth service instance
auth_service = AuthService()
