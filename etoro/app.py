import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from data import get_portfolio, get_summary, get_available_dates
from charts import treemap, waterfall, gain_pct_horizontal, bubble, gain_loss_bar
from analysis import analyse_portfolio, chat

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

# Row 1 — Treemap + Gain/Loss bar
col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(treemap(df), use_container_width=True)
with col_right:
    st.plotly_chart(gain_loss_bar(df), use_container_width=True)

# Row 2 — Waterfall
st.plotly_chart(waterfall(df), use_container_width=True)

# Row 3 — Return % horizontal + Bubble
col_left2, col_right2 = st.columns(2)
with col_left2:
    st.plotly_chart(gain_pct_horizontal(df), use_container_width=True)
with col_right2:
    st.plotly_chart(bubble(df), use_container_width=True)

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

# AI analysis
st.subheader("🤖 AI Portfolio Analysis & Rebalancing")
if st.button("Analyse my portfolio"):
    with st.spinner("Analysing..."):
        analysis = analyse_portfolio(df, summary)
    st.markdown(analysis)

st.divider()

# Chat
st.subheader("💬 Ask about your portfolio")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything about your portfolio..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = chat(st.session_state.messages, df, summary)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
