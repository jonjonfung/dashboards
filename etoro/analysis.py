import os
import groq
import pandas as pd

try:
    import streamlit as st
    def _secret(key):
        return st.secrets.get(key, os.getenv(key))
except Exception:
    def _secret(key):
        return os.getenv(key)


def analyse_portfolio(df: pd.DataFrame, summary: dict) -> str:
    client = groq.Groq(api_key=_secret("GROQ_API_KEY"))

    portfolio_text = df[["name", "total_invested", "total_gain", "gain_pct"]].to_string(index=False)

    prompt = f"""You are a portfolio analyst. Here is a snapshot of my eToro investment portfolio:

Total Invested: ${summary['total_invested']:,.2f}
Total Unrealised Gain: ${summary['total_gain']:,.2f}
Overall Return: {summary['gain_pct']:.2f}%

Positions:
{portfolio_text}

Please provide:
1. **Strengths** — what's working well in this portfolio
2. **Weaknesses** — risks or underperformers to watch
3. **Concentration risks** — any overexposure to sectors or single positions
4. **Rebalancing recommendations for the next 3 months** — specific actions: what to trim, what to add to, what to exit, and why. Be concrete.
5. **Key takeaway** — one actionable insight

Keep it concise, direct, and practical. No fluff."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )
    return response.choices[0].message.content


def rebalancing_tips(df: pd.DataFrame, summary: dict) -> list[str]:
    """Returns exactly 3 short rebalancing bullet points for the next 3 months."""
    client = groq.Groq(api_key=_secret("GROQ_API_KEY"))
    portfolio_text = df[["name", "total_invested", "total_gain", "gain_pct"]].to_string(index=False)

    prompt = f"""You are a portfolio analyst. Here is my eToro portfolio:

Total Invested: ${summary['total_invested']:,.2f}
Unrealised Gain: ${summary['total_gain']:,.2f}
Overall Return: {summary['gain_pct']:.2f}%

Positions:
{portfolio_text}

Give me exactly 3 concise rebalancing actions for the next 3 months.
Return ONLY a JSON array of 3 strings, each one sentence. Example:
["Trim X as it is overweight at Y%.", "Add to Z which is underperforming.", "Exit W due to poor fundamentals."]
No extra text, just the JSON array."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    import json
    try:
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception:
        return [response.choices[0].message.content.strip()]


def chat(messages: list, df: pd.DataFrame, summary: dict) -> str:
    client = groq.Groq(api_key=_secret("GROQ_API_KEY"))

    portfolio_text = df[["name", "total_invested", "total_gain", "gain_pct"]].to_string(index=False)

    system_prompt = f"""You are a helpful portfolio analyst. The user is asking questions about their eToro investment portfolio.

Portfolio snapshot:
Total Invested: ${summary['total_invested']:,.2f}
Total Unrealised Gain: ${summary['total_gain']:,.2f}
Overall Return: {summary['gain_pct']:.2f}%

Positions:
{portfolio_text}

Answer questions concisely and practically. Always reference specific positions and numbers from their portfolio."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}] + messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content
