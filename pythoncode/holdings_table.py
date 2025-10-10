import streamlit as st
import pandas as pd

def show_holdings_table():
    st.subheader("Holdings Table")
    # Placeholder data
    data = {
        "Stock": ["AAPL", "GOOGL", "TSLA"],
        "Shares": [10, 5, 8],
        "Price": [175.0, 2800.0, 750.0]
    }
    df = pd.DataFrame(data)
    st.dataframe(df)
