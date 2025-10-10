import streamlit as st
import pandas as pd

def show_mutual_fund_dashboard():
    st.subheader("Mutual Fund Dashboard")
    # Placeholder data
    data = {
        "Fund": ["ABC Growth", "XYZ Value"],
        "Units": [100, 200],
        "NAV": [25.5, 18.2]
    }
    df = pd.DataFrame(data)
    st.dataframe(df)
