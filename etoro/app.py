import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from data import get_portfolio, get_summary, get_available_dates, get_trades, get_portfolio_history, get_sector_breakdown
from charts import treemap, waterfall, gain_pct_horizontal, bubble, gain_loss_bar, trades_by_fy, buys_vs_sells_bar, profit_by_instrument, portfolio_vs_sp500, sector_breakdown
from analysis import analyse_portfolio, chat, rebalancing_tips

st.set_page_config(page_title="eToro Dashboard", layout="wide")
st.title("📈 eToro Portfolio Dashboard")

tab1, tab2 = st.tabs(["Portfolio", "Buys & Sells"])

# ── TAB 1: PORTFOLIO ──────────────────────────────────────────────────────────
with tab1:
    dates = get_available_dates()
    selected_date = st.selectbox("Snapshot date", dates)

    with st.spinner("Loading portfolio..."):
        df = get_portfolio(selected_date)
        summary = get_summary(selected_date)

    total_value = summary['total_invested'] + summary['total_gain']
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Portfolio Value", f"${total_value:,.2f}")
    col2.metric("Total Invested", f"${summary['total_invested']:,.2f}")
    col3.metric("Unrealised Gain", f"${summary['total_gain']:,.2f}")
    col4.metric("Overall Return", f"{summary['gain_pct']:.2f}%",
                delta=f"{summary['gain_pct']:.2f}%")

    st.divider()

    with st.spinner("Generating rebalancing tips..."):
        tips = rebalancing_tips(df, summary)
    st.subheader("📋 3-Month Rebalancing Recommendations")
    for tip in tips:
        st.markdown(f"- {tip}")

    st.divider()

    with st.spinner("Loading performance history..."):
        history_df = get_portfolio_history()
    if len(history_df) > 1:
        st.plotly_chart(portfolio_vs_sp500(history_df), use_container_width=True)
        st.divider()

    with st.spinner("Loading sector data..."):
        sector_df = get_sector_breakdown(selected_date)
    st.plotly_chart(sector_breakdown(sector_df), use_container_width=True)

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(treemap(df), use_container_width=True)
    with col_right:
        st.plotly_chart(gain_loss_bar(df), use_container_width=True)

    st.plotly_chart(waterfall(df), use_container_width=True)

    col_left2, col_right2 = st.columns(2)
    with col_left2:
        st.plotly_chart(gain_pct_horizontal(df), use_container_width=True)
    with col_right2:
        st.plotly_chart(bubble(df), use_container_width=True)

    st.divider()

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

    st.subheader("🤖 AI Portfolio Analysis & Rebalancing")
    if st.button("Analyse my portfolio"):
        with st.spinner("Analysing..."):
            analysis = analyse_portfolio(df, summary)
        st.markdown(analysis)

    st.divider()

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

# ── TAB 2: BUYS & SELLS ───────────────────────────────────────────────────────
with tab2:
    st.subheader("Buys & Sells by Australian Financial Year")
    st.caption("Australian FY runs July 1 – June 30")

    with st.spinner("Loading trade history..."):
        trades_df = get_trades()

    if trades_df.empty:
        st.info("No closed trades found yet.")
    else:
        fys = sorted(trades_df["financial_year"].dropna().unique(), reverse=True)
        selected_fy = st.selectbox("Financial Year", [f"FY{int(y)}" for y in fys])
        fy_year = int(selected_fy.replace("FY", ""))
        fy_df = trades_df[trades_df["financial_year"] == fy_year]

        # FY summary metrics
        buys = fy_df[fy_df["is_buy"] == True]
        sells = fy_df[fy_df["is_buy"] == False]
        total_profit = fy_df["net_profit"].sum()
        total_fees = fy_df["fees"].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Trades", len(fy_df))
        c2.metric("Buy Trades", len(buys))
        c3.metric("Sell Trades", len(sells))
        c4.metric("Net Profit", f"${total_profit:,.2f}", delta=f"${total_profit:,.2f}")

        st.divider()

        col_l, col_r = st.columns(2)
        with col_l:
            st.plotly_chart(trades_by_fy(trades_df), use_container_width=True)
        with col_r:
            st.plotly_chart(buys_vs_sells_bar(trades_df), use_container_width=True)

        st.plotly_chart(profit_by_instrument(fy_df), use_container_width=True)

        st.divider()

        st.subheader(f"Trade History — {selected_fy}")
        display_df = fy_df[["close_date", "name", "is_buy", "investment", "net_profit", "fees"]].copy()
        display_df["is_buy"] = display_df["is_buy"].map({True: "Buy", False: "Sell"})
        st.dataframe(
            display_df.rename(columns={
                "close_date": "Close Date",
                "name": "Instrument",
                "is_buy": "Type",
                "investment": "Investment (USD)",
                "net_profit": "Net Profit (USD)",
                "fees": "Fees (USD)",
            }).sort_values("Close Date", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
