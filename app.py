
import streamlit as st
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LinearRegression
companies = {
    "TCS": "TCS.NS",
    "Apple": "AAPL",
    "Reliance": "RELIANCE.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Microsoft": "MSFT",
    "Amazon": "AMZN"
}
@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    stock = yf.download(
        ticker,
        period="1y",
        interval="1d",
        progress=False
    )

    if not stock.empty:
        stock.columns = stock.columns.get_level_values(0)
        stock = stock.reset_index()

    return stock

def predict_stock_price(stock_data):
    data = stock_data[["Close"]].dropna().copy()

    data["Day"] = range(len(data))

    X = data[["Day"]]
    y = data["Close"]

    model = LinearRegression()
    model.fit(X, y)

    future_days = pd.DataFrame({
        "Day": range(len(data), len(data) + 7)
    })

    predictions = model.predict(future_days)

    return predictions


import numpy as np

st.set_page_config(
    page_title="Stock Price Analysis",
    page_icon="📈",
    layout="wide"
) 

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #172554);
    color: white;
}

h1, h2, h3 {
    color: #60a5fa;
}

div[data-testid="stMetric"] {
    background: #1e293b;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)



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
if "pending_page" in st.session_state:
    st.session_state["page_navigation"] 
= st.session_state.pop("pending_page")

st.sidebar.title("📈 Stock Analysis")
page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "TCS Analysis",
        "Apple Analysis",
        "Explore Companies",
        "Comparison",
        "About Project"
    ],
    key="page_navigation"
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
    st.subheader("High & Low Stock Price Analysis")
    c1, c2 = st.columns(2)
    c1.metric(
        "Highest Stock Price",
        f"{currency}{df['High'].max():.2f}"
    )

    c2.metric(
        "Lowest Stock Price",
        f"{currency}{df['Low'].min():.2f}"
    )

    st.subheader("Daily High & Low Price Trend")

    st.line_chart(
        df.set_index("Date")[["High", "Low"]]
    )
    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        file_name=name.lower().replace(" ", "_") + ".csv",
        mime="text/csv"
    )

       
# Home
if page == "Home":
    st.title("📈 Stock Market Intelligence")
    st.caption("Your Smart Platform to Explore, Analyze & Compare Stocks")

    st.markdown("---")

    st.subheader("📊 Market Overview")
    market_cols = st.columns(4)

    with market_cols[0]:
        st.metric("Companies Tracked", "7")

    with market_cols[1]:
        st.metric("Analysis Period", "1 Year")

    with market_cols[2]:
        st.metric("Prediction", "7 Days")

    with market_cols[3]:
        st.metric("Data Type", "Historical")
    st.subheader("🏢 Explore Top Companies")

    company_columns = st.columns(4)

    company_names = [
        ("TCS", "🇮🇳", "TCS.NS"),
        ("Apple", "🍎", "AAPL"),
        ("Reliance", "🇮🇳", "RELIANCE.NS"),
        ("Infosys", "💻", "INFY.NS"),
        ("HDFC Bank", "🏦", "HDFCBANK.NS"),
        ("Microsoft", "🪟", "MSFT"),
        ("Amazon", "📦", "AMZN")
    ]

    for index, (name, icon, ticker) in enumerate(company_names):
        with company_columns[index % 4]:
            st.markdown(
                f"""
                <div style="
                    background: #1e293b;
                    padding: 20px;
                    border-radius: 15px;
                    border: 1px solid #334155;
                    text-align: center;
                    margin-bottom: 15px;
                ">
                    <h3 style="color: #60a5fa;">{icon} {name}</h3>
                    <p style="color: #cbd5e1;">{ticker}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Explore " +
                name, key="explore_" + name, use_container_width=True):
                st.session_state["pending_page"] = "Explore Companies"
                st.session_state["selected_company"] = name
                st.rerun()
            

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "TCS Price",
            f"₹{tcs['Close'].dropna().iloc[-1]:.2f}"
        )

    with c2:
        st.metric(
            "Apple Price",
            f"${apple['Close'].dropna().iloc[-1]:.2f}"
        )

    with c3:
        st.metric(
            "TCS Daily Return",
            f"{tcs['Daily_Return'].dropna().iloc[-1]:.2f}%"
        )

    with c4:
        st.metric(
            "Apple Daily Return",
            f"{apple['Daily_Return'].dropna().iloc[-1]:.2f}%"
        )

    st.markdown("---")

    st.subheader("📈 Stock Performance")

    tab1, tab2 = st.tabs(["TCS", "Apple"])

    with tab1:
        st.line_chart(tcs.set_index("Date")["Close"])

    with tab2:
        st.line_chart(apple.set_index("Date")["Close"])

    st.markdown("---")

    st.subheader("⚖️ Company Comparison")

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

    st.markdown("---")

    st.subheader("🔗 Correlation Analysis")

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

    st.caption(
        "Note: Prices are based on available historical stock data."
    )


# Explore Companies
elif page == "Explore Companies":
    st.title("📊 Explore Companies")
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
