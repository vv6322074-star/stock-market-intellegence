
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

.stButton > button {
    background: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
}
</style>
""", unsafe_allow_html=True)
    page_title="Stock Price Analysis",
    page_icon="📈",
    layout="wide"
)
st.markdown("""
<style>
.stApp {
    background-color: #F5F7FA;
}
h1, h2, h3 {
    color: #173B35;
}
.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #E1E8E5;
}
.stButton button {
    background-color: #176B55;
    color: white;
    border-radius: 8px;
}
[data-testid="stSidebar"] {
    background-color: #EAF2EF;
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
st.sidebar.title("📈 Stock Analysis")
page = st.sidebar.radio(
    "Navigation",
  ["Home", "TCS Analysis", "Apple Analysis",
 "Explore Companies", "Comparison", "About Project"] 
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
            st.markdown(f"### {icon} {name}")
            st.caption(ticker)

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
    st.caption("Explore stocks, track price movements and understand market risk.")

    company_name = st.selectbox(
        "Select Company",
        list(companies.keys())
    )

    ticker = companies[company_name]
    stock_data = get_stock_data(ticker)

    if stock_data.empty:
        st.warning("Stock data is not available right now.")

    else:
        date_column = "Date" if "Date" in stock_data.columns else "Datetime"

        stock_data["Daily_Return"] = (
            stock_data["Close"].pct_change() * 100
        )

        valid_prices = stock_data["Close"].dropna()

        latest_price = valid_prices.iloc[-1]
        previous_price = valid_prices.iloc[-2] if len(valid_prices) > 1 else latest_price

        daily_change = latest_price - previous_price

        daily_change_percent = (
            (daily_change / previous_price) * 100
            if previous_price != 0 else 0
        )

        currency = "₹" if ticker.endswith(".NS") else "$"

        st.subheader(company_name + " Stock Overview")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Latest Available Close",
                f"{currency}{latest_price:.2f}"
            )

        with c2:
            st.metric(
                "Daily Change",
                f"{currency}{daily_change:.2f}",
                f"{daily_change_percent:.2f}%"
            )

        with c3:
            st.metric(
                "Daily Volatility",
                f"{stock_data['Daily_Return'].std():.2f}%"
            )

        st.markdown("---")

        st.subheader("📈 Stock Price Trend")

        st.line_chart(
            stock_data.set_index(date_column)["Close"]
        )
        
        st.markdown("---")
        st.subheader("🤖 AI-Based 7-Day Stock Price Prediction")

        predictions = predict_stock_price(stock_data)

        prediction_df = pd.DataFrame({
            "Day": [f"Day {i}" for i in range(1, 8)],
            "Predicted Price": predictions
        })

        st.line_chart(
            prediction_df.set_index("Day")["Predicted Price"]
        )

        st.caption(
            "These are model-based estimates from historical prices, "
            "not guaranteed future prices."
        )
        st.subheader("📊 Daily Returns")

        st.line_chart(
            stock_data.set_index(date_column)["Daily_Return"]
        )

        st.subheader("⚠️ Risk Analysis")

        st.write(
            "Daily volatility measures how much the stock returns fluctuate."
        )

        st.info(
            "Higher volatility indicates greater price fluctuation. "
            "This is historical analysis, not a guarantee of future performance."
        )
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
