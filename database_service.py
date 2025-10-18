import os
import bcrypt
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from datetime import datetime
import streamlit as st
from typing import Optional, Dict, List, Any


class DatabaseService:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            mongodb_uri = os.getenv('MONGODB_URI')
            database_name = os.getenv('DATABASE_NAME', 'stock_tracker')

            if not mongodb_uri:
                st.error("MongoDB URI not found in environment variables")
                return False

            self.client = MongoClient(mongodb_uri)
            self.db = self.client[database_name]

            # Test the connection
            self.client.admin.command('ping')
            print("Connected to MongoDB Atlas successfully!")

            # Create indexes for better performance
            self._create_indexes()
            return True

        except ConnectionFailure as e:
            st.error(f"Failed to connect to MongoDB Atlas: {e}")
            return False
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return False

    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # User collection indexes
            self.db.users.create_index("username", unique=True)
            self.db.users.create_index("email", unique=True)

            # Portfolio collection indexes
            self.db.portfolios.create_index([("user_id", 1), ("symbol", 1)])
            self.db.portfolios.create_index("user_id")

            # Watchlist collection indexes
            self.db.watchlists.create_index([("user_id", 1), ("symbol", 1)])
            self.db.watchlists.create_index("user_id")

            # Alerts collection indexes
            self.db.alerts.create_index([("user_id", 1), ("symbol", 1)])
            self.db.alerts.create_index("user_id")

        except Exception as e:
            print(f"Error creating indexes: {e}")

    # User Authentication Methods
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user account"""
        try:
            # Hash the password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

            user_doc = {
                "username": username.lower(),
                "email": email.lower(),
                "password": hashed_password,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "is_active": True
            }

            result = self.db.users.insert_one(user_doc)
            return result.acknowledged

        except DuplicateKeyError:
            st.error("Username or email already exists")
            return False
        except Exception as e:
            st.error(f"Error creating user: {e}")
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        try:
            user = self.db.users.find_one({
                "username": username.lower(),
                "is_active": True
            })

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
                # Update last login
                self.db.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
                return {
                    "user_id": str(user["_id"]),
                    "username": user["username"],
                    "email": user["email"]
                }
            return None

        except Exception as e:
            st.error(f"Authentication error: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user information by ID"""
        try:
            from bson import ObjectId
            user = self.db.users.find_one({"_id": ObjectId(user_id), "is_active": True})
            if user:
                return {
                    "user_id": str(user["_id"]),
                    "username": user["username"],
                    "email": user["email"]
                }
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    # Portfolio Methods
    def save_portfolio(self, user_id: str, portfolio_data: Dict, data_type: str = "stocks") -> bool:
        """Save user's portfolio data"""
        try:
            from bson import ObjectId

            portfolio_doc = {
                "user_id": ObjectId(user_id),
                f"{data_type}": portfolio_data.get(data_type, {}),
                "total_value": portfolio_data.get("total_value", 0),
                "total_cost": portfolio_data.get("total_cost", 0),
                "total_pnl": portfolio_data.get("total_pnl", 0),
                "data_type": data_type,
                "updated_at": datetime.utcnow()
            }

            # Upsert portfolio data
            result = self.db.portfolios.replace_one(
                {"user_id": ObjectId(user_id), "data_type": data_type},
                portfolio_doc,
                upsert=True
            )
            return result.acknowledged

        except Exception as e:
            st.error(f"Error saving portfolio: {e}")
            return False

    def load_portfolio(self, user_id: str, data_type: str = "stocks") -> Optional[Dict]:
        """Load user's portfolio data"""
        try:
            from bson import ObjectId
            portfolio = self.db.portfolios.find_one({"user_id": ObjectId(user_id), "data_type": data_type})
            if portfolio:
                return {
                    data_type: portfolio.get(data_type, {}),
                    "total_value": portfolio.get("total_value", 0),
                    "total_cost": portfolio.get("total_cost", 0),
                    "total_pnl": portfolio.get("total_pnl", 0)
                }
            return None
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            return None

    # Watchlist Methods
    def save_watchlist(self, user_id: str, watchlist_data: Dict, data_type: str = "stocks") -> bool:
        """Save user's watchlist data"""
        try:
            from bson import ObjectId

            watchlist_doc = {
                "user_id": ObjectId(user_id),
                f"{data_type}": watchlist_data.get(data_type, {}),
                "alerts": watchlist_data.get("alerts", {}),
                "data_type": data_type,
                "updated_at": datetime.utcnow()
            }

            result = self.db.watchlists.replace_one(
                {"user_id": ObjectId(user_id), "data_type": data_type},
                watchlist_doc,
                upsert=True
            )
            return result.acknowledged

        except Exception as e:
            st.error(f"Error saving watchlist: {e}")
            return False

    def load_watchlist(self, user_id: str, data_type: str = "stocks") -> Optional[Dict]:
        """Load user's watchlist data"""
        try:
            from bson import ObjectId
            watchlist = self.db.watchlists.find_one({"user_id": ObjectId(user_id), "data_type": data_type})
            if watchlist:
                return {
                    data_type: watchlist.get(data_type, {}),
                    "alerts": watchlist.get("alerts", {})
                }
            return None
        except Exception as e:
            print(f"Error loading watchlist: {e}")
            return None

    # Alert History Methods
    def save_alert_history(self, user_id: str, alert_data: List[Dict]) -> bool:
        """Save user's alert history"""
        try:
            from bson import ObjectId

            # Get existing alerts
            existing_alerts = list(self.db.alerts.find({"user_id": ObjectId(user_id)}))

            # Add new alerts
            for alert in alert_data:
                alert_doc = {
                    "user_id": ObjectId(user_id),
                    "symbol": alert.get("symbol"),
                    "alert_type": alert.get("alert_type"),
                    "threshold": alert.get("threshold"),
                    "current_price": alert.get("current_price"),
                    "message": alert.get("message"),
                    "timestamp": alert.get("timestamp", datetime.utcnow())
                }
                self.db.alerts.insert_one(alert_doc)

            return True

        except Exception as e:
            st.error(f"Error saving alert history: {e}")
            return False

    def load_alert_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Load user's alert history"""
        try:
            from bson import ObjectId
            alerts = list(self.db.alerts.find(
                {"user_id": ObjectId(user_id)}
            ).sort("timestamp", -1).limit(limit))

            return [{
                "symbol": alert["symbol"],
                "alert_type": alert["alert_type"],
                "threshold": alert["threshold"],
                "current_price": alert["current_price"],
                "message": alert["message"],
                "timestamp": alert["timestamp"]
            } for alert in alerts]

        except Exception as e:
            print(f"Error loading alert history: {e}")
            return []

    # AI Analysis History Methods
    def save_ai_analysis(self, user_id: str, analysis_type: str, symbol: str, analysis_data: Dict) -> bool:
        """Save AI analysis results"""
        try:
            from bson import ObjectId

            analysis_doc = {
                "user_id": ObjectId(user_id),
                "analysis_type": analysis_type,
                "symbol": symbol,
                "analysis_data": analysis_data,
                "timestamp": datetime.utcnow()
            }

            result = self.db.ai_analyses.insert_one(analysis_doc)
            return result.acknowledged

        except Exception as e:
            print(f"Error saving AI analysis: {e}")
            return False

    def load_ai_analysis_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Load user's AI analysis history"""
        try:
            from bson import ObjectId
            analyses = list(self.db.ai_analyses.find(
                {"user_id": ObjectId(user_id)}
            ).sort("timestamp", -1).limit(limit))

            return [{
                "analysis_type": analysis["analysis_type"],
                "symbol": analysis["symbol"],
                "analysis_data": analysis["analysis_data"],
                "timestamp": analysis["timestamp"]
            } for analysis in analyses]

        except Exception as e:
            print(f"Error loading AI analysis history: {e}")
            return []

    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()


# Global database instance
db_service = DatabaseService()
