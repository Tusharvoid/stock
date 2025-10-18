import streamlit as st
import streamlit.components.v1 as components
import re
from theme import get_theme_css

def create_chat_html(chat_history, ai_typing=False):
    """Create a self-contained HTML chat interface"""
    # Start building the HTML
    # Embed shared theme CSS into the chat HTML head
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {get_theme_css()}
        <style>
            /* Chat-specific overrides that layer on top of the shared theme */
            html, body {{ height: 100%; margin: 0; padding: 20px; background: linear-gradient(180deg, var(--bg) 0%, #121212 100%); font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: var(--soft); box-sizing: border-box; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }}

            .chat-messages {{ max-width: 100%; margin: 0 auto; }}

            .message {{ margin-bottom: 14px; padding: 14px 18px; border-radius: 12px; max-width: 86%; word-wrap: break-word; line-height: 1.6; font-size: 15px; transition: transform .18s ease, box-shadow .18s ease; will-change: transform; }}

            .message:hover {{ transform: translateY(-2px); }}

            .user-message {{ background: linear-gradient(180deg,#081222,#0b1624); color: var(--accent); margin-left: auto; text-align: right; border: 1px solid rgba(255,255,255,0.02); border-bottom-right-radius: 8px; box-shadow: 0 8px 26px rgba(2,6,23,0.6); }}

            .ai-message {{ background: linear-gradient(180deg,#071223,#08162a); color: var(--accent); border: 1px solid rgba(255,255,255,0.02); border-bottom-left-radius: 8px; box-shadow: 0 8px 26px rgba(2,6,23,0.6); }}

            .ai-typing {{ background: linear-gradient(180deg, #0f0f0f, #151515); color: var(--soft); border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; display: flex; align-items: center; padding: 12px 16px; margin-bottom: 16px; animation: fadeIn 220ms ease-in-out; }}

            .typing-indicator {{ display:flex; align-items:center; margin-right:12px; }}
            .typing-dot {{ width:8px; height:8px; border-radius:50%; margin: 0 4px; background: rgba(255,255,255,0.9); opacity: 0.9; transform: scale(0.9); animation: typing 1.2s infinite cubic-bezier(.2,.7,.2,1); }}
            .typing-dot:nth-child(1){{ animation-delay: -0.32s; }} .typing-dot:nth-child(2){{ animation-delay: -0.16s; }} .typing-dot:nth-child(3){{ animation-delay: 0s; }}

            @keyframes typing {{ 0%,80%,100%{{ transform: translateY(0) scale(0.9); opacity:0.6; }} 40%{{ transform: translateY(-4px) scale(1); opacity:1; }} }}

            .ai-header {{ font-weight:700; font-size:13px; margin-bottom:6px; color:var(--soft); }}
            .message-content {{ padding-top:6px; }}

            .empty-chat {{ text-align:center; color: var(--muted); margin-top: 84px; }}
            .empty-chat h3 {{ color: var(--soft); margin-bottom: 10px; }}

            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}

            /* Typography for converted markdown */
            strong {{ font-weight:700; color:var(--accent); }}
            em {{ font-style:italic; color:#6b7176; }}
            h1,h2,h3 {{ margin:14px 0 8px 0; color:var(--soft); font-weight:700; }}
            h1{{ font-size:22px; }} h2{{ font-size:18px; }} h3{{ font-size:16px; }}

            ul{{ margin:8px 0; padding-left:20px; color:var(--muted); }} li{{ margin:4px 0; line-height:1.45; }}
        </style>
    </head>
    <body>
        <div class="chat-messages">
    """

    if not chat_history and not ai_typing:
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

        # Add typing indicator if AI is typing
        if ai_typing:
            html += '''
            <div class="ai-typing">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <div class="ai-header">🤖 AI is typing...</div>
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

def send_message():
    """Callback function to send a message"""
    if st.session_state.get('user_input', '').strip():
        user_message = st.session_state.user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_message})

        # Set flag to stay on AI Insights tab
        st.session_state.stay_on_ai_tab = True

        # Set flag to show AI is typing
        st.session_state.ai_typing = True

        # Generate AI response
        with st.spinner("🤖 AI is thinking..."):
            ai_response = st.session_state.get('tracker').generate_ai_response(user_message)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

        # Clear typing flag
        st.session_state.ai_typing = False

def clear_chat():
    """Callback function to clear chat history"""
    st.session_state.chat_history = []
    st.session_state.ai_typing = False
    st.session_state.stay_on_ai_tab = True

def quick_action_analyze():
    """Quick action: Analyze portfolio"""
    user_message = "Can you analyze my current portfolio and give me insights?"
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    st.session_state.stay_on_ai_tab = True
    st.session_state.ai_typing = True
    with st.spinner("🤖 AI is analyzing your portfolio..."):
        analysis = st.session_state.get('tracker').ai_service.analyze_portfolio(
            st.session_state.portfolio,
            st.session_state.stock_data
        )
    st.session_state.chat_history.append({"role": "assistant", "content": analysis})
    st.session_state.ai_typing = False

def quick_action_predict():
    """Quick action: Predict stock movement"""
    if st.session_state.watched_stocks:
        selected = st.session_state.watched_stocks[0]
        user_message = f"Can you predict the movement for {selected}?"
        st.session_state.chat_history.append({"role": "user", "content": user_message})

        st.session_state.stay_on_ai_tab = True
        st.session_state.ai_typing = True
        with st.spinner(f"🤖 AI is predicting {selected} movement..."):
            stock_data = st.session_state.stock_data.get(selected, {})
            portfolio_data = st.session_state.portfolio.get(selected)
            prediction = st.session_state.get('tracker').ai_service.predict_stock_movement(selected, stock_data, portfolio_data)
        st.session_state.chat_history.append({"role": "assistant", "content": prediction})
        st.session_state.ai_typing = False

def quick_action_sentiment():
    """Quick action: Market sentiment"""
    user_message = "What's the current market sentiment?"
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    st.session_state.stay_on_ai_tab = True
    st.session_state.ai_typing = True
    with st.spinner("🤖 AI is analyzing market sentiment..."):
        sentiment = st.session_state.get('tracker').ai_service.get_market_sentiment()
    st.session_state.chat_history.append({"role": "assistant", "content": sentiment})
    st.session_state.ai_typing = False

def quick_action_strategy():
    """Quick action: Investment strategy"""
    user_message = "Can you suggest an investment strategy for me?"
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    st.session_state.stay_on_ai_tab = True
    st.session_state.ai_typing = True
    with st.spinner("🤖 AI is creating your investment strategy..."):
        strategy = st.session_state.get('tracker').ai_service.get_investment_strategy("moderate", "medium-term (3-7 years)")
    st.session_state.chat_history.append({"role": "assistant", "content": strategy})
    st.session_state.ai_typing = False

def render_chat_interface(tracker):
    """Render the complete chat interface"""
    # Initialize chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'ai_typing' not in st.session_state:
        st.session_state.ai_typing = False

    # Store tracker in session state for callbacks
    st.session_state.tracker = tracker

    # Add a back button to return to normal tab view
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Back to Dashboard", key="back_to_dashboard"):
            if 'stay_on_ai_tab' in st.session_state:
                del st.session_state.stay_on_ai_tab
            st.rerun()
    with col_title:
        st.markdown('<div class="tab-header">🤖 AI Investment Assistant</div>', unsafe_allow_html=True)

    # Chat window first (above input)
    chat_html = create_chat_html(st.session_state.chat_history, st.session_state.ai_typing)
    components.html(chat_html, height=750, scrolling=True)

    # Input area below the chat
    st.markdown("---")  # Separator

    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("📊 Analyze My Portfolio", key="quick_portfolio", on_click=quick_action_analyze)

    with col2:
        st.button("🔮 Predict Stock Movement", key="quick_predict", on_click=quick_action_predict)

    with col3:
        st.button("🌍 Market Sentiment", key="quick_sentiment", on_click=quick_action_sentiment)

    with col4:
        st.button("💡 Investment Strategy", key="quick_strategy", on_click=quick_action_strategy)

    # User input
    user_input = st.text_input(
        "💬 Ask me anything about your investments...",
        key="user_input",
        placeholder="e.g., 'Should I buy more AAPL?' or 'What's happening with tech stocks?'",
        label_visibility="collapsed"
    )

    col_send, col_clear = st.columns([4, 1])
    with col_send:
        st.button("📤 Send", type="primary", use_container_width=True, on_click=send_message)
    with col_clear:
        st.button("🗑️ Clear Chat", use_container_width=True, on_click=clear_chat)
