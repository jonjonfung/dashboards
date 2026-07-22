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
