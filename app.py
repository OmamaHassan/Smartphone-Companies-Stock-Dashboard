import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Smartphone Stock Peer Analysis",
    layout="wide"
)

st.header("📱Smartphone Companies Stock Market Dashboard (2016–2021)")

# -----------------------------
# Load and Merge Data/csv
# -----------------------------
DATA_FOLDER = "data"

dfs = []

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".csv"):
        company_name = file.replace(".csv", "")
        df = pd.read_csv(os.path.join(DATA_FOLDER, file))
        
        df["Date"] = pd.to_datetime(df["Date"])
        df["Source"] = company_name  # source column
        
        dfs.append(df)

stock_df = pd.concat(dfs, ignore_index=True)
stock_df = stock_df.sort_values("Date")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

# Company multi-select
companies = st.sidebar.multiselect(
    "Select Companies", 
    options=stock_df["Source"].unique(),
    default=stock_df["Source"].unique()[:2] # by default 2 options are selected
)

# Separate FROM and TO date pickers
start_date = st.sidebar.date_input(
    "From",
    value=stock_df["Date"].min(),
    min_value=stock_df["Date"].min(),
    max_value=stock_df["Date"].max()
)

end_date = st.sidebar.date_input(
    "To",
    value=stock_df["Date"].max(),
    min_value=stock_df["Date"].min(),
    max_value=stock_df["Date"].max()
)

# Ensure start_date <= end_date
if start_date > end_date:
    st.sidebar.error("❌ 'From' date must be before 'To' date")

# Metric selection
metric = st.sidebar.selectbox(
    "Select Metric",
    ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
)

# Metrics Explanation
metric_explanations = {
    "Open": "Opening price of the stock at the start of the trading day.",
    "High": "Highest price reached during the trading day.",
    "Low": "Lowest price reached during the trading day.",
    "Close": "Closing price of the stock at the end of the trading day.",
    "Adj Close": "Adjusted closing price accounting for dividends and stock splits.",
    "Volume": "Number of shares traded during the day."
}

# Convert to pandas datetime for filtering
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data
filtered_df = stock_df[
    (stock_df["Source"].isin(companies)) &
    (stock_df["Date"] >= start_date) &
    (stock_df["Date"] <= end_date)
]


# -----------------------------
# KPI Section
# -----------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Companies Selected", len(companies))

with col2:
    st.metric("From", start_date.strftime("%Y-%m-%d"))

with col3:
    st.metric("To", end_date.strftime("%Y-%m-%d"))

# -----------------------------
# Stock Price Comparison Chart
# -----------------------------
st.subheader(f"📈 {metric} Comparison")
st.caption(metric_explanations[metric])

fig = px.line(
    filtered_df,
    x="Date",
    y=metric,
    color="Source",
    labels={"Source": "Company"},
)
st.plotly_chart(fig, use_container_width=True)


st.subheader("📈 Individual Stock vs Peer Average")

if len(companies) >= 2:
    CARD_WIDTH = 3  # how many cards per row

    for start in range(0, len(companies), CARD_WIDTH):
        row_companies = companies[start:start + CARD_WIDTH]
        cols = st.columns(CARD_WIDTH)  # equal‑width columns for this row

        for idx, company in enumerate(row_companies):
            with cols[idx]:
                # Individual stock series
                stock_data = (
                    filtered_df[filtered_df["Source"] == company]
                    [["Date", metric]]
                    .rename(columns={metric: company})
                )

                # Peer average (exclude company)
                peer_data = (
                    filtered_df[filtered_df["Source"] != company]
                    .groupby("Date")[metric]
                    .mean()
                    .reset_index()
                    .rename(columns={metric: "Peer Average"})
                )

                # merge-time series
                comp_df = pd.merge(stock_data, peer_data, on="Date", how="inner")

                fig = px.line(
                    comp_df,
                    x="Date",
                    y=[company, "Peer Average"],
                    labels={"value": metric, "variable": "Legend"},
                    title=f"{company} vs Peer Average",
                    height=300,
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Select at least 2 companies to see peer comparisons.")

# -----------------------------
# Data Preview
# -----------------------------
st.subheader("📄 Dataset Preview")
st.dataframe(filtered_df.head(20))