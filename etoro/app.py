import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from data import get_portfolio, get_summary, get_available_dates
from charts import allocation_pie, gain_loss_bar, gain_pct_bar, invested_vs_gain_scatter
from analysis import analyse_portfolio

st.set_page_config(page_title="eToro Dashboard", layout="wide")
st.title("📈 eToro Portfolio Dashboard")

# Date selector
dates = get_available_dates()
selected_date = st.selectbox("Snapshot date", dates)

# Load data
with st.spinner("Loading portfolio..."):
    df = get_portfolio(selected_date)
    summary = get_summary(selected_date)

# Summary metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Invested", f"${summary['total_invested']:,.2f}")
col2.metric("Unrealised Gain", f"${summary['total_gain']:,.2f}")
col3.metric("Overall Return", f"{summary['gain_pct']:.2f}%",
            delta=f"{summary['gain_pct']:.2f}%")

st.divider()

# Charts
col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(allocation_pie(df), use_container_width=True)
with col_right:
    st.plotly_chart(gain_loss_bar(df), use_container_width=True)

st.plotly_chart(gain_pct_bar(df), use_container_width=True)
st.plotly_chart(invested_vs_gain_scatter(df), use_container_width=True)

st.divider()

# Positions table
st.subheader("Positions")
st.dataframe(
    df[["name", "total_invested", "total_gain", "gain_pct"]].rename(columns={
        "name": "Name",
        "total_invested": "Invested (USD)",
        "total_gain": "Gain (USD)",
        "gain_pct": "Return %",
    }),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# Claude analysis
st.subheader("🤖 Claude Portfolio Analysis")
if st.button("Analyse my portfolio"):
    with st.spinner("Asking Claude..."):
        analysis = analyse_portfolio(df, summary)
    st.markdown(analysis)
