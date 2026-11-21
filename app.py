
import streamlit as st
import pandas as pd
import yfinance as yf
import random
import smtplib
from email.mime.text import MIMEText
def send_otp(email, otp):
    sender_email = st.secrets["email"]["sender_email"]
    sender_password = st.secrets["email"]["sender_password"]

    message = MIMEText(f"Your Stoxen verification OTP is: {otp}")
    message["Subject"] = "Stoxen - Email Verification"
    message["From"] = sender_email
    message["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
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
# Email OTP Login
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

st.title("🔐 Stoxen Email Login")

if not st.session_state.otp_verified:
    email = st.text_input("Enter your Gmail address")

    if st.button("Send OTP"):
        if email and "@" in email:
            otp = str(random.randint(100000, 999999))
            try:
                send_otp(email, otp)
                st.session_state["otp"] = otp
                st.session_state["otp_email"] = email
                st.success("OTP sent to your email!")
            except Exception:
                st.error("OTP sending failed. Please check your email settings.")
        else:
            st.warning("Please enter a valid email address.")

    if "otp" in st.session_state:
        entered_otp = st.text_input("Enter OTP")

        if st.button("Verify OTP"):
            if entered_otp == st.session_state["otp"]:
                st.session_state.otp_verified = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect OTP. Try again.")

    st.stop()
# Sidebar
if "pending_page" in st.session_state:
    st.session_state["page_navigation"] = st.session_state.pop("pending_page")

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

if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []  
    if "price_alerts" not in st.session_state:
    st.session_state["price_alerts"] = []
# Home
if page == "Home":
    st.title("📈 Stock Market Intelligence")
    st.caption("Your Smart Platform to Explore, Analyze & Compare Stocks")

    st.markdown("---")
    st.subheader("📋 Your Active Price Alerts")

    if st.session_state["price_alerts"]:
        for alert in st.session_state["price_alerts"]:
            st.write(
                f"🔔 {alert['company']} - Target Price: {alert['target']:.2f}"
            )
    else:
        st.info("No price alerts set yet.")

    st.subheader("📊 Market Overview")

    market_cols = st.columns(4)

    st.subheader("⭐ My Watchlist")
    st.markdown("---")
    st.subheader("🔔 Smart Price Alerts")

    alert_company = st.selectbox(
        "Select Company",
        list(companies.keys()),
        key="alert_company"
    )

    target_price = st.number_input(
        "Enter Target Price",
        min_value=0.01,
        value=100.0,
        key="target_price"
    )

    if st.button("Set Price Alert"):
        st.session_state["price_alerts"].append({
            "company": alert_company,
            "target": target_price
        })
        st.success("Price alert added successfully!")

    if st.session_state["watchlist"]:
        for stock in st.session_state["watchlist"]:
            st.write("⭐", stock)
    else:
        st.info("Your watchlist is empty. Add your favourite companies!")

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
    st.subheader("🔍 Search Your Company")

    search_query = st.text_input("Search company")

    filtered_companies = [
        company for company in company_names
        if search_query.lower() in company[0].lower()
    ]

    for index, (name, icon, ticker) in enumerate(filtered_companies):
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
            if st.button("⭐ Add to Watchlist", key="watch_" + name):
                if name not in st.session_state["watchlist"]:
                    st.session_state["watchlist"].append(name)
                    st.success(name + " added to Watchlist!")
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
    st.caption("Explore and analyse different companies.")

    company_options = list(companies.keys())
    selected_company = st.session_state.get("selected_company", "TCS")

    company_name = st.selectbox(
        "Select Company",
        company_options,
        index=company_options.index(selected_company)
    )

    ticker = companies[company_name]
    stock_data = get_stock_data(ticker)

    if stock_data.empty:
        st.warning("Stock data is not available. Please try again.")
    else:
        st.subheader(company_name + " Stock Analysis")
        latest_price = stock_data["Close"].dropna().iloc[-1]
        st.metric("Latest Closing Price", f"{latest_price:.2f}")
        st.subheader("Stock Price History")
        st.line_chart(stock_data.set_index("Date")["Close"])
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
