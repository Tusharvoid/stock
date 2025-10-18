import google.generativeai as genai
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()
try:
    # Apply embedded defaults if present
    from secrets_config import apply_to_env
    apply_to_env()
except Exception:
    pass

class GeminiAIService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    def is_available(self) -> bool:
        """Check if Gemini AI is available"""
        return self.model is not None

    def get_stock_insights(self, symbol: str, stock_data: Dict[str, Any]) -> Optional[str]:
        """Get AI insights for a specific stock"""
        if not self.is_available():
            return "🤖 **AI Assistant:** Oops! I'm having trouble connecting right now. Please check your GOOGLE_API_KEY so I can help you with stock insights!"

        try:
            prompt = f"""
            You are a friendly, knowledgeable AI investment assistant having a casual chat with an investor. Respond in a natural, conversational way like you're texting a friend about stocks.

            **CHAT CONTEXT:**
            The user is asking about {symbol} stock. Here's the current data:
            - Company: {stock_data.get('name', 'Unknown')}
            - Current Price: ${stock_data.get('current_price', 0):.2f}
            - Today's Change: ${stock_data.get('change', 0):.2f} ({stock_data.get('change_percent', 0):.2f}%)
            - Day Range: ${stock_data.get('low', 0):.2f} - ${stock_data.get('high', 0):.2f}
            - 52-Week Range: ${stock_data.get('52_week_low', 0):.2f} - ${stock_data.get('52_week_high', 0):.2f}

            **RESPONSE FORMAT:**
            Start with: "🤖 **AI Assistant:** Hey! Let me break down {symbol} for you:"

            Then structure your response like a friendly chat:
            � **Quick Take:** [2-3 sentence overview]
            📊 **What's Happening:** [technical analysis in simple terms]
            🎯 **My Thoughts:** [personal recommendation with confidence level]
            ⚠️ **Watch Out For:** [1-2 key risks]
            💡 **Bottom Line:** [clear buy/hold/sell recommendation]

            Keep it conversational, use emojis, and make it feel like a helpful friend giving advice over coffee. Be encouraging and realistic!
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"🤖 **AI Assistant:** 😅 Sorry, I'm having technical difficulties right now. Let's try again in a moment! (Error: {str(e)})"

    def analyze_portfolio(self, portfolio: Dict[str, Any], stock_data: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """Analyze the user's entire portfolio and provide recommendations"""
        if not self.is_available():
            return "🤖 **AI Assistant:** Hi! I'm having trouble connecting right now. Please check your GOOGLE_API_KEY setup so I can help with your portfolio!"

        try:
            portfolio_summary = []
            total_value = 0
            total_cost = 0

            for symbol, position in portfolio.items():
                if symbol in stock_data:
                    current_price = stock_data[symbol]['current_price']
                    shares = position['shares']
                    avg_price = position['avg_price']

                    position_value = current_price * shares
                    position_cost = avg_price * shares
                    gain_loss = position_value - position_cost
                    gain_loss_percent = (gain_loss / position_cost * 100) if position_cost > 0 else 0

                    total_value += position_value
                    total_cost += position_cost

                    emoji = "📈" if gain_loss >= 0 else "📉"
                    portfolio_summary.append(f"• {emoji} **{symbol}:** {shares} shares (${position_value:.0f} value, {gain_loss_percent:+.1f}%)")

            total_gain_loss = total_value - total_cost
            total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0

            emoji = "🎉" if total_gain_loss >= 0 else "😔"
            status = "winning" if total_gain_loss >= 0 else "taking a hit"

            prompt = f"""
            You are a friendly AI portfolio advisor chatting with an investor about their holdings. Respond naturally like you're having a conversation.

            **CHAT CONTEXT:**
            User's portfolio summary:
            💰 Total Value: ${total_value:.0f}
            💵 Total Invested: ${total_cost:.0f}
            {emoji} Overall: ${total_gain_loss:.0f} ({total_gain_loss_percent:+.1f}%) - currently {status}

            Holdings breakdown:
            {chr(10).join(portfolio_summary)}

            **RESPONSE FORMAT:**
            Start with: "🤖 **AI Assistant:** Hey! Let me take a look at your portfolio:"

            Structure like a friendly chat:
            � **Overall Health:** [quick assessment in 1-2 sentences]
            🎯 **Standouts:** [mention 1-2 positions doing well or needing attention]
            ⚖️ **Risk Check:** [diversification and risk assessment]
            � **My Suggestions:** [2-3 specific, actionable recommendations]
            🎪 **Next Moves:** [what to consider doing now]

            Keep it conversational, encouraging, and practical - like a knowledgeable friend giving portfolio advice!
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"🤖 **AI Assistant:** 😅 Oops! I had trouble analyzing your portfolio. Let's try again in a moment. Error: {str(e)}"

    def predict_stock_movement(self, symbol: str, stock_data: Dict[str, Any], portfolio_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Predict stock movement and provide buy/sell recommendations"""
        if not self.is_available():
            return "🤖 **AI Assistant:** Hi! My crystal ball is a bit foggy right now. Please check your GOOGLE_API_KEY so I can give you predictions!"

        try:
            # Get historical data for better analysis
            import yfinance as yf
            stock = yf.Ticker(symbol)
            hist = stock.history(period="3mo")

            if hist.empty:
                return f"🤖 **AI Assistant:** 😅 I couldn't fetch historical data for {symbol} right now. This sometimes happens with certain stocks. Try again later!"

            # Calculate some technical indicators
            recent_prices = hist['Close'].tail(30)
            price_trend = "📈 upward" if recent_prices.iloc[-1] > recent_prices.iloc[0] else "📉 downward"
            volatility = recent_prices.std() / recent_prices.mean() * 100
            avg_volume = hist['Volume'].tail(30).mean()

            portfolio_info = ""
            if portfolio_data and symbol in portfolio_data:
                position = portfolio_data[symbol]
                current_price = stock_data.get('current_price', 0)
                avg_price = position['avg_price']
                shares = position['shares']
                unrealized_pl = (current_price - avg_price) * shares
                unrealized_pl_percent = (unrealized_pl / (avg_price * shares)) * 100

                emoji = "😊" if unrealized_pl >= 0 else "😟"
                portfolio_info = f"You own {shares} shares (avg: ${avg_price:.2f}, {emoji} P&L: {unrealized_pl_percent:+.1f}%)"

            prompt = f"""
            You are a friendly AI investment assistant having a quick chat about {symbol} stock. Give direct, actionable advice like a trusted friend.

            **QUICK FACTS:**
            📊 {symbol} at ${stock_data.get('current_price', 0):.2f} ({stock_data.get('change_percent', 0):.2f}% today)
            � 3-month trend: {price_trend}
            🎢 Volatility: {volatility:.1f}%
            {portfolio_info}

            **CHAT RESPONSE FORMAT:**
            Start with: "🤖 **AI Assistant:** Quick take on {symbol}:"

            Keep it super conversational and direct:
            💬 **My Prediction:** [1-2 week outlook in simple terms]
            🎯 **Recommendation:** [BUY/HOLD/SELL with confidence level]
            💰 **Price Targets:** [if buying/selling, suggest entry/exit prices]
            ⚠️ **Risk Level:** [Low/Medium/High with quick reason]
            💡 **Quick Tip:** [one actionable suggestion]

            Be direct and helpful - like texting a friend for quick investment advice!
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"🤖 **AI Assistant:** 😅 My crystal ball got a little cloudy while predicting {symbol}. Let's try again soon! Error: {str(e)}"

    def get_market_sentiment(self) -> Optional[str]:
        """Get overall market sentiment and outlook"""
        if not self.is_available():
            return "🤖 **AI Assistant:** Hello! I'm having connection issues right now. Please check your GOOGLE_API_KEY so I can share market insights!"

        try:
            prompt = """
            You are a friendly AI market analyst chatting casually about the current market mood. Respond like you're texting a friend about market conditions.

            **CHAT RESPONSE FORMAT:**
            Start with: "🤖 **AI Assistant:** Hey! Market check-in:"

            Keep it conversational and timely:
            🌟 **Current Mood:** [bullish/bearish/neutral with quick reason]
            � **Big Stories:** [2-3 key drivers in simple terms]
            📊 **Sector Winners:** [which areas are hot right now]
            ⚠️ **Watch Outs:** [1-2 things to be careful about]
            💡 **My Take:** [quick strategy suggestion for most investors]

            Make it feel like a friendly market update over coffee! ☕
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"🤖 **AI Assistant:** 😅 The market's being a bit mysterious today! I couldn't get the latest sentiment. Let's try again soon. Error: {str(e)}"

    def get_investment_strategy(self, risk_tolerance: str = "moderate", investment_horizon: str = "medium") -> Optional[str]:
        """Provide personalized investment strategy recommendations"""
        if not self.is_available():
            return "🤖 **AI Assistant:** Hi there! I'm ready to help with investment strategies, but I need your GOOGLE_API_KEY to be configured first!"

        try:
            # Convert the inputs to more friendly language
            risk_descriptions = {
                "conservative": "play-it-safe type",
                "moderate": "balanced investor",
                "aggressive": "growth-seeking adventurer"
            }

            horizon_descriptions = {
                "short-term (1-3 years)": "need money soon",
                "medium-term (3-7 years)": "have some time",
                "long-term (7+ years)": "thinking long game"
            }

            risk_desc = risk_descriptions.get(risk_tolerance, risk_tolerance)
            horizon_desc = horizon_descriptions.get(investment_horizon, investment_horizon)

            prompt = f"""
            You are a friendly AI investment coach giving personalized advice. Respond like you're having a casual conversation about investment strategy.

            **INVESTOR PROFILE:**
            🎢 {risk_tolerance} risk tolerance ({risk_desc})
            ⏰ {investment_horizon} horizon ({horizon_desc})

            **CHAT RESPONSE FORMAT:**
            Start with: "🤖 **AI Assistant:** Perfect! For your {risk_tolerance} style with {horizon_desc}:"

            Keep it conversational and practical:
            💰 **Asset Mix:** [how to spread investments simply]
            🏢 **Good Sectors:** [2-3 sectors that fit this profile]
            🛡️ **Smart Moves:** [risk management tips]
            🔄 **Check Frequency:** [how often to review]
            � **Top Tips:** [3 quick, actionable suggestions]

            Make it feel like personalized coaching from a trusted advisor! 🎯
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"🤖 **AI Assistant:** 😅 I had trouble crafting your investment strategy. Let's give it another shot! Error: {str(e)}"
