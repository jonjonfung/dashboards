import boto3
import awswrangler as wr
import os
try:
    import streamlit as st
    def _secret(key):
        return st.secrets.get(key, os.getenv(key))
except Exception:
    def _secret(key):
        return os.getenv(key)

SECTOR_MAP = {
    1003:  "Technology",           # Meta
    1023:  "Financials",           # JPMorgan
    1130:  "Technology",           # Micron
    1141:  "Technology",           # Baidu
    1155:  "Consumer Discretionary", # Alibaba
    1583:  "Consumer Staples",     # Altria
    1634:  "Technology",           # Texas Instruments
    1757:  "Materials",            # Newmont Mining
    3008:  "Energy",               # XLE
    3190:  "Commodities",          # SPDR Gold
    3251:  "Healthcare",           # Vanguard Health Care ETF
    4236:  "Technology",           # Broadcom
    4238:  "Broad Market",         # Vanguard S&P 500 ETF
    4244:  "Technology",           # ASML
    4260:  "Technology",           # ServiceNow
    4430:  "Commodities",          # Silver Trust
    4481:  "Technology",           # TSMC
    4498:  "Fixed Income",         # Vanguard Intl Bond ETF
    6368:  "International Equity", # Vanguard Intl Stock ETF
    6434:  "Technology",           # Alphabet
    8748:  "Energy",               # Uranium ETF
    9425:  "Technology",           # IONQ
}


def _session():
    return boto3.Session(
        aws_access_key_id=_secret("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=_secret("AWS_SECRET_ACCESS_KEY"),
        region_name=_secret("AWS_DEFAULT_REGION") or "ap-southeast-2",
    )


def get_portfolio(date: str = None) -> "pd.DataFrame":
    sql = f"""
        SELECT
            i.symbol,
            i.name,
            ROUND(SUM(p.amount), 2)          AS total_invested,
            ROUND(SUM(p.unrealized_pnl), 2)  AS total_gain,
            ROUND(SUM(p.unrealized_pnl) / SUM(p.amount) * 100, 2) AS gain_pct,
            p.date
        FROM etoro_db.positions p
        JOIN etoro_db.instruments i ON p.instrument_id = i.instrument_id
        {"WHERE p.date = '" + date + "'" if date else ""}
        GROUP BY i.symbol, i.name, p.date
        ORDER BY total_invested DESC
    """
    return wr.athena.read_sql_query(
        sql,
        database="etoro_db",
        s3_output="s3://etoro-pipeline-john/athena-results/",
        boto3_session=_session(),
    )


def get_summary(date: str = None) -> dict:
    sql = f"""
        SELECT
            ROUND(SUM(p.amount), 2)          AS total_invested,
            ROUND(SUM(p.unrealized_pnl), 2)  AS total_gain,
            ROUND(SUM(p.unrealized_pnl) / SUM(p.amount) * 100, 2) AS gain_pct
        FROM etoro_db.positions p
        {"WHERE p.date = '" + date + "'" if date else ""}
    """
    df = wr.athena.read_sql_query(
        sql,
        database="etoro_db",
        s3_output="s3://etoro-pipeline-john/athena-results/",
        boto3_session=_session(),
    )
    return df.iloc[0].to_dict()


def get_trades() -> "pd.DataFrame":
    """
    Fetch closed trades with instrument names and Australian FY.
    Australian FY runs July 1 - June 30. FY2025 = Jul 2024 - Jun 2025.
    """
    sql = """
        SELECT
            t.trade_id,
            i.name,
            i.symbol,
            t.is_buy,
            t.open_date,
            t.close_date,
            t.investment,
            t.net_profit,
            t.fees,
            t.leverage,
            CASE
                WHEN MONTH(DATE(t.close_date)) >= 7
                THEN YEAR(DATE(t.close_date)) + 1
                ELSE YEAR(DATE(t.close_date))
            END AS financial_year
        FROM etoro_db.trades t
        LEFT JOIN etoro_db.instruments i ON t.instrument_id = i.instrument_id
        WHERE t.close_date IS NOT NULL AND t.close_date != ''
        ORDER BY t.close_date DESC
    """
    return wr.athena.read_sql_query(
        sql,
        database="etoro_db",
        s3_output="s3://etoro-pipeline-john/athena-results/",
        boto3_session=_session(),
    )


def get_sector_breakdown(date: str = None) -> "pd.DataFrame":
    import pandas as pd
    df = get_portfolio(date)
    # instrument_id is in the positions table — re-query to get it
    sql = f"""
        SELECT
            p.instrument_id,
            i.name,
            ROUND(SUM(p.amount), 2) AS total_invested
        FROM etoro_db.positions p
        JOIN etoro_db.instruments i ON p.instrument_id = i.instrument_id
        {"WHERE p.date = '" + date + "'" if date else ""}
        GROUP BY p.instrument_id, i.name
    """
    df = wr.athena.read_sql_query(
        sql,
        database="etoro_db",
        s3_output="s3://etoro-pipeline-john/athena-results/",
        boto3_session=_session(),
    )
    df["sector"] = df["instrument_id"].map(SECTOR_MAP).fillna("Other")
    return df


def get_portfolio_history() -> "pd.DataFrame":
    """
    Returns total portfolio value (invested + unrealized PnL) per snapshot date.
    Used for performance trend vs S&P 500.
    """
    sql = """
        SELECT
            p.date,
            ROUND(SUM(p.amount) + SUM(p.unrealized_pnl), 2) AS portfolio_value
        FROM etoro_db.positions p
        GROUP BY p.date
        ORDER BY p.date ASC
    """
    return wr.athena.read_sql_query(
        sql,
        database="etoro_db",
        s3_output="s3://etoro-pipeline-john/athena-results/",
        boto3_session=_session(),
    )


def get_available_dates() -> list:
    df = wr.athena.read_sql_query(
        "SELECT DISTINCT date FROM etoro_db.positions ORDER BY date DESC",
        database="etoro_db",
        s3_output="s3://etoro-pipeline-john/athena-results/",
        boto3_session=_session(),
    )
    return df["date"].tolist()
