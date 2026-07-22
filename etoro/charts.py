import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def treemap(df: pd.DataFrame):
    """Treemap — size = invested, colour = return %"""
    return px.treemap(
        df,
        path=["name"],
        values="total_invested",
        color="gain_pct",
        color_continuous_scale=["#ef4444", "#f97316", "#22c55e"],
        color_continuous_midpoint=0,
        title="Portfolio Allocation (size = invested, colour = return %)",
        custom_data=["total_gain", "gain_pct", "total_invested"],
    ).update_traces(
        texttemplate="<b>%{label}</b><br>$%{customdata[2]:,.0f}<br>%{customdata[1]:.1f}%",
        hovertemplate="<b>%{label}</b><br>Invested: $%{customdata[2]:,.2f}<br>Gain: $%{customdata[0]:,.2f}<br>Return: %{customdata[1]:.2f}%",
    )


def waterfall(df: pd.DataFrame):
    """Waterfall showing each position's contribution to total gain"""
    df = df.sort_values("total_gain")
    colors = ["#ef4444" if g < 0 else "#22c55e" for g in df["total_gain"]]
    fig = go.Figure(go.Waterfall(
        name="Gain/Loss",
        orientation="v",
        x=df["name"],
        y=df["total_gain"],
        text=[f"${g:,.0f}" for g in df["total_gain"]],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#22c55e"}},
        decreasing={"marker": {"color": "#ef4444"}},
    ))
    fig.update_layout(
        title="Gain / Loss Waterfall by Position",
        xaxis_tickangle=-45,
        yaxis_title="USD",
        showlegend=False,
    )
    return fig


def gain_pct_horizontal(df: pd.DataFrame):
    """Horizontal bar — easier to read with many positions"""
    df = df.sort_values("gain_pct")
    colors = ["#ef4444" if g < 0 else "#22c55e" for g in df["gain_pct"]]
    fig = go.Figure(go.Bar(
        y=df["name"],
        x=df["gain_pct"],
        orientation="h",
        marker_color=colors,
        text=[f"{g:.1f}%" for g in df["gain_pct"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Return % by Position",
        xaxis_title="%",
        showlegend=False,
        height=600,
    )
    return fig


def bubble(df: pd.DataFrame):
    """Bubble — invested vs gain, bubble size = position size, colour = return %"""
    return px.scatter(
        df,
        x="total_invested",
        y="total_gain",
        size="total_invested",
        color="gain_pct",
        text="name",
        color_continuous_scale=["#ef4444", "#f97316", "#22c55e"],
        color_continuous_midpoint=0,
        title="Invested vs Gain (bubble size = amount invested)",
        labels={"total_invested": "Invested (USD)", "total_gain": "Gain (USD)", "gain_pct": "Return %"},
    ).update_traces(textposition="top center")


def trades_by_fy(df: pd.DataFrame):
    """Stacked bar — number of buys and sells per Australian FY"""
    summary = df.groupby(["financial_year", "is_buy"]).size().reset_index(name="count")
    summary["type"] = summary["is_buy"].map({True: "Buy", False: "Sell"})
    summary["FY"] = "FY" + summary["financial_year"].astype(int).astype(str)
    return px.bar(
        summary,
        x="FY",
        y="count",
        color="type",
        color_discrete_map={"Buy": "#22c55e", "Sell": "#ef4444"},
        title="Trades per Financial Year (Buy vs Sell)",
        labels={"count": "Number of Trades", "FY": "Financial Year"},
        barmode="group",
    )


def buys_vs_sells_bar(df: pd.DataFrame):
    """Net profit per FY"""
    summary = df.groupby("financial_year")["net_profit"].sum().reset_index()
    summary["FY"] = "FY" + summary["financial_year"].astype(int).astype(str)
    colors = ["#22c55e" if p >= 0 else "#ef4444" for p in summary["net_profit"]]
    fig = go.Figure(go.Bar(
        x=summary["FY"],
        y=summary["net_profit"],
        marker_color=colors,
        text=[f"${p:,.0f}" for p in summary["net_profit"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Net Profit per Financial Year",
        yaxis_title="USD",
        showlegend=False,
    )
    return fig


def profit_by_instrument(df: pd.DataFrame):
    """Horizontal bar — net profit by instrument for selected FY"""
    summary = df.groupby("name")["net_profit"].sum().reset_index().sort_values("net_profit")
    colors = ["#ef4444" if p < 0 else "#22c55e" for p in summary["net_profit"]]
    fig = go.Figure(go.Bar(
        y=summary["name"],
        x=summary["net_profit"],
        orientation="h",
        marker_color=colors,
        text=[f"${p:,.0f}" for p in summary["net_profit"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Net Profit by Instrument",
        xaxis_title="USD",
        showlegend=False,
        height=500,
    )
    return fig


def gain_loss_bar(df: pd.DataFrame):
    df = df.sort_values("total_gain")
    colors = ["#ef4444" if g < 0 else "#22c55e" for g in df["total_gain"]]
    fig = go.Figure(go.Bar(
        x=df["name"],
        y=df["total_gain"],
        marker_color=colors,
        text=[f"${g:,.0f}" for g in df["total_gain"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Unrealised Gain / Loss by Position",
        xaxis_tickangle=-45,
        yaxis_title="USD",
        showlegend=False,
    )
    return fig
