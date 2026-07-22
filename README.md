# dashboards

Interactive portfolio dashboards powered by Streamlit, Plotly, and Claude AI.

## etoro

Visualises your eToro portfolio from data stored in AWS Athena, with Claude AI analysis.

### Features
- Portfolio allocation pie chart
- Gain / loss bar chart per position
- Return % by position
- Invested vs gain scatter plot
- Claude AI strengths & weaknesses analysis

### Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add your `ANTHROPIC_API_KEY` to `.env`, then:

```bash
cd etoro
streamlit run app.py
```
