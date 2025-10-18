import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from ai_service import GeminiAIService
from auth_service import auth_service
from database_service import db_service
from chat_interface import render_chat_interface
from theme import get_theme_css

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Advanced Stock Portfolio Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject centralized theme CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

class EmailNotifier:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')

    def send_alert(self, subject: str, message: str) -> bool:
        """Send email alert"""
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            st.warning("Email configuration incomplete. Please set environment variables.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)
            server.quit()

            return True
        except Exception as e:
            st.error(f"Failed to send email: {str(e)}")
            return False

class AdvancedStockTracker:
    def __init__(self):
        # Get current user
        self.current_user = auth_service.get_current_user()
        self.is_guest = self.current_user and self.current_user.get('user_id') == 'guest'

        # Initialize session state for persistent data
        self._init_session_state()

        self.email_notifier = EmailNotifier()
        self.ai_service = GeminiAIService()

        # Currency conversion
        self.usd_to_inr_rate = self._get_usd_to_inr_rate()

    def _get_usd_to_inr_rate(self) -> float:
        """Get current USD to INR exchange rate"""
        try:
            # Try to get exchange rate from a free API
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data['rates'].get('INR', 83.0)  # Default to 83 if API fails
        except Exception as e:
            st.warning(f"Could not fetch exchange rate: {e}. Using default rate.")

        return 83.0  # Default USD to INR rate

    def usd_to_inr(self, usd_amount: float) -> float:
        """Convert USD amount to INR"""
        return round(usd_amount * self.usd_to_inr_rate, 2)

    def format_inr(self, usd_amount: float) -> str:
        """Format USD amount as INR string"""
        inr_amount = self.usd_to_inr(usd_amount)
        return f"₹{inr_amount:,.2f}"

    def search_stocks_by_name(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for stocks by name and return matching symbols"""
        if not query or len(query.strip()) < 2:
            return []

        query = query.strip().lower()
        results = []

        try:
            # First try Gemini AI to identify potential stock symbols
            ai_suggestions = self._get_stock_suggestions_from_ai(query)
            ai_symbols = ai_suggestions.get('symbols', [])

            # Add AI-suggested symbols to search
            all_symbols_to_check = ai_symbols[:limit]  # Limit AI suggestions

            # Add common symbols that might match
            common_symbols = [
                'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'BABA', 'ORCL',
                'INTC', 'AMD', 'CRM', 'ADBE', 'PYPL', 'UBER', 'LYFT', 'SPOT', 'ZOOM', 'SHOP',
                'SQ', 'COIN', 'MSTR', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'TCEHY', 'BIDU',
                'JD', 'PDD', 'NTES', 'BILI', 'IQ', 'WB', 'YY', 'HUYA', 'DOYU', 'TAL',
                'EDU', 'GOTU', 'DAO', 'KC', 'QFIN', 'LU', 'YALA', 'FINV', 'AIHS', 'BTBT',
                # Indian stocks
                'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
                'ITC.NS', 'KOTAKBANK.NS', 'LT.NS', 'MARUTI.NS', 'BAJFINANCE.NS', 'BHARTIARTL.NS',
                'TATAMOTORS.NS', 'WIPRO.NS', 'AXISBANK.NS', 'NTPC.NS', 'POWERGRID.NS', 'ONGC.NS'
            ]

            # Filter common symbols that might match the query
            for symbol in common_symbols:
                if len(all_symbols_to_check) >= limit:
                    break
                if query in symbol.lower() or any(word in symbol.lower() for word in query.split()):
                    if symbol not in all_symbols_to_check:
                        all_symbols_to_check.append(symbol)

            # Now check each symbol
            for symbol in all_symbols_to_check[:limit]:
                try:
                    stock = yf.Ticker(symbol)
                    info = stock.info

                    if info and 'longName' in info:
                        name = info.get('longName', '').lower()
                        short_name = info.get('shortName', '').lower()

                        # Check if query matches name or symbol
                        if (query in name or query in short_name or
                            any(word in name for word in query.split()) or
                            any(word in short_name for word in query.split())):

                            current_price = info.get('currentPrice', 0)
                            if current_price > 0:
                                results.append({
                                    'symbol': symbol,
                                    'name': info.get('longName', symbol),
                                    'short_name': info.get('shortName', symbol),
                                    'current_price': round(current_price, 2),
                                    'exchange': info.get('exchange', 'Unknown')
                                })

                except Exception:
                    continue  # Skip failed lookups

            # If no results from AI suggestions, try direct symbol lookup
            if not results and len(query) <= 5:  # Likely a symbol
                try:
                    stock = yf.Ticker(query.upper())
                    info = stock.info
                    if info and 'longName' in info:
                        current_price = info.get('currentPrice', 0)
                        if current_price > 0:
                            results.append({
                                'symbol': query.upper(),
                                'name': info.get('longName', query.upper()),
                                'short_name': info.get('shortName', query.upper()),
                                'current_price': round(current_price, 2),
                                'exchange': info.get('exchange', 'Unknown')
                            })
                except Exception:
                    pass

        except Exception as e:
            st.error(f"Error searching stocks: {e}")

        return results

    def _get_stock_suggestions_from_ai(self, query: str) -> Dict:
        """Use Gemini AI to suggest stock symbols for a company name"""
        try:
            if not self.ai_service or not self.ai_service.is_available():
                return {'symbols': []}

            prompt = f"""
            For the company name "{query}", suggest the most relevant stock ticker symbols.
            Focus on major exchanges like NYSE, NASDAQ, NSE (India), etc.

            Return ONLY a JSON object with this exact format:
            {{
                "symbols": ["SYMBOL1", "SYMBOL2", "SYMBOL3"],
                "explanation": "brief explanation"
            }}

            Examples:
            - For "Apple" -> ["AAPL"]
            - For "Google" -> ["GOOGL", "GOOG"]
            - For "Tata Motors" -> ["TATAMOTORS.NS"]
            - For "Reliance" -> ["RELIANCE.NS"]

            Be precise and include the correct exchange suffix (.NS for NSE, etc.).
            """

            response = self.ai_service.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean up response (remove markdown formatting if present)
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            import json
            result = json.loads(response_text)
            return result

        except Exception as e:
            # Fallback symbols for common queries
            fallbacks = {
                'tata motors': ['TATAMOTORS.NS'],
                'tata': ['TATAMOTORS.NS', 'TATACONSUM.NS', 'TATAPOWER.NS'],
                'reliance': ['RELIANCE.NS'],
                'infosys': ['INFY.NS'],
                'wipro': ['WIPRO.NS'],
                'hdfc': ['HDFCBANK.NS', 'HDFC.NS'],
                'icici': ['ICICIBANK.NS'],
                'sbi': ['SBIN.NS'],
                'apple': ['AAPL'],
                'google': ['GOOGL'],
                'microsoft': ['MSFT'],
                'amazon': ['AMZN'],
                'tesla': ['TSLA'],
                'meta': ['META'],
                'netflix': ['NFLX']
            }

            query_lower = query.lower()
            for key, symbols in fallbacks.items():
                if key in query_lower or query_lower in key:
                    return {'symbols': symbols, 'explanation': f'Common symbols for {query}'}

            return {'symbols': [], 'explanation': 'No suggestions available'}

    def _init_session_state(self):
        """Initialize session state, loading from database if user is logged in"""
        # Initialize basic session state
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None

        # Load user data from database if authenticated
        if self.current_user and not self.is_guest:
            self._load_user_data_from_db()
        else:
            self._init_guest_data()

    def _init_guest_data(self):
        """Initialize data for guest users"""
        if 'watched_stocks' not in st.session_state:
            st.session_state.watched_stocks = []
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = {}
        if 'stock_data' not in st.session_state:
            st.session_state.stock_data = {}
        if 'alerts' not in st.session_state:
            st.session_state.alerts = {}
        if 'email_history' not in st.session_state:
            st.session_state.email_history = []

        # Mutual fund data
        if 'watched_mutual_funds' not in st.session_state:
            st.session_state.watched_mutual_funds = []
        if 'mutual_fund_data' not in st.session_state:
            st.session_state.mutual_fund_data = {}
        if 'mutual_fund_alerts' not in st.session_state:
            st.session_state.mutual_fund_alerts = {}
        if 'mutual_fund_portfolio' not in st.session_state:
            st.session_state.mutual_fund_portfolio = {}

    def _load_user_data_from_db(self):
        """Load user data from database"""
        user_id = self.current_user['user_id']

        # Load watchlist
        watchlist_data = db_service.load_watchlist(user_id)
        if watchlist_data:
            st.session_state.watched_stocks = list(watchlist_data.get('stocks', {}).keys())
            st.session_state.stock_data = watchlist_data.get('stocks', {})
            st.session_state.alerts = watchlist_data.get('alerts', {})
        else:
            st.session_state.watched_stocks = []
            st.session_state.stock_data = {}
            st.session_state.alerts = {}

        # Load portfolio
        portfolio_data = db_service.load_portfolio(user_id)
        if portfolio_data:
            st.session_state.portfolio = portfolio_data.get('stocks', {})
        else:
            st.session_state.portfolio = {}

        # Load mutual fund data
        mf_watchlist_data = db_service.load_watchlist(user_id, data_type='mutual_funds')
        if mf_watchlist_data:
            st.session_state.watched_mutual_funds = list(mf_watchlist_data.get('mutual_funds', {}).keys())
            st.session_state.mutual_fund_data = mf_watchlist_data.get('mutual_funds', {})
            st.session_state.mutual_fund_alerts = mf_watchlist_data.get('alerts', {})
        else:
            st.session_state.watched_mutual_funds = []
            st.session_state.mutual_fund_data = {}
            st.session_state.mutual_fund_alerts = {}

        # Load mutual fund portfolio
        mf_portfolio_data = db_service.load_portfolio(user_id, data_type='mutual_funds')
        if mf_portfolio_data:
            st.session_state.mutual_fund_portfolio = mf_portfolio_data.get('mutual_funds', {})
        else:
            st.session_state.mutual_fund_portfolio = {}

        # Load alert history
        alert_history = db_service.load_alert_history(user_id)
        st.session_state.email_history = alert_history

    def _save_user_data_to_db(self):
        """Save current user data to database"""
        if not self.current_user or self.is_guest:
            return  # Don't save for guest users

        user_id = self.current_user['user_id']

        # Save stock watchlist
        watchlist_data = {
            'stocks': st.session_state.stock_data,
            'alerts': st.session_state.alerts
        }
        db_service.save_watchlist(user_id, watchlist_data)

        # Save stock portfolio
        portfolio_data = {
            'stocks': st.session_state.portfolio,
            'total_value': self.get_portfolio_value()['total_value'],
            'total_cost': self.get_portfolio_value()['total_cost'],
            'total_pnl': self.get_portfolio_value()['total_gain_loss']
        }
        db_service.save_portfolio(user_id, portfolio_data)

        # Save mutual fund watchlist
        mf_watchlist_data = {
            'mutual_funds': st.session_state.mutual_fund_data,
            'alerts': st.session_state.mutual_fund_alerts
        }
        db_service.save_watchlist(user_id, mf_watchlist_data, data_type='mutual_funds')

        # Save mutual fund portfolio
        mf_portfolio_data = {
            'mutual_funds': st.session_state.mutual_fund_portfolio,
            'total_value': self.get_mutual_fund_portfolio_value()['total_value'],
            'total_cost': self.get_mutual_fund_portfolio_value()['total_cost'],
            'total_pnl': self.get_mutual_fund_portfolio_value()['total_gain_loss']
        }
        db_service.save_portfolio(user_id, mf_portfolio_data, data_type='mutual_funds')

        # Save alert history
        if st.session_state.email_history:
            db_service.save_alert_history(user_id, st.session_state.email_history)

    def get_stock_data_yahoo(self, symbol: str) -> Optional[Dict]:
        """Get stock data using yfinance (Yahoo Finance)"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1d")

            if hist.empty:
                return None

            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0

            return {
                'symbol': symbol.upper(),
                'name': info.get('longName', info.get('shortName', symbol)),
                'current_price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'open': round(info.get('open', 0), 2),
                'high': round(info.get('dayHigh', hist['High'].max()), 2),
                'low': round(info.get('dayLow', hist['Low'].min()), 2),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'dividend_yield': info.get('dividendYield', None),
                '52_week_high': round(info.get('fiftyTwoWeekHigh', 0), 2),
                '52_week_low': round(info.get('fiftyTwoWeekLow', 0), 2),
                'source': 'yahoo_finance',
                'last_updated': datetime.now()
            }
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get stock data using Yahoo Finance"""
        return self.get_stock_data_yahoo(symbol)

    def add_stock(self, symbol: str) -> bool:
        """Add a stock to the watchlist"""
        symbol = symbol.upper().strip()

        if symbol in st.session_state.watched_stocks:
            st.warning(f"Stock {symbol} is already in your watchlist!")
            return False

        # Verify stock exists
        stock_data = self.get_stock_data(symbol)
        if not stock_data:
            st.error(f"Could not find stock data for {symbol}")
            return False

        st.session_state.watched_stocks.append(symbol)
        st.session_state.stock_data[symbol] = stock_data
        st.session_state.alerts[symbol] = {'buy_threshold': 0.0, 'sell_threshold': 0.0}
        st.success(f"Added {symbol} to your watchlist!")
        return True

    def remove_stock(self, symbol: str) -> bool:
        """Remove a stock from the watchlist"""
        if symbol in st.session_state.watched_stocks:
            st.session_state.watched_stocks.remove(symbol)
            if symbol in st.session_state.stock_data:
                del st.session_state.stock_data[symbol]
            if symbol in st.session_state.alerts:
                del st.session_state.alerts[symbol]
            if symbol in st.session_state.portfolio:
                del st.session_state.portfolio[symbol]
            st.success(f"Removed {symbol} from your watchlist!")
            return True
        return False

    def buy_stock(self, symbol: str, shares: int, price_inr: float) -> bool:
        """Add stock to portfolio"""
        if symbol not in st.session_state.watched_stocks:
            st.error(f"Stock {symbol} is not in your watchlist!")
            return False

        if shares <= 0 or price_inr <= 0:
            st.error("Invalid shares or price!")
            return False

        # Convert INR price to USD for storage
        price_usd = price_inr / self.usd_to_inr_rate

        if symbol in st.session_state.portfolio:
            # Update existing position
            existing_shares = st.session_state.portfolio[symbol]['shares']
            existing_total = st.session_state.portfolio[symbol]['avg_price'] * existing_shares
            new_total = price_usd * shares
            total_shares = existing_shares + shares
            avg_price = (existing_total + new_total) / total_shares

            st.session_state.portfolio[symbol]['shares'] = total_shares
            st.session_state.portfolio[symbol]['avg_price'] = round(avg_price, 2)
        else:
            # New position
            st.session_state.portfolio[symbol] = {
                'shares': shares,
                'avg_price': round(price_usd, 2),
                'buy_date': datetime.now()
            }

        st.success(f"Bought {shares} shares of {symbol} at {self.format_inr(price_inr)} per share!")
        self._save_user_data_to_db()  # Save after buying
        return True

    def sell_stock(self, symbol: str, shares: int, price_inr: float) -> bool:
        """Sell stock from portfolio"""
        if symbol not in st.session_state.portfolio:
            st.error(f"You don't own {symbol}!")
            return False

        if shares > st.session_state.portfolio[symbol]['shares']:
            st.error("You don't have enough shares!")
            return False

        # Convert INR price to USD for calculation
        price_usd = price_inr / self.usd_to_inr_rate

        # Calculate profit/loss
        cost_basis = st.session_state.portfolio[symbol]['avg_price'] * shares
        sale_value = price_usd * shares
        profit_loss = sale_value - cost_basis

        # Update portfolio
        st.session_state.portfolio[symbol]['shares'] -= shares
        if st.session_state.portfolio[symbol]['shares'] == 0:
            del st.session_state.portfolio[symbol]

        st.success(f"Sold {shares} shares of {symbol} at {self.format_inr(price_inr)} per share. P&L: {self.format_inr(profit_loss * self.usd_to_inr_rate)}")
        self._save_user_data_to_db()  # Save after selling
        return True

    def check_alerts(self):
        """Check if any stock prices have hit alert thresholds"""
        alerts_triggered = []

        for symbol in st.session_state.watched_stocks:
            if symbol in st.session_state.stock_data and symbol in st.session_state.alerts:
                current_price = st.session_state.stock_data[symbol]['current_price']
                buy_threshold = st.session_state.alerts[symbol]['buy_threshold']
                sell_threshold = st.session_state.alerts[symbol]['sell_threshold']

                if buy_threshold > 0 and current_price <= buy_threshold:
                    alerts_triggered.append({
                        'type': 'BUY',
                        'symbol': symbol,
                        'current_price': current_price,
                        'threshold': buy_threshold
                    })

                if sell_threshold > 0 and current_price >= sell_threshold:
                    alerts_triggered.append({
                        'type': 'SELL',
                        'symbol': symbol,
                        'current_price': current_price,
                        'threshold': sell_threshold
                    })

        # Send email notifications for new alerts
        for alert in alerts_triggered:
            alert_key = f"{alert['symbol']}_{alert['type']}_{datetime.now().strftime('%Y%m%d_%H%M')}"

            if alert_key not in [h['key'] for h in st.session_state.email_history]:
                subject = f"🚨 Stock Alert: {alert['type']} {alert['symbol']}"
                message = f"""
                <h2>Stock Alert Triggered!</h2>
                <p><strong>Action:</strong> {alert['type']}</p>
                <p><strong>Stock:</strong> {alert['symbol']}</p>
                <p><strong>Current Price:</strong> ${alert['current_price']:.2f}</p>
                <p><strong>Threshold:</strong> ${alert['threshold']:.2f}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                """

                if self.email_notifier.send_alert(subject, message):
                    st.session_state.email_history.append({
                        'key': alert_key,
                        'timestamp': datetime.now(),
                        'alert': alert
                    })

        # Save alert history to database
        if alerts_triggered:
            self._save_user_data_to_db()

        return alerts_triggered

    def generate_ai_response(self, user_input: str) -> str:
        """Generate contextual AI response based on user input and portfolio data"""
        user_input_lower = user_input.lower()

        # Analyze user intent and provide contextual responses
        try:
            # Check for stock-specific queries
            mentioned_stocks = []
            for symbol in st.session_state.watched_stocks:
                if symbol.lower() in user_input_lower or symbol in user_input.upper():
                    mentioned_stocks.append(symbol)

            # Portfolio analysis requests
            if any(word in user_input_lower for word in ['portfolio', 'holdings', 'positions', 'analyze my']):
                if st.session_state.portfolio:
                    return self.ai_service.analyze_portfolio(
                        st.session_state.portfolio,
                        st.session_state.stock_data
                    )
                else:
                    return "🤖 **AI Assistant:** I see you don't have any stocks in your portfolio yet! Would you like me to help you get started with some investment recommendations? I can suggest stocks based on different risk levels and market sectors."

            # Stock analysis requests
            elif mentioned_stocks:
                symbol = mentioned_stocks[0]  # Take the first mentioned stock
                stock_data = st.session_state.stock_data.get(symbol)

                if stock_data:
                    if any(word in user_input_lower for word in ['predict', 'forecast', 'movement', 'trend']):
                        portfolio_data = st.session_state.portfolio.get(symbol)
                        return self.ai_service.predict_stock_movement(symbol, stock_data, portfolio_data)
                    else:
                        return self.ai_service.get_stock_insights(symbol, stock_data)
                else:
                    return f"🤖 **AI Assistant:** I don't have current data for {symbol}. Try refreshing your watchlist first!"

            # Market sentiment requests
            elif any(word in user_input_lower for word in ['market', 'sentiment', 'outlook', 'economy']):
                return self.ai_service.get_market_sentiment()

            # Investment strategy requests
            elif any(word in user_input_lower for word in ['strategy', 'invest', 'advice', 'recommend']):
                # Try to infer risk tolerance and horizon from context
                risk_tolerance = "moderate"
                if any(word in user_input_lower for word in ['conservative', 'safe', 'low risk']):
                    risk_tolerance = "conservative"
                elif any(word in user_input_lower for word in ['aggressive', 'high risk', 'growth']):
                    risk_tolerance = "aggressive"

                horizon = "medium-term (3-7 years)"
                if any(word in user_input_lower for word in ['short', 'quick', '1-3']):
                    horizon = "short-term (1-3 years)"
                elif any(word in user_input_lower for word in ['long', 'retirement', '7+']):
                    horizon = "long-term (7+ years)"

                return self.ai_service.get_investment_strategy(risk_tolerance, horizon)

            # Help/greeting requests
            elif any(word in user_input_lower for word in ['help', 'what can you', 'how', 'hi', 'hello', 'start']):
                portfolio_status = "you have an active portfolio" if st.session_state.portfolio else "you're just getting started"
                watchlist_count = len(st.session_state.watched_stocks)

                return f"""🤖 **AI Assistant:** Hi there! I'm your personal investment assistant. I can help you with:

💰 **Portfolio Analysis**: Deep insights into your current holdings ({len(st.session_state.portfolio)} positions)
📊 **Stock Research**: Detailed analysis of any stock in your watchlist ({watchlist_count} stocks)
🔮 **Price Predictions**: AI-powered movement forecasts
🌍 **Market Intelligence**: Current market sentiment and trends
💡 **Investment Strategy**: Personalized recommendations based on your risk tolerance

You can ask me things like:
• "Analyze my portfolio"
• "What do you think about AAPL?"
• "Should I buy more of my current holdings?"
• "What's the market outlook?"
• "Suggest an investment strategy"

What would you like to know about your investments?"""

            # Default response - general investment chat
            else:
                # Create a contextual prompt based on user's portfolio
                context_info = ""
                if st.session_state.portfolio:
                    top_holdings = list(st.session_state.portfolio.keys())[:3]
                    context_info = f"You have positions in {', '.join(top_holdings)}. "
                if st.session_state.watched_stocks:
                    watchlist_sample = st.session_state.watched_stocks[:5]
                    context_info += f"You're watching {', '.join(watchlist_sample)}."

                prompt = f"""
                You are a friendly AI investment assistant having a conversation. The user asked: "{user_input}"

                Context about the user: {context_info}

                Provide a helpful, conversational response about their investment question.
                Keep it practical and actionable. Use emojis to make it friendly.
                If they're asking something specific about investing, give concrete advice.
                If it's a general question, provide educational insights.

                Format your response like a natural conversation, not a formal report.
                """

                response = self.ai_service.model.generate_content(prompt)
                return response.text

        except Exception as e:
            return f"🤖 **AI Assistant:** I had trouble processing that request. Let me try a different approach! Error: {str(e)}"

    def refresh_all_stocks(self):
        """Refresh data for all watched stocks"""
        if not st.session_state.watched_stocks:
            st.info("No stocks in watchlist to refresh")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()

        total_stocks = len(st.session_state.watched_stocks)
        updated_count = 0

        for i, symbol in enumerate(st.session_state.watched_stocks):
            status_text.text(f"Refreshing {symbol}...")
            stock_data = self.get_stock_data(symbol)

            if stock_data:
                st.session_state.stock_data[symbol] = stock_data
                updated_count += 1

            progress_bar.progress((i + 1) / total_stocks)
            time.sleep(0.1)  # Small delay to show progress

        progress_bar.empty()
        status_text.empty()

        st.session_state.last_update = datetime.now()

        # Check for alerts after refresh
        alerts = self.check_alerts()
        if alerts:
            st.info(f"⚠️ {len(alerts)} alert(s) triggered! Check the Alerts tab.")

        st.success(f"Refreshed {updated_count}/{total_stocks} stocks")

    def get_historical_data(self, symbol: str, period: str = "1mo") -> pd.DataFrame:
        """Get historical data for charting"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            return hist
        except Exception as e:
            st.error(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()

    def get_mutual_fund_data(self, scheme_code: str) -> Optional[Dict]:
        """Get mutual fund data from BSE API"""
        try:
            # BSE API for mutual fund data
            url = f"https://api.bseindia.com/BseIndiaAPI/api/GetMktData/w"
            params = {
                'flag': 'MF',
                'scode': scheme_code
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()

                if data and 'Table' in data and data['Table']:
                    mf_data = data['Table'][0]

                    # Extract NAV and other details
                    nav = float(mf_data.get('NAV', 0))
                    if nav > 0:
                        return {
                            'scheme_code': scheme_code,
                            'name': mf_data.get('SchemeName', f'MF-{scheme_code}'),
                            'nav': nav,
                            'change': float(mf_data.get('Change', 0)),
                            'change_percent': float(mf_data.get('ChangePercent', 0)),
                            'category': mf_data.get('Category', 'Unknown'),
                            'amc': mf_data.get('AMC', 'Unknown'),
                            'aum': mf_data.get('AUM', 0),
                            'last_updated': datetime.now(),
                            'source': 'bse_api'
                        }

            # Fallback: Try alternative API or mock data for demo
            return self._get_mock_mutual_fund_data(scheme_code)

        except Exception as e:
            st.error(f"Error fetching MF data for {scheme_code}: {str(e)}")
            return self._get_mock_mutual_fund_data(scheme_code)

    def _get_mock_mutual_fund_data(self, scheme_code: str) -> Optional[Dict]:
        """Mock mutual fund data for demonstration"""
        # Common Indian mutual fund schemes with mock data
        mock_funds = {
            '120465': {  # SBI Bluechip Fund
                'name': 'SBI Bluechip Fund - Direct Plan',
                'nav': 85.32,
                'change': 1.25,
                'change_percent': 1.49,
                'category': 'Large Cap',
                'amc': 'SBI Mutual Fund'
            },
            '118834': {  # HDFC Top 100 Fund
                'name': 'HDFC Top 100 Fund - Direct Plan',
                'nav': 945.67,
                'change': -2.15,
                'change_percent': -0.23,
                'category': 'Large Cap',
                'amc': 'HDFC Mutual Fund'
            },
            '120828': {  # ICICI Prudential Technology Fund
                'name': 'ICICI Prudential Technology Fund - Direct Plan',
                'nav': 178.45,
                'change': 3.67,
                'change_percent': 2.10,
                'category': 'Sectoral/Technology',
                'amc': 'ICICI Prudential Mutual Fund'
            },
            '122639': {  # Axis Small Cap Fund
                'name': 'Axis Small Cap Fund - Direct Plan',
                'nav': 92.18,
                'change': 0.95,
                'change_percent': 1.04,
                'category': 'Small Cap',
                'amc': 'Axis Mutual Fund'
            }
        }

        if scheme_code in mock_funds:
            fund_data = mock_funds[scheme_code]
            return {
                'scheme_code': scheme_code,
                'name': fund_data['name'],
                'nav': fund_data['nav'],
                'change': fund_data['change'],
                'change_percent': fund_data['change_percent'],
                'category': fund_data['category'],
                'amc': fund_data['amc'],
                'aum': 0,
                'last_updated': datetime.now(),
                'source': 'mock_data'
            }

        return None

    def search_mutual_funds_by_name(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for mutual funds by name"""
        if not query or len(query.strip()) < 2:
            return []

        query = query.strip().lower()
        results = []

        # Common mutual fund search terms and their codes
        fund_mappings = {
            'sbi bluechip': '120465',
            'hdfc top 100': '118834',
            'icici technology': '120828',
            'axis small cap': '122639',
            'sbi': ['120465', '120828'],
            'hdfc': ['118834'],
            'icici': ['120828'],
            'axis': ['122639'],
            'bluechip': ['120465'],
            'technology': ['120828'],
            'small cap': ['122639'],
            'large cap': ['120465', '118834']
        }

        matching_codes = []
        for key, codes in fund_mappings.items():
            if key in query:
                if isinstance(codes, list):
                    matching_codes.extend(codes)
                else:
                    matching_codes.append(codes)

        # Remove duplicates
        matching_codes = list(set(matching_codes))[:limit]

        # Get data for matching funds
        for code in matching_codes:
            fund_data = self.get_mutual_fund_data(code)
            if fund_data:
                results.append(fund_data)

        # If no results, try AI suggestions
        if not results:
            ai_suggestions = self._get_mutual_fund_suggestions_from_ai(query)
            for code in ai_suggestions.get('codes', [])[:limit]:
                fund_data = self.get_mutual_fund_data(code)
                if fund_data:
                    fund_data['ai_suggested'] = True
                    results.append(fund_data)

        return results[:limit]

    def _get_mutual_fund_suggestions_from_ai(self, query: str) -> Dict:
        """Use AI to suggest mutual fund codes"""
        try:
            if not self.ai_service or not self.ai_service.is_available():
                return {'codes': []}

            prompt = f"""
            For the mutual fund search "{query}", suggest relevant Indian mutual fund scheme codes.
            Focus on popular mutual funds from SBI, HDFC, ICICI, Axis, etc.

            Return ONLY a JSON object with this exact format:
            {{
                "codes": ["CODE1", "CODE2", "CODE3"],
                "explanation": "brief explanation"
            }}

            Common codes:
            - SBI Bluechip: 120465
            - HDFC Top 100: 118834
            - ICICI Technology: 120828
            - Axis Small Cap: 122639

            Be precise and include only valid scheme codes.
            """

            response = self.ai_service.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean up response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            import json
            result = json.loads(response_text)
            return result

        except Exception:
            # Fallback codes
            fallbacks = {
                'bluechip': ['120465'],
                'large cap': ['120465', '118834'],
                'technology': ['120828'],
                'small cap': ['122639'],
                'sbi': ['120465'],
                'hdfc': ['118834'],
                'icici': ['120828'],
                'axis': ['122639']
            }

            query_lower = query.lower()
            for key, codes in fallbacks.items():
                if key in query_lower:
                    return {'codes': codes, 'explanation': f'Common funds for {query}'}

            return {'codes': [], 'explanation': 'No suggestions available'}

    def add_mutual_fund(self, scheme_code: str) -> bool:
        """Add a mutual fund to the watchlist"""
        scheme_code = scheme_code.strip()

        if scheme_code in st.session_state.get('watched_mutual_funds', []):
            st.warning(f"Mutual fund {scheme_code} is already in your watchlist!")
            return False

        # Verify fund exists
        fund_data = self.get_mutual_fund_data(scheme_code)
        if not fund_data:
            st.error(f"Could not find mutual fund data for {scheme_code}")
            return False

        if 'watched_mutual_funds' not in st.session_state:
            st.session_state.watched_mutual_funds = []

        if 'mutual_fund_data' not in st.session_state:
            st.session_state.mutual_fund_data = {}

        if 'mutual_fund_alerts' not in st.session_state:
            st.session_state.mutual_fund_alerts = {}

        st.session_state.watched_mutual_funds.append(scheme_code)
        st.session_state.mutual_fund_data[scheme_code] = fund_data
        st.session_state.mutual_fund_alerts[scheme_code] = {'buy_threshold': 0.0, 'sell_threshold': 0.0}
        st.success(f"Added {scheme_code} to your watchlist!")
        return True

    def remove_mutual_fund(self, scheme_code: str) -> bool:
        """Remove a mutual fund from the watchlist"""
        if scheme_code in st.session_state.get('watched_mutual_funds', []):
            st.session_state.watched_mutual_funds.remove(scheme_code)
            if scheme_code in st.session_state.get('mutual_fund_data', {}):
                del st.session_state.mutual_fund_data[scheme_code]
            if scheme_code in st.session_state.get('mutual_fund_alerts', {}):
                del st.session_state.mutual_fund_alerts[scheme_code]
            if scheme_code in st.session_state.get('mutual_fund_portfolio', {}):
                del st.session_state.mutual_fund_portfolio[scheme_code]
            st.success(f"Removed {scheme_code} from your watchlist!")
            return True
        return False

    def buy_mutual_fund(self, scheme_code: str, units: float, price_per_unit: float) -> bool:
        """Add mutual fund to portfolio"""
        if scheme_code not in st.session_state.get('watched_mutual_funds', []):
            st.error(f"Mutual fund {scheme_code} is not in your watchlist!")
            return False

        if units <= 0 or price_per_unit <= 0:
            st.error("Invalid units or price!")
            return False

        if 'mutual_fund_portfolio' not in st.session_state:
            st.session_state.mutual_fund_portfolio = {}

        if scheme_code in st.session_state.mutual_fund_portfolio:
            # Update existing position
            existing_units = st.session_state.mutual_fund_portfolio[scheme_code]['units']
            existing_total = st.session_state.mutual_fund_portfolio[scheme_code]['avg_price'] * existing_units
            new_total = price_per_unit * units
            total_units = existing_units + units
            avg_price = (existing_total + new_total) / total_units

            st.session_state.mutual_fund_portfolio[scheme_code]['units'] = total_units
            st.session_state.mutual_fund_portfolio[scheme_code]['avg_price'] = round(avg_price, 2)
        else:
            # New position
            st.session_state.mutual_fund_portfolio[scheme_code] = {
                'units': units,
                'avg_price': round(price_per_unit, 2),
                'buy_date': datetime.now()
            }

        st.success(f"Bought {units} units of {scheme_code} at {self.format_inr(price_per_unit)} per unit!")
        self._save_user_data_to_db()
        return True

    def sell_mutual_fund(self, scheme_code: str, units: float, price_per_unit: float) -> bool:
        """Sell mutual fund from portfolio"""
        if scheme_code not in st.session_state.get('mutual_fund_portfolio', {}):
            st.error(f"You don't own {scheme_code}!")
            return False

        if units > st.session_state.mutual_fund_portfolio[scheme_code]['units']:
            st.error("You don't have enough units!")
            return False

        # Calculate profit/loss
        cost_basis = st.session_state.mutual_fund_portfolio[scheme_code]['avg_price'] * units
        sale_value = price_per_unit * units
        profit_loss = sale_value - cost_basis

        # Update portfolio
        st.session_state.mutual_fund_portfolio[scheme_code]['units'] -= units
        if st.session_state.mutual_fund_portfolio[scheme_code]['units'] == 0:
            del st.session_state.mutual_fund_portfolio[scheme_code]

        st.success(f"Sold {units} units of {scheme_code} at {self.format_inr(price_per_unit)} per unit. P&L: {self.format_inr(profit_loss)}")
        self._save_user_data_to_db()
        return True

    def get_portfolio_value(self) -> Dict:
        """Calculate portfolio value and performance"""
        total_value = 0
        total_cost = 0
        total_positions = 0

        for symbol, position in st.session_state.portfolio.items():
            if symbol in st.session_state.stock_data:
                current_price = st.session_state.stock_data[symbol]['current_price']
                shares = position['shares']
                avg_price = position['avg_price']

                position_value = current_price * shares
                position_cost = avg_price * shares

                total_value += position_value
                total_cost += position_cost
                total_positions += 1

        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0

        return {
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'total_gain_loss': round(total_gain_loss, 2),
            'total_gain_loss_percent': round(total_gain_loss_percent, 2),
            'total_positions': total_positions
        }

    def get_mutual_fund_portfolio_value(self) -> Dict:
        """Calculate mutual fund portfolio value and performance"""
        total_value = 0
        total_cost = 0
        total_positions = 0

        for scheme_code, position in st.session_state.get('mutual_fund_portfolio', {}).items():
            if scheme_code in st.session_state.get('mutual_fund_data', {}):
                current_nav = st.session_state.mutual_fund_data[scheme_code]['nav']
                units = position['units']
                avg_price = position['avg_price']

                position_value = current_nav * units
                position_cost = avg_price * units

                total_value += position_value
                total_cost += position_cost
                total_positions += 1

        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0

        return {
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'total_gain_loss': round(total_gain_loss, 2),
            'total_gain_loss_percent': round(total_gain_loss_percent, 2),
            'total_positions': total_positions
        }

def create_chat_html(chat_history):
    """Create a self-contained HTML chat interface"""
    import re

    # Start building the HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            /* Polished chat CSS to match chat_interface.py */
            :root {
                --bg: #0b0b0b;
                --panel: #fbfbfc;
                --muted: #9aa0a6;
                --accent: #0b0b0b;
                --inverted: #ffffff;
                --soft: #f4f6f8;
            }

            html, body { height:100%; margin:0; padding:20px; background: linear-gradient(180deg, var(--bg) 0%, #121212 100%); font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: var(--soft); box-sizing: border-box; }

            .chat-messages { max-width:100%; margin:0 auto; }

            .message { margin-bottom:14px; padding:14px 18px; border-radius:12px; max-width:86%; word-wrap:break-word; line-height:1.6; font-size:15px; transition: transform .18s ease, box-shadow .18s ease; }

            .message:hover { transform: translateY(-2px); }

            .user-message { background: linear-gradient(180deg, var(--panel), #f7f8f9); color: var(--accent); margin-left:auto; text-align:right; border:1px solid rgba(11,11,11,0.06); border-bottom-right-radius:8px; box-shadow:0 6px 18px rgba(2,6,23,0.08); }

            .ai-message { background: linear-gradient(180deg, #0f0f0f, #171717); color: var(--inverted); border:1px solid rgba(255,255,255,0.04); border-bottom-left-radius:8px; box-shadow:0 6px 18px rgba(0,0,0,0.24); }

            .ai-typing { background: linear-gradient(180deg, #0f0f0f, #151515); color: var(--inverted); border:1px solid rgba(255,255,255,0.03); border-radius:12px; display:flex; align-items:center; padding:12px 16px; margin-bottom:16px; animation: fadeIn 220ms ease-in-out; }

            .typing-indicator { display:flex; align-items:center; margin-right:12px; }
            .typing-dot { width:8px; height:8px; border-radius:50%; margin:0 4px; background: rgba(255,255,255,0.9); opacity:0.9; transform:scale(0.9); animation: typing 1.2s infinite cubic-bezier(.2,.7,.2,1); }
            .typing-dot:nth-child(1){ animation-delay: -0.32s; } .typing-dot:nth-child(2){ animation-delay: -0.16s; } .typing-dot:nth-child(3){ animation-delay: 0s; }

            @keyframes typing { 0%,80%,100%{ transform:translateY(0) scale(0.9); opacity:0.6; } 40%{ transform:translateY(-4px) scale(1); opacity:1; } }

            .ai-header { font-weight:700; font-size:13px; margin-bottom:6px; color:#ffffff; }
            .message-content { padding-top:6px; }

            .empty-chat { text-align:center; color:var(--muted); margin-top:84px; }
            .empty-chat h3 { color:var(--soft); margin-bottom:10px; }

            @keyframes fadeIn { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }

            strong { font-weight:700; color:#0b0b0b; }
            em { font-style:italic; color:#6b7176; }
            h1,h2,h3 { margin:14px 0 8px 0; color:#ffffff; font-weight:700; }
            h1{ font-size:22px;} h2{ font-size:18px;} h3{ font-size:16px; }

            ul{ margin:8px 0; padding-left:20px; color:var(--muted); } li{ margin:4px 0; line-height:1.45; }
        </style>
    </head>
    <body>
        <div class="chat-messages">
    """

    if not chat_history:
        html += """
            <div class="empty-chat">
                <h3>👋 Welcome to your AI Investment Assistant!</h3>
                <p>Ask me anything about your portfolio, stocks, market trends, or investment strategies.</p>
                <p>Use the quick action buttons below or type your question in the input field!</p>
            </div>
        """
    else:
        for message in chat_history:
            if message['role'] == 'user':
                # Escape HTML for user messages
                safe_content = message["content"].replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                html += f'<div class="message user-message">{safe_content}</div>'
            else:
                # Convert markdown to HTML for AI messages
                content = message["content"]

                # Convert basic markdown to HTML
                content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
                content = re.sub(r'^### (.*)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
                content = re.sub(r'^## (.*)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
                content = re.sub(r'^# (.*)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
                content = re.sub(r'^- (.*)$', r'<li>\1</li>', content, flags=re.MULTILINE)
                content = content.replace('\n', '<br>')

                # Wrap lists
                if '<li>' in content:
                    content = '<ul>' + content + '</ul>'

                html += f'''
                <div class="message ai-message">
                    <div class="ai-header">🤖 AI Assistant</div>
                    <div class="message-content">{content}</div>
                </div>
                '''

    html += """
        </div>
        <script>
            // Auto-scroll to bottom
            window.scrollTo(0, document.body.scrollHeight);
        </script>
    </body>
    </html>
    """

    return html

def main():
    # Check authentication first
    auth_service.require_auth()

    tracker = AdvancedStockTracker()

    # Main header with enhanced styling
    st.markdown("""
    <div class="header-hero">
        <div class="main-header">📈 Advanced Stock Portfolio Tracker</div>
        <p>Track stocks, mutual funds, and get AI-powered investment insights</p>
    </div>
    """, unsafe_allow_html=True)

    # Tab management - preserve AI Insights tab when chat is active
    if 'stay_on_ai_tab' in st.session_state and st.session_state.stay_on_ai_tab:
        # Force show AI Insights tab content
        st.markdown('<div class="tab-header">🤖 AI Investment Assistant</div>', unsafe_allow_html=True)

        if not tracker.ai_service.is_available():
            st.error("🤖 AI service is not configured. Please add your GOOGLE_API_KEY to the .env file.")
            st.info("Get your free API key from: https://makersuite.google.com/app/apikey")
            with st.expander("How to set up AI"):
                st.code("""
# Add this to your .env file:
GOOGLE_API_KEY=your_api_key_here
                """)
        else:
            render_chat_interface(tracker)
        return  # Exit early to only show AI Insights

    # Create tabs normally
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 **Dashboard**",
        "📈 **Stocks**",
        "🏛️ **Mutual Funds**",
        "💼 **Portfolio**",
        "🚨 **Alerts**",
        "🤖 **AI Insights**"
    ])

    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-intro">
            <div class="sidebar-header">⚙️ Investment Controls</div>
            <p>Manage your portfolio with AI-powered insights</p>
        </div>
        """, unsafe_allow_html=True)

        # User menu
        auth_service.show_user_menu()

        asset_tab1, asset_tab2 = st.tabs(["📈 **Stocks**", "🏛️ **Mutual Funds**"])

        # Stocks Tab
        with asset_tab1:
            # Add new stock
            with st.expander("➕ Add Stock", expanded=True):
                # Step 1: Search by name
                stock_name_query = st.text_input(
                    "🔍 Search by Company Name",
                    key="stock_name_query",
                    placeholder="e.g., Apple, Google, Microsoft, Reliance..."
                )

            search_results = []
            if stock_name_query and len(stock_name_query.strip()) >= 2:
                with st.spinner("🔍 Searching stocks..."):
                    search_results = tracker.search_stocks_by_name(stock_name_query.strip(), limit=8)

                if search_results:
                    ai_count = sum(1 for r in search_results if r.get('ai_suggested', False))
                    if ai_count > 0:
                        st.success(f"🤖 AI found {len(search_results)} matching stocks for '{stock_name_query}'")
                    else:
                        st.success(f"Found {len(search_results)} matching stocks")
                else:
                    st.warning(f"No stocks found for '{stock_name_query}'. Try a different search term or enter symbol directly below.")
                    # Try AI suggestions as fallback
                    try:
                        ai_suggestions = tracker._get_stock_suggestions_from_ai(stock_name_query.strip())
                        if ai_suggestions and ai_suggestions.get('symbols'):
                            st.info(f"💡 AI suggests trying: {', '.join(ai_suggestions['symbols'][:3])}")
                    except:
                        pass

            # Step 2: Select from results
            selected_stock = None
            if search_results:
                st.markdown("### 📋 Select a Stock to Add")

                # Create options list
                options = ["Choose a stock..."]
                stock_data = {}

                for result in search_results:
                    ai_badge = "🤖 " if result.get('ai_suggested', False) else ""
                    option_text = f"{ai_badge}{result['symbol']} - {result['name']} ({tracker.format_inr(result['current_price'])})"
                    options.append(option_text)
                    stock_data[option_text] = result

                selected_option = st.selectbox(
                    "Click to add to watchlist:",
                    options=options,
                    key="selected_stock_option",
                    help="Select the stock you want to add to your watchlist"
                )

                if selected_option != "Choose a stock..." and selected_option in stock_data:
                    selected_stock = stock_data[selected_option]['symbol']

                    # Show selected stock details
                    stock_details = stock_data[selected_option]
                    st.info(f"📊 **{stock_details['name']}** ({stock_details['symbol']}) - Current: {tracker.format_inr(stock_details['current_price'])}")

                    # Auto-add button
                    if st.button(f"✅ Add {selected_stock} to Watchlist", type="primary", use_container_width=True):
                        success = tracker.add_stock(selected_stock)
                        if success:
                            tracker._save_user_data_to_db()
                            st.success(f"✅ Added {selected_stock} to your watchlist!")
                            # Clear search input and selection after successful addition
                            if "company_search" in st.session_state:
                                del st.session_state.company_search
                            if "selected_stock_option" in st.session_state:
                                del st.session_state.selected_stock_option
                            st.rerun()
                else:
                    st.info("👆 Select a stock above to add it to your watchlist")

            # Step 3: Direct symbol input as fallback
            st.markdown("### � Or Enter Symbol Directly")
            direct_symbol = st.text_input(
                "Stock Symbol",
                key="direct_symbol",
                placeholder="e.g., AAPL, GOOGL, MSFT, RELIANCE.NS...",
                help="Enter the stock ticker symbol directly if not found in search"
            ).upper().strip()

            if direct_symbol:
                selected_stock = direct_symbol

            # Add to watchlist button
            if selected_stock:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Ready to add:** {selected_stock}")
                with col2:
                    if st.button("➕ Add to Watchlist", type="primary", use_container_width=True):
                        success = tracker.add_stock(selected_stock)
                        if success:
                            tracker._save_user_data_to_db()
                            # Clear search inputs after successful addition
                            if "company_search" in st.session_state:
                                del st.session_state.company_search
                            if "selected_stock_option" in st.session_state:
                                del st.session_state.selected_stock_option
                            if "direct_symbol" in st.session_state:
                                del st.session_state.direct_symbol
                            st.rerun()
            else:
                st.info("💡 Search for a company name above or enter a stock symbol to get started!")

        # Refresh all stocks
        if st.button("🔄 Refresh All Stocks", type="secondary"):
            tracker.refresh_all_stocks()
            tracker._save_user_data_to_db()  # Save after refresh
            st.rerun()

        # Display last update time
        if st.session_state.last_update:
            st.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")

            # Stock Watchlist management
            if st.session_state.watched_stocks:
                st.markdown("### 📋 Your Stock Watchlist")
                for symbol in st.session_state.watched_stocks:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{symbol}**")
                    with col2:
                        if st.button("❌", key=f"remove_stock_{symbol}", help=f"Remove {symbol}"):
                            tracker.remove_stock(symbol)
                            tracker._save_user_data_to_db()  # Save after removing stock
                            st.rerun()

        # Mutual Funds Tab
        with asset_tab2:
            # Add new mutual fund
            with st.expander("➕ Add Mutual Fund", expanded=True):
                # Step 1: Search by name
                mf_name_query = st.text_input(
                    "🔍 Search by Fund Name",
                    key="mf_name_query",
                    placeholder="e.g., SBI Bluechip, HDFC Top 100, ICICI Technology..."
                )

                mf_search_results = []
                if mf_name_query and len(mf_name_query.strip()) >= 2:
                    with st.spinner("🔍 Searching mutual funds..."):
                        mf_search_results = tracker.search_mutual_funds_by_name(mf_name_query.strip(), limit=8)

                    if mf_search_results:
                        ai_count = sum(1 for r in mf_search_results if r.get('ai_suggested', False))
                        if ai_count > 0:
                            st.success(f"🤖 AI found {len(mf_search_results)} matching funds for '{mf_name_query}'")
                        else:
                            st.success(f"Found {len(mf_search_results)} matching funds")
                    else:
                        st.warning(f"No mutual funds found for '{mf_name_query}'. Try a different search term or enter code directly below.")
                        # Try AI suggestions as fallback
                        try:
                            ai_suggestions = tracker._get_mutual_fund_suggestions_from_ai(mf_name_query.strip())
                            if ai_suggestions and ai_suggestions.get('codes'):
                                st.info(f"💡 AI suggests trying: {', '.join(ai_suggestions['codes'][:3])}")
                        except:
                            pass

                # Step 2: Select from results
                selected_mf = None
                if mf_search_results:
                    st.markdown("### 📋 Select a Mutual Fund to Add")

                    # Create options list
                    mf_options = ["Choose a mutual fund..."]
                    mf_data = {}

                    for result in mf_search_results:
                        ai_badge = "🤖 " if result.get('ai_suggested', False) else ""
                        option_text = f"{ai_badge}{result['scheme_code']} - {result['name']} ({tracker.format_inr(result['nav'])})"
                        mf_options.append(option_text)
                        mf_data[option_text] = result

                    selected_mf_option = st.selectbox(
                        "Click to add to watchlist:",
                        options=mf_options,
                        key="selected_mf_option",
                        help="Select the mutual fund you want to add to your watchlist"
                    )

                    if selected_mf_option != "Choose a mutual fund..." and selected_mf_option in mf_data:
                        selected_mf = mf_data[selected_mf_option]['scheme_code']

                        # Show selected fund details
                        mf_details = mf_data[selected_mf_option]
                        st.info(f"📊 **{mf_details['name']}** ({mf_details['scheme_code']}) - NAV: {tracker.format_inr(mf_details['nav'])}")

                        # Auto-add button
                        if st.button(f"✅ Add {selected_mf} to Watchlist", type="primary", use_container_width=True):
                            success = tracker.add_mutual_fund(selected_mf)
                            if success:
                                tracker._save_user_data_to_db()
                                st.success(f"✅ Added {selected_mf} to your watchlist!")
                                # Clear search input and selection after successful addition
                                if "mf_name_query" in st.session_state:
                                    del st.session_state.mf_name_query
                                if "selected_mf_option" in st.session_state:
                                    del st.session_state.selected_mf_option
                                st.rerun()
                    else:
                        st.info("👆 Select a mutual fund above to add it to your watchlist")

                # Step 3: Direct code input as fallback
                st.markdown("### Or Enter Scheme Code Directly")
                direct_mf_code = st.text_input(
                    "Scheme Code",
                    key="direct_mf_code",
                    placeholder="e.g., 120465, 118834, 120828...",
                    help="Enter the mutual fund scheme code directly if not found in search"
                ).strip()

                if direct_mf_code:
                    selected_mf = direct_mf_code

                # Add to watchlist button
                if selected_mf:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Ready to add:** {selected_mf}")
                    with col2:
                        if st.button("➕ Add MF to Watchlist", type="primary", use_container_width=True):
                            success = tracker.add_mutual_fund(selected_mf)
                            if success:
                                tracker._save_user_data_to_db()
                                # Clear search inputs after successful addition
                                if "mf_name_query" in st.session_state:
                                    del st.session_state.mf_name_query
                                if "selected_mf_option" in st.session_state:
                                    del st.session_state.selected_mf_option
                                if "direct_mf_code" in st.session_state:
                                    del st.session_state.direct_mf_code
                                st.rerun()
                else:
                    st.info("💡 Search for a fund name above or enter a scheme code to get started!")

            # Refresh all mutual funds
            if st.button("🔄 Refresh All Mutual Funds", type="secondary"):
                # Refresh MF data
                if hasattr(st.session_state, 'watched_mutual_funds') and st.session_state.watched_mutual_funds:
                    for code in st.session_state.watched_mutual_funds:
                        mf_data = tracker.get_mutual_fund_data(code)
                        if mf_data:
                            st.session_state.mutual_fund_data[code] = mf_data
                    st.success(f"Refreshed {len(st.session_state.watched_mutual_funds)} mutual funds")
                    tracker._save_user_data_to_db()
                else:
                    st.info("No mutual funds in watchlist to refresh")

            # Mutual Fund Watchlist management
            if hasattr(st.session_state, 'watched_mutual_funds') and st.session_state.watched_mutual_funds:
                st.markdown("### 📋 Your Mutual Fund Watchlist")
                for code in st.session_state.watched_mutual_funds:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{code}**")
                    with col2:
                        if st.button("❌", key=f"remove_mf_{code}", help=f"Remove {code}"):
                            tracker.remove_mutual_fund(code)
                            tracker._save_user_data_to_db()  # Save after removing MF
                            st.rerun()

        # Display last update time
        if st.session_state.last_update:
            st.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
    with tab1:
        st.markdown('<div class="tab-header">📊 Portfolio Overview</div>', unsafe_allow_html=True)

        # Calculate portfolio values
        stock_portfolio_data = tracker.get_portfolio_value()
        mf_portfolio_data = tracker.get_mutual_fund_portfolio_value()

        total_value = stock_portfolio_data['total_value'] + mf_portfolio_data['total_value']
        total_cost = stock_portfolio_data['total_cost'] + mf_portfolio_data['total_cost']
        total_gain_loss = stock_portfolio_data['total_gain_loss'] + mf_portfolio_data['total_gain_loss']
        total_positions = stock_portfolio_data['total_positions'] + mf_portfolio_data['total_positions']
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0

        # Quick stats row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_value_str = tracker.format_inr(total_value)
            st.markdown(f"""
            <div class="metric-card animate-slide-in">
                <div class="stat-label">Total Value</div>
                <div class="stat-value">{total_value_str}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card animate-slide-in">
                <div class="stat-label">Total P&amp;L</div>
                <div class="stat-value">{tracker.format_inr(total_gain_loss)} ({total_gain_loss_percent:+.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card animate-slide-in">
                <div class="stat-label">Total Positions</div>
                <div class="stat-value">{total_positions}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            last_update_str = st.session_state.last_update.strftime('%H:%M:%S') if st.session_state.last_update else 'Never'
            st.markdown(f"""
            <div class="metric-card animate-slide-in">
                <div class="stat-label">Last Update</div>
                <div class="stat-label">{last_update_str}</div>
            </div>
            """, unsafe_allow_html=True)

        # Asset breakdown with enhanced cards
        st.markdown("### 📊 Asset Breakdown")
        col1, col2 = st.columns(2)

        with col1:
            stock_value_str = tracker.format_inr(stock_portfolio_data['total_value'])
            stock_change_class = "positive-change" if stock_portfolio_data['total_gain_loss'] >= 0 else "negative-change"
            stock_pl_str = tracker.format_inr(stock_portfolio_data['total_gain_loss'])
            stock_pl_percent = stock_portfolio_data['total_gain_loss_percent']
            st.markdown(f"""
            <div class="stock-card animate-slide-in">
                <div class="card-content">
                    <h3 class="section-title blue">📈 Stocks</h3>
                    <div class="row-between">
                        <span class="muted-label">Value:</span>
                        <span class="grid-value">{stock_value_str}</span>
                    </div>
                    <div class="row-between">
                        <span class="muted-label">P&amp;L:</span>
                        <span class="grid-value {stock_change_class}">{stock_pl_str} ({stock_pl_percent:+.1f}%)</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            mf_value_str = tracker.format_inr(mf_portfolio_data['total_value'])
            mf_change_class = "positive-change" if mf_portfolio_data['total_gain_loss'] >= 0 else "negative-change"
            mf_pl_str = tracker.format_inr(mf_portfolio_data['total_gain_loss'])
            mf_pl_percent = mf_portfolio_data['total_gain_loss_percent']
            st.markdown(f"""
            <div class="portfolio-card animate-slide-in">
                <div class="card-content">
                    <h3 class="section-title purple">🏛️ Mutual Funds</h3>
                    <div class="row-between">
                        <span class="muted-label">Value:</span>
                        <span class="grid-value">{mf_value_str}</span>
                    </div>
                    <div class="row-between">
                        <span class="muted-label">P&amp;L:</span>
                        <span class="grid-value {mf_change_class}">{mf_pl_str} ({mf_pl_percent:+.1f}%)</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Enhanced portfolio allocation section
        if st.session_state.portfolio or (hasattr(st.session_state, 'mutual_fund_portfolio') and st.session_state.mutual_fund_portfolio):
            st.markdown("### 📈 Portfolio Allocation")

            # Create allocation data
            allocation_data = []

            # Add stock positions
            for symbol, position in st.session_state.portfolio.items():
                if symbol in st.session_state.stock_data:
                    current_price = st.session_state.stock_data[symbol]['current_price']
                    value = position['shares'] * current_price
                    allocation_data.append({
                        'Asset': f"{symbol} (Stock)",
                        'Value': value,
                        'Type': 'Stock',
                        'Color': '#667eea'
                    })

            # Add mutual fund positions
            mf_portfolio = st.session_state.get('mutual_fund_portfolio', {})
            for code, position in mf_portfolio.items():
                mf_data = st.session_state.get('mutual_fund_data', {}).get(code)
                if mf_data:
                    current_nav = mf_data['nav']
                    value = position['units'] * current_nav
                    allocation_data.append({
                        'Asset': f"{code} (MF)",
                        'Value': value,
                        'Type': 'Mutual Fund',
                        'Color': '#764ba2'
                    })

            if allocation_data:
                df_allocation = pd.DataFrame(allocation_data)

                # Enhanced pie chart
                col1, col2 = st.columns([2, 1])

                with col1:
                    fig = px.pie(
                        df_allocation,
                        values='Value',
                        names='Asset',
                        title='Portfolio Allocation by Asset',
                        color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4ecdc4']
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#e2e8f0',
                        title_font_color='#e2e8f0'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Summary table
                    st.markdown("#### 📋 Allocation Summary")
                    for item in allocation_data:
                        percentage = (item['Value'] / sum(x['Value'] for x in allocation_data)) * 100
                        # map known colors to accent classes
                        accent_class = 'blue' if item.get('Color') == '#667eea' else 'purple' if item.get('Color') == '#764ba2' else ''
                        st.markdown(f"""
                        <div class="allocation-row">
                            <div class="flex-center">
                                <span class="accent-strip {accent_class}"></span>
                                <span class="grid-value">{item['Asset']}</span>
                            </div>
                            <span class="muted-label">{percentage:.1f}%</span>
                        </div>
                        """, unsafe_allow_html=True)

        # Enhanced recent alerts section
        if st.session_state.email_history:
            st.markdown("### 🚨 Recent Alerts")
            recent_alerts = sorted(st.session_state.email_history, key=lambda x: x['timestamp'], reverse=True)[:5]
            for alert_info in recent_alerts:
                alert = alert_info['alert']
                alert_type_color = "#10b981" if alert['type'] == 'BUY' else "#ef4444"

                with st.container():
                    # Use class-based alert rendering; add buy/sell class for accent
                    alert_class = 'alert-buy' if alert['type'] == 'BUY' else 'alert-sell'
                    st.markdown(f"""
                    <div class="alert-card animate-slide-in {alert_class}">
                        <div class="row-between-center">
                            <span class="alert-title">{alert['type']} Alert</span>
                            <span class="alert-meta">{alert_info['timestamp'].strftime('%m/%d %H:%M')}</span>
                        </div>
                        <div class="grid-value">
                            <strong>{alert['symbol']}</strong> at {tracker.format_inr(alert['current_price'])} (Threshold: {tracker.format_inr(alert['threshold'])})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # Stocks Tab
    with tab2:
        st.markdown('<div class="tab-header">📈 Stock Watchlist</div>', unsafe_allow_html=True)

        if not st.session_state.watched_stocks:
            st.info("👋 Add some stocks to your watchlist using the sidebar!")
        else:
            # Display stocks in a grid
            cols = st.columns(min(3, len(st.session_state.watched_stocks)))

            for i, symbol in enumerate(st.session_state.watched_stocks):
                with cols[i % len(cols)]:
                    stock_data = st.session_state.stock_data.get(symbol)

                    if stock_data:
                        # Enhanced stock card with better layout
                        in_portfolio = symbol in st.session_state.portfolio
                        portfolio_badge = "💼 **In Portfolio**" if in_portfolio else ""

                        # prepare values for f-string template
                        s_name = stock_data['name']
                        s_symbol = stock_data['symbol']
                        s_badge_html = f'<div class="small-pill blue">{portfolio_badge}</div>' if portfolio_badge else ''
                        s_price = tracker.format_inr(stock_data['current_price'])
                        s_change_class = "positive-change" if stock_data['change'] > 0 else "negative-change" if stock_data['change'] < 0 else "neutral-change"
                        s_change = tracker.format_inr(stock_data['change'])
                        s_change_percent = stock_data['change_percent']
                        s_open = tracker.format_inr(stock_data['open'])
                        s_high = tracker.format_inr(stock_data['high'])
                        s_low = tracker.format_inr(stock_data['low'])
                        s_volume = f"{stock_data['volume']:,}"

                        st.markdown(f"""
                        <div class="stock-card animate-slide-in">
                            <div class="row-between-start">
                                <div>
                                    <h3 class="card-title">{s_name}</h3>
                                    <p class="card-subtitle">{s_symbol}</p>
                                    {s_badge_html}
                                </div>
                                <div class="text-right">
                                    <div class="card-price">{s_price}</div>
                                    <div class="card-change {s_change_class}">{s_change} ({s_change_percent:+.2f}%)</div>
                                </div>
                            </div>

                            <div class="two-col-grid">
                                <div class="info-panel">
                                    <div class="grid-label">OPEN</div>
                                    <div class="grid-value">{s_open}</div>
                                </div>
                                <div class="info-panel">
                                    <div class="grid-label">HIGH</div>
                                    <div class="grid-value">{s_high}</div>
                                </div>
                                <div class="info-panel">
                                    <div class="grid-label">LOW</div>
                                    <div class="grid-value">{s_low}</div>
                                </div>
                                <div class="info-panel">
                                    <div class="grid-label">VOLUME</div>
                                    <div class="grid-value">{s_volume}</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Alert settings
                        with st.expander(f"⚙️ Alert Settings - {symbol}"):
                            # Get current values first
                            current_buy_threshold = st.session_state.alerts[symbol]['buy_threshold']
                            current_sell_threshold = st.session_state.alerts[symbol]['sell_threshold']

                            buy_threshold = st.slider(
                                f"Buy Alert Threshold for {symbol} ({tracker.format_inr(current_buy_threshold)})",
                                min_value=0.0,
                                max_value=float(stock_data['current_price'] * 2),
                                value=current_buy_threshold,
                                step=0.01,
                                key=f"buy_{symbol}"
                            )

                            sell_threshold = st.slider(
                                f"Sell Alert Threshold for {symbol} ({tracker.format_inr(current_sell_threshold)})",
                                min_value=0.0,
                                max_value=float(stock_data['current_price'] * 2),
                                value=current_sell_threshold,
                                step=0.01,
                                key=f"sell_{symbol}"
                            )

                            if st.button(f"Save Alerts for {symbol}", key=f"save_alerts_{symbol}"):
                                st.session_state.alerts[symbol]['buy_threshold'] = buy_threshold
                                st.session_state.alerts[symbol]['sell_threshold'] = sell_threshold
                                tracker._save_user_data_to_db()  # Save after updating alerts
                                st.success(f"Alert settings saved for {symbol}!")

                        # Quick actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"📊 View Chart - {symbol}", key=f"chart_{symbol}"):
                                st.session_state.selected_stock = symbol

                        with col2:
                            if st.button(f"🔄 Refresh - {symbol}", key=f"refresh_{symbol}"):
                                new_data = tracker.get_stock_data(symbol)
                                if new_data:
                                    st.session_state.stock_data[symbol] = new_data
                                    st.success(f"Refreshed {symbol}")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to refresh {symbol}")

        # Chart section
        if 'selected_stock' in st.session_state and st.session_state.selected_stock in st.session_state.watched_stocks:
            st.markdown("---")
            st.subheader(f"📊 {st.session_state.selected_stock} - Historical Data")

            chart_col1, chart_col2 = st.columns([3, 1])

            with chart_col2:
                period = st.selectbox(
                    "Time Period",
                    ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
                    index=2,
                    key="chart_period"
                )

            with chart_col1:
                hist_data = tracker.get_historical_data(st.session_state.selected_stock, period)

                if not hist_data.empty:
                    # Create candlestick chart
                    fig = go.Figure(data=[go.Candlestick(
                        x=hist_data.index,
                        open=hist_data['Open'],
                        high=hist_data['High'],
                        low=hist_data['Low'],
                        close=hist_data['Close'],
                        name=st.session_state.selected_stock
                    )])

                    fig.update_layout(
                        title=f"{st.session_state.selected_stock} Stock Price",
                        yaxis_title="Price (INR)",
                        xaxis_title="Date",
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No historical data available")

            if st.button("❌ Close Chart"):
                del st.session_state.selected_stock
                st.rerun()

    # Mutual Funds Tab
    with tab3:
        st.markdown('<div class="tab-header">🏛️ Mutual Fund Watchlist</div>', unsafe_allow_html=True)

        if not hasattr(st.session_state, 'watched_mutual_funds') or not st.session_state.watched_mutual_funds:
            st.info("👋 Add some mutual funds to your watchlist using the sidebar!")
        else:
            # Display mutual funds in a grid
            cols = st.columns(min(3, len(st.session_state.watched_mutual_funds)))

            for i, code in enumerate(st.session_state.watched_mutual_funds):
                with cols[i % len(cols)]:
                    mf_data = st.session_state.get('mutual_fund_data', {}).get(code)

                    if mf_data:
                        # Enhanced mutual fund card
                        in_portfolio = code in st.session_state.get('mutual_fund_portfolio', {})
                        portfolio_badge = "💼 **In Portfolio**" if in_portfolio else ""

                        mf_name = mf_data['name']
                        mf_code = code
                        mf_badge = f'<div class="small-pill purple">{portfolio_badge}</div>' if portfolio_badge else ''
                        mf_nav_str = tracker.format_inr(mf_data['nav'])
                        mf_change_class = "positive-change" if mf_data.get('change', 0) > 0 else "negative-change" if mf_data.get('change', 0) < 0 else "neutral-change"
                        mf_change_str = tracker.format_inr(mf_data.get('change', 0))
                        mf_change_percent = mf_data.get('change_percent', 0)
                        mf_category = mf_data.get('category', 'Unknown')
                        mf_amc = mf_data.get('amc', 'Unknown')

                        st.markdown(f"""
                        <div class="stock-card animate-slide-in">
                            <div class="row-between-start">
                                <div>
                                    <h3 class="card-title">{mf_name}</h3>
                                    <p class="card-subtitle">Scheme Code: {mf_code}</p>
                                    {mf_badge}
                                </div>
                                <div class="text-right">
                                    <div class="card-price card-price-purple">{mf_nav_str}</div>
                                    <div class="card-change {mf_change_class}">{mf_change_str} ({mf_change_percent:+.2f}%)</div>
                                </div>
                            </div>

                            <div class="two-col-grid">
                                <div class="info-panel">
                                    <div class="grid-label">CATEGORY</div>
                                    <div class="grid-value">{mf_category}</div>
                                </div>
                                <div class="info-panel">
                                    <div class="grid-label">AMC</div>
                                    <div class="grid-value">{mf_amc}</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Alert settings for mutual funds
                        if hasattr(st.session_state, 'mutual_fund_alerts') and code in st.session_state.mutual_fund_alerts:
                            with st.expander(f"⚙️ Alert Settings - {code}"):
                                # Get current values first
                                current_buy_threshold = st.session_state.mutual_fund_alerts[code]['buy_threshold']
                                current_sell_threshold = st.session_state.mutual_fund_alerts[code]['sell_threshold']

                                buy_threshold = st.slider(
                                    f"Buy Alert Threshold for {code} ({tracker.format_inr(current_buy_threshold)})",
                                    min_value=0.0,
                                    max_value=float(mf_data['nav'] * 2),
                                    value=current_buy_threshold,
                                    step=0.01,
                                    key=f"mf_buy_{code}"
                                )

                                sell_threshold = st.slider(
                                    f"Sell Alert Threshold for {code} ({tracker.format_inr(current_sell_threshold)})",
                                    min_value=0.0,
                                    max_value=float(mf_data['nav'] * 2),
                                    value=current_sell_threshold,
                                    step=0.01,
                                    key=f"mf_sell_{code}"
                                )

                                if st.button(f"Save MF Alerts for {code}", key=f"save_mf_alerts_{code}"):
                                    st.session_state.mutual_fund_alerts[code]['buy_threshold'] = buy_threshold
                                    st.session_state.mutual_fund_alerts[code]['sell_threshold'] = sell_threshold
                                    tracker._save_user_data_to_db()  # Save after updating alerts
                                    st.success(f"Alert settings saved for {code}!")

                        # Quick actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"📊 View Details - {code}", key=f"mf_details_{code}"):
                                st.session_state.selected_mf = code

                        with col2:
                            if st.button(f"🔄 Refresh - {code}", key=f"mf_refresh_{code}"):
                                new_data = tracker.get_mutual_fund_data(code)
                                if new_data:
                                    if 'mutual_fund_data' not in st.session_state:
                                        st.session_state.mutual_fund_data = {}
                                    st.session_state.mutual_fund_data[code] = new_data
                                    st.success(f"Refreshed {code}")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to refresh {code}")

        # MF details section
        if 'selected_mf' in st.session_state and st.session_state.selected_mf in st.session_state.get('watched_mutual_funds', []):
            st.markdown("---")
            st.subheader(f"📊 {st.session_state.selected_mf} - Fund Details")

            mf_data = st.session_state.get('mutual_fund_data', {}).get(st.session_state.selected_mf)
            if mf_data:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    **Fund Name:** {mf_data['name']}
                    **Scheme Code:** {mf_data['scheme_code']}
                    **Category:** {mf_data.get('category', 'Unknown')}
                    **AMC:** {mf_data.get('amc', 'Unknown')}
                    """)

                with col2:
                    st.markdown(f"""
                    **Current NAV:** {tracker.format_inr(mf_data['nav'])}
                    **Change:** {tracker.format_inr(mf_data.get('change', 0))} ({mf_data.get('change_percent', 0):+.2f}%)
                    **Last Updated:** {mf_data.get('last_updated', 'Unknown')}
                    """)

            if st.button("❌ Close Details"):
                del st.session_state.selected_mf
                st.rerun()

    # Portfolio Tab
    with tab4:
        st.markdown('<div class="tab-header">💼 Portfolio Management</div>', unsafe_allow_html=True)

        # Create sub-tabs for stocks and mutual funds
        port_tab1, port_tab2 = st.tabs(["📈 Stocks", "🏛️ Mutual Funds"])

        # Stock Portfolio
        with port_tab1:
            # Buy/Sell forms
            col1, col2 = st.columns(2)

            with col1:
                with st.expander("💰 Buy Stock", expanded=True):
                    buy_symbol = st.selectbox("Select Stock", st.session_state.watched_stocks, key="buy_symbol")
                    buy_shares = st.number_input("Number of Shares", min_value=1, value=1, key="buy_shares")
                    buy_price = st.number_input("Price per Share (INR)", min_value=0.01, step=0.01, key="buy_price")

                    if st.button("Buy Stock", type="primary"):
                        if buy_symbol and buy_price > 0:
                            tracker.buy_stock(buy_symbol, buy_shares, buy_price)
                            st.rerun()
                        else:
                            st.error("Please fill all fields correctly!")

            with col2:
                with st.expander("💸 Sell Stock", expanded=True):
                    owned_stocks = list(st.session_state.portfolio.keys())
                    if owned_stocks:
                        sell_symbol = st.selectbox("Select Stock", owned_stocks, key="sell_symbol")
                        max_shares = st.session_state.portfolio[sell_symbol]['shares']
                        sell_shares = st.number_input("Number of Shares", min_value=1, max_value=max_shares, value=1, key="sell_shares")
                        sell_price = st.number_input("Price per Share (INR)", min_value=0.01, step=0.01, key="sell_price")

                        if st.button("Sell Stock", type="secondary"):
                            if sell_symbol and sell_price > 0:
                                tracker.sell_stock(sell_symbol, sell_shares, sell_price)
                                st.rerun()
                            else:
                                st.error("Please fill all fields correctly!")
                    else:
                        st.info("You don't own any stocks yet!")

            # Stock Portfolio positions
            if st.session_state.portfolio:
                st.markdown("### Your Stock Positions")

                for symbol, position in st.session_state.portfolio.items():
                    if symbol in st.session_state.stock_data:
                        stock_data = st.session_state.stock_data[symbol]
                        current_price = stock_data['current_price']
                        shares = position['shares']
                        avg_price = position['avg_price']

                        current_value = current_price * shares
                        cost_basis = avg_price * shares
                        gain_loss = current_value - cost_basis
                        gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0

                        gain_class = "positive-change" if gain_loss >= 0 else "negative-change"

                        gain_class = "positive-change" if gain_loss >= 0 else "negative-change"

                        s_name = stock_data['name']
                        s_symbol = symbol
                        s_buy_date = position['buy_date'].strftime('%Y-%m-%d')
                        s_gain_class = gain_class
                        s_pnl = tracker.format_inr(gain_loss)
                        s_pnl_percent = gain_loss_percent
                        s_shares = f"{shares:,}"
                        s_avg = tracker.format_inr(avg_price)
                        s_current_value = tracker.format_inr(current_value)
                        s_current_price = tracker.format_inr(current_price)

                        st.markdown(f"""
                        <div class="portfolio-card animate-slide-in">
                            <div class="row-between-start">
                                <div>
                                    <h3 class="card-title">{s_name} ({s_symbol})</h3>
                                    <p class="card-subtitle">Purchase Date: {s_buy_date}</p>
                                </div>
                                <div class="text-right">
                                    <div class="{s_gain_class}">P&L: {s_pnl} ({s_pnl_percent:+.2f}%)</div>
                                </div>
                            </div>

                            <div class="two-col-grid">
                                <div class="info-panel">
                                    <div class="grid-label">HOLDINGS</div>
                                    <div class="grid-value">{s_shares} shares</div>
                                    <div class="muted-label">@ {s_avg} avg</div>
                                </div>

                                <div class="info-panel">
                                    <div class="grid-label">CURRENT VALUE</div>
                                    <div class="value-blue">{s_current_value}</div>
                                    <div class="muted-label">@ {s_current_price} current</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # Mutual Fund Portfolio
        with port_tab2:
            # Buy/Sell forms for mutual funds
            col1, col2 = st.columns(2)

            with col1:
                with st.expander("💰 Buy Mutual Fund", expanded=True):
                    if hasattr(st.session_state, 'watched_mutual_funds') and st.session_state.watched_mutual_funds:
                        buy_mf_code = st.selectbox("Select Mutual Fund", st.session_state.watched_mutual_funds, key="buy_mf_code")
                        buy_units = st.number_input("Number of Units", min_value=0.01, value=1.0, step=0.01, key="buy_units")
                        buy_nav = st.number_input("NAV per Unit (INR)", min_value=0.01, step=0.01, key="buy_nav")

                        if st.button("Buy Mutual Fund", type="primary"):
                            if buy_mf_code and buy_nav > 0:
                                tracker.buy_mutual_fund(buy_mf_code, buy_units, buy_nav)
                                st.rerun()
                            else:
                                st.error("Please fill all fields correctly!")
                    else:
                        st.info("Add mutual funds to your watchlist first!")

            with col2:
                with st.expander("💸 Sell Mutual Fund", expanded=True):
                    owned_mfs = list(st.session_state.get('mutual_fund_portfolio', {}).keys())
                    if owned_mfs:
                        sell_mf_code = st.selectbox("Select Mutual Fund", owned_mfs, key="sell_mf_code")
                        max_units = st.session_state.mutual_fund_portfolio[sell_mf_code]['units']
                        sell_units = st.number_input("Number of Units", min_value=0.01, max_value=max_units, value=1.0, step=0.01, key="sell_units")
                        sell_nav = st.number_input("NAV per Unit (INR)", min_value=0.01, step=0.01, key="sell_nav")

                        if st.button("Sell Mutual Fund", type="secondary"):
                            if sell_mf_code and sell_nav > 0:
                                tracker.sell_mutual_fund(sell_mf_code, sell_units, sell_nav)
                                st.rerun()
                            else:
                                st.error("Please fill all fields correctly!")
                    else:
                        st.info("You don't own any mutual funds yet!")

            # Mutual Fund Portfolio positions
            mf_portfolio = st.session_state.get('mutual_fund_portfolio', {})
            if mf_portfolio:
                st.markdown("### Your Mutual Fund Positions")

                for code, position in mf_portfolio.items():
                    mf_data = st.session_state.get('mutual_fund_data', {}).get(code)
                    if mf_data:
                        current_nav = mf_data['nav']
                        units = position['units']
                        avg_price = position['avg_price']

                        current_value = current_nav * units
                        cost_basis = avg_price * units
                        gain_loss = current_value - cost_basis
                        gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0

                        gain_class = "positive-change" if gain_loss >= 0 else "negative-change"

                        gain_class = "positive-change" if gain_loss >= 0 else "negative-change"

                        mf_name = mf_data['name']
                        mf_code = code
                        mf_buy_date = position['buy_date'].strftime('%Y-%m-%d')
                        mf_gain_class = gain_class
                        mf_pnl = tracker.format_inr(gain_loss)
                        mf_pnl_percent = gain_loss_percent
                        mf_units = f"{units:.2f}"
                        mf_avg = tracker.format_inr(avg_price)
                        mf_current_value = tracker.format_inr(current_value)
                        mf_nav = tracker.format_inr(current_nav)

                        st.markdown(f"""
                        <div class="portfolio-card animate-slide-in">
                            <div class="row-between-start">
                                <div>
                                    <h3 class="card-title">{mf_name} ({mf_code})</h3>
                                    <p class="card-subtitle">Purchase Date: {mf_buy_date}</p>
                                </div>
                                <div class="text-right">
                                    <div class="{mf_gain_class}">P&L: {mf_pnl} ({mf_pnl_percent:+.2f}%)</div>
                                </div>
                            </div>

                            <div class="two-col-grid">
                                <div class="info-panel">
                                    <div class="grid-label">HOLDINGS</div>
                                    <div class="grid-value">{mf_units} units</div>
                                    <div class="muted-label">@ {mf_avg} avg NAV</div>
                                </div>

                                <div class="info-panel">
                                    <div class="grid-label">CURRENT VALUE</div>
                                    <div class="value-purple">{mf_current_value}</div>
                                    <div class="muted-label">@ {mf_nav} current NAV</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    # Alerts Tab
    with tab5:
        st.markdown('<div class="tab-header">🚨 Alert Management</div>', unsafe_allow_html=True)

        # Current alerts
        st.markdown("### Current Alert Settings")
        if st.session_state.alerts:
            for symbol, alert_settings in st.session_state.alerts.items():
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{symbol}**")
                    with col2:
                        st.write(f"Buy: {tracker.format_inr(alert_settings['buy_threshold'])}")
                    with col3:
                        st.write(f"Sell: {tracker.format_inr(alert_settings['sell_threshold'])}")

        # Email history
        if st.session_state.email_history:
            st.markdown("### Email Alert History")
            for alert_info in sorted(st.session_state.email_history, key=lambda x: x['timestamp'], reverse=True):
                alert = alert_info['alert']
                with st.container():
                    st.markdown(f"""
                    <div class="success-card">
                        <strong>{alert['type']} Alert Sent:</strong> {alert['symbol']} at {tracker.format_inr(alert['current_price'])}
                        (Threshold: {tracker.format_inr(alert['threshold'])}) - {alert_info['timestamp'].strftime('%m/%d/%Y %H:%M:%S')}
                    </div>
                    """, unsafe_allow_html=True)

        # Email configuration
        st.markdown("### Email Configuration")
        with st.expander("Configure Email Settings"):
            st.info("Set these environment variables in your .env file:")
            st.code("""
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient_email@gmail.com
            """)

    # AI Insights Tab
    with tab6:
        st.markdown('<div class="tab-header">🤖 AI Investment Assistant</div>', unsafe_allow_html=True)

        if not tracker.ai_service.is_available():
            st.error("🤖 AI service is not configured. Please add your GOOGLE_API_KEY to the .env file.")
            st.info("Get your free API key from: https://makersuite.google.com/app/apikey")
            with st.expander("How to set up AI"):
                st.code("""
# Add this to your .env file:
GOOGLE_API_KEY=your_api_key_here
                """)
        else:
            render_chat_interface(tracker)



if __name__ == "__main__":
    main()

