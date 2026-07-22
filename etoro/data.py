import boto3
import awswrangler as wr
import os


def _session():
    return boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2"),
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


def get_available_dates() -> list:
    df = wr.athena.read_sql_query(
        "SELECT DISTINCT date FROM etoro_db.positions ORDER BY date DESC",
        database="etoro_db",
        s3_output="s3://etoro-pipeline-john/athena-results/",
        boto3_session=_session(),
    )
    return df["date"].tolist()
