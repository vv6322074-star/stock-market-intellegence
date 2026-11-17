
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Stock Price Analysis",
    page_icon="📈",
    layout="wide"
)

# Load data
tcs = pd.read_csv("tcs.csv")
apple = pd.read_csv("apple.csv")
for df in [tcs, apple]:
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)

    df["Moving_Average"] = df["Close"].rolling(window=7).mean()

    df["Daily_Return"] = df["Close"].pct_change() * 100
# Styling
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#07152f,#101d3d);
    color: white;
}
[data-testid="stSidebar"] {
    background-color: #101a35;
}
h1, h2, h3, p, label {
    color: white !important;
}
div[data-testid="stMetric"] {
    background: #172c50;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #315b91;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📈 Stock Analysis")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "TCS Analysis", "Apple Analysis",
     "Comparison", "About Project"]
)

st.sidebar.markdown("---")
st.sidebar.info("Smart Analysis\nBetter Decisions")

def show_analysis(df, name, currency):
    st.subheader(name + " Stock Analysis")

    latest = df["Close"].dropna().iloc[-1]

    c1, c2, c3 = st.columns(3)
    c1.metric("Latest Price", f"{currency}{latest:.2f}")
    c2.metric("Highest Price", f"{currency}{df['Close'].max():.2f}")
    c3.metric("Lowest Price", f"{currency}{df['Close'].min():.2f}")

    st.subheader("Stock Price Trend")
    st.line_chart(
        df.set_index("Date")[["Close", "Moving_Average"]]
    )

    st.subheader("Daily Returns")
    st.line_chart(
        df.set_index("Date")["Daily_Return"]
    )

    volatility = df["Daily_Return"].std()
    st.metric("Daily Volatility", f"{volatility:.2f}%")

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        file_name=name.lower().replace(" ", "_") + ".csv",
        mime="text/csv"
    )

# Home
if page == "Home":
    st.title("📈 STOCK PRICE ANALYSIS USING PYTHON")
    st.caption("Analyze • Compare • Understand")

    st.subheader("Company Overview")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("TCS Latest Price",
                  f"₹{tcs['Close'].dropna().iloc[-1]:.2f}")

    with c2:
        st.metric("Apple Latest Price",
                  f"${apple['Close'].dropna().iloc[-1]:.2f}")

    st.subheader("TCS Stock Price Trend")
    st.line_chart(tcs.set_index("Date")["Close"])

    st.subheader("Apple Stock Price Trend")
    st.line_chart(apple.set_index("Date")["Close"])

    st.subheader("Comparison Overview")

    comparison = pd.DataFrame({
        "TCS": [
            tcs["Daily_Return"].std(),
            tcs["Daily_Return"].mean()
        ],
        "Apple": [
            apple["Daily_Return"].std(),
            apple["Daily_Return"].mean()
        ]
    }, index=["Volatility (%)", "Average Daily Return (%)"])

    st.bar_chart(comparison)

    st.subheader("Correlation Analysis")

    joined = pd.merge(
        tcs[["Date", "Daily_Return"]],
        apple[["Date", "Daily_Return"]],
        on="Date",
        suffixes=("_TCS", "_Apple")
    ).dropna()

    corr = joined["Daily_Return_TCS"].corr(
        joined["Daily_Return_Apple"]
    )

    st.metric("TCS vs Apple Correlation", f"{corr:.4f}")

# TCS
elif page == "TCS Analysis":
    show_analysis(tcs, "TCS", "₹")

# Apple
elif page == "Apple Analysis":
    show_analysis(apple, "Apple", "$")

# Comparison
elif page == "Comparison":
    st.title("⚖️ TCS vs Apple Comparison")

    st.subheader("Daily Returns Comparison")

    joined = pd.merge(
        tcs[["Date", "Daily_Return"]],
        apple[["Date", "Daily_Return"]],
        on="Date",
        suffixes=("_TCS", "_Apple")
    ).dropna()

    st.line_chart(
        joined.set_index("Date")
        [["Daily_Return_TCS", "Daily_Return_Apple"]]
    )

    st.subheader("Volatility Comparison")

    volatility = pd.DataFrame({
        "Company": ["TCS", "Apple"],
        "Volatility": [
            tcs["Daily_Return"].std(),
            apple["Daily_Return"].std()
        ]
    }).set_index("Company")

    st.bar_chart(volatility)

    st.metric(
        "Correlation",
        f"{joined['Daily_Return_TCS'].corr(joined['Daily_Return_Apple']):.4f}"
    )

# About
elif page == "About Project":
    st.title("ℹ️ About This Project")

    st.write("""
    This project performs stock price analysis of
    Tata Consultancy Services (TCS) and Apple Inc.
    using Python.

    **Features:**
    - Stock Price Analysis
    - Daily Returns Analysis
    - Moving Average Analysis
    - Volatility Analysis
    - Company Comparison
    - Correlation Analysis

    **Technologies Used:**
    Python, Pandas, Matplotlib, Streamlit
    """)

    st.success("Stock Price Analysis Using Python")
