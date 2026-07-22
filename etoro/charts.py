import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def allocation_pie(df: pd.DataFrame):
    return px.pie(
        df,
        names="name",
        values="total_invested",
        title="Portfolio Allocation",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )


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


def gain_pct_bar(df: pd.DataFrame):
    df = df.sort_values("gain_pct")
    colors = ["#ef4444" if g < 0 else "#22c55e" for g in df["gain_pct"]]
    fig = go.Figure(go.Bar(
        x=df["name"],
        y=df["gain_pct"],
        marker_color=colors,
        text=[f"{g:.1f}%" for g in df["gain_pct"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Return % by Position",
        xaxis_tickangle=-45,
        yaxis_title="%",
        showlegend=False,
    )
    return fig


def invested_vs_gain_scatter(df: pd.DataFrame):
    return px.scatter(
        df,
        x="total_invested",
        y="total_gain",
        text="name",
        size="total_invested",
        color="gain_pct",
        color_continuous_scale=["#ef4444", "#f97316", "#22c55e"],
        title="Invested vs Gain",
        labels={"total_invested": "Invested (USD)", "total_gain": "Gain (USD)"},
    ).update_traces(textposition="top center")
