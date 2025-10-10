import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def show_portfolio_chart():
    st.subheader("Portfolio Chart")
    # Placeholder chart
    labels = ['AAPL', 'GOOGL', 'TSLA']
    sizes = [10, 5, 8]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    st.pyplot(fig)
