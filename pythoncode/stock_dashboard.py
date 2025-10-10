import streamlit as st
import pandas as pd

def show_stock_dashboard():
    st.subheader("Stock Dashboard")
    # Placeholder data
    data = {
        "Stock": ["AAPL", "GOOGL", "TSLA"],
        "Change %": [1.2, -0.5, 2.1]
    }
    df = pd.DataFrame(data)
    st.dataframe(df)
