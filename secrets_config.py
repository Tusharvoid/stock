"""
Embedded configuration defaults. This file intentionally sets application
secrets as defaults for local testing or when environment variables are not
provided. It uses os.environ.setdefault so that real environment variables
or Streamlit Secrets (st.secrets) take precedence.

WARNING: Storing secrets in code is insecure for public repositories. Only do
this if you understand the risk. Prefer Streamlit Cloud Secrets or real
environment variables in production.
"""
import os

SECRETS = {
    "ALPHA_VANTAGE_API_KEY": "",
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": "587",
    "SENDER_EMAIL": "your_email@gmail.com",
    "SENDER_PASSWORD": "your_app_password",
    "RECIPIENT_EMAIL": "your_email@gmail.com",
    "GOOGLE_API_KEY": "AIzaSyANsL45-tJAoQlO5gUDTaXsRroaa4V6tzQ",
    "MONGODB_URI": "mongodb+srv://tusharbhande2040_db_user:voidbt9572@cluster0.vhyu9m7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "DATABASE_NAME": "stock_tracker",
    "APP_TITLE": "Advanced Stock Portfolio Tracker",
    "DEFAULT_PERIOD": "1mo",
    "STREAMLIT_SERVER_HEADLESS": "true",
    "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
}


def apply_to_env():
    """Apply secrets to os.environ only when the key is not already set.

    This uses setdefault to avoid overwriting environment values provided by
    the runtime (for example Streamlit's Secrets or CI/CD environment).
    """
    for k, v in SECRETS.items():
        if v is None:
            continue
        os.environ.setdefault(k, str(v))


if __name__ == "__main__":
    print("This module only provides embedded secrets. Call apply_to_env() in your app.")
