import streamlit as st

# Sidebar navigation
st.sidebar.title("Navigation")
pages = [
    "Landing Page",
    "Main Portfolio",
    "Mutual Fund Dashboard",
    "Stock Dashboard",
    "Real-Time Stock Charts"
]
page = st.sidebar.radio("Go to", pages)

# Import feature modules
from holdings_table import show_holdings_table
from portfolio_chart import show_portfolio_chart
from mutual_fund_dashboard import show_mutual_fund_dashboard
from stock_dashboard import show_stock_dashboard
from real_time_stock_charts import show_real_time_stock_charts
# Page content rendering
if page == "Landing Page":
    st.title("Landing Page")
    st.write("Welcome to the Stock Portfolio App!")
    st.info("Navigate using the sidebar to explore features.")

elif page == "Main Portfolio":
    st.title("Main Portfolio")
    st.write("Portfolio overview and holdings table.")
    show_holdings_table()
    show_portfolio_chart()

elif page == "Mutual Fund Dashboard":
    show_mutual_fund_dashboard()

elif page == "Stock Dashboard":
    show_stock_dashboard()

elif page == "Real-Time Stock Charts":
    show_real_time_stock_charts()

import streamlit as st
from user_auth import authenticate, register_user, get_user_stocks, add_user_stock

st.title("Stock Portfolio App - Login")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")
    with tab2:
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            if register_user(new_username, new_password):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists.")
else:
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    st.header("Your Stock Portfolio")
    stocks = get_user_stocks(st.session_state.username)
    st.write("Your stocks:")
    st.table(stocks)
    st.subheader("Add a new stock")
    stock_name = st.text_input("Stock Name")
    shares = st.number_input("Shares", min_value=1, step=1)
    price = st.number_input("Price", min_value=0.0, step=0.01)
    if st.button("Add Stock"):
        if stock_name:
            stock = {"Stock": stock_name, "Shares": shares, "Price": price}
            add_user_stock(st.session_state.username, stock)
            st.success("Stock added!")
            st.experimental_rerun()
        else:
            st.error("Please enter a stock name.")
import streamlit as st

# Sidebar navigation

st.sidebar.title("Navigation")
pages = [
    "Landing Page",
    "Main Portfolio",
    "Mutual Fund Dashboard",
    "Stock Dashboard",
    "Real-Time Stock Charts"
]
page = st.sidebar.radio("Go to", pages)

# Import feature modules
from holdings_table import show_holdings_table
from portfolio_chart import show_portfolio_chart
from mutual_fund_dashboard import show_mutual_fund_dashboard
from stock_dashboard import show_stock_dashboard
from real_time_stock_charts import show_real_time_stock_charts

# Page content rendering
if page == "Landing Page":
    st.title("Landing Page")
    st.write("Welcome to the Stock Portfolio App!")
    st.info("Navigate using the sidebar to explore features.")

elif page == "Main Portfolio":
    st.title("Main Portfolio")
    st.write("Portfolio overview and holdings table.")
    show_holdings_table()
    show_portfolio_chart()

elif page == "Mutual Fund Dashboard":
    show_mutual_fund_dashboard()

elif page == "Stock Dashboard":
    show_stock_dashboard()

elif page == "Real-Time Stock Charts":
    show_real_time_stock_charts()
