import os
import groq
import pandas as pd


def analyse_portfolio(df: pd.DataFrame, summary: dict) -> str:
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

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


def chat(messages: list, df: pd.DataFrame, summary: dict) -> str:
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

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
