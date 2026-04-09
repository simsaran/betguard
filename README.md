# BetGuard: Betting Fraud & Risk Monitoring Dashboard

## The Problem

Online sports betting platforms process thousands of transactions daily. Hidden within this volume are fraudulent activities: money laundering, bonus abuse, bot-driven betting, and account takeovers. Without automated detection, these threats go unnoticed until financial damage is done.

## The Solution

BetGuard is an interactive fraud monitoring dashboard that:
- Ingests betting transaction data
- Engineers 6 behavioral risk features based on real industry fraud patterns
- Applies an Isolation Forest anomaly detection model to flag suspicious bets
- Presents results through interactive charts and sortable tables
- Enables risk analysts to download flagged transactions for investigation

## Live Demo

🔗 [Access the Live Dashboard](https://betguard-anuz63rqv3kaskgeba4tnq.streamlit.app/)

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| Python | Core programming language |
| Pandas | Data manipulation and feature engineering |
| Scikit-Learn | Isolation Forest anomaly detection |
| Plotly | Interactive data visualizations |
| Streamlit | Web application framework |
| Excel | Source data format |

## Key Features

- **Behavioral Risk Scoring**: 6 engineered features including bet-size spikes, temporal anomalies, account-age risk, and win-rate analysis
- **Unsupervised Anomaly Detection**: No labeled data required — Isolation Forest identifies outliers automatically
- **Interactive Dashboard**: Real-time filtering, hover details, and drill-down capability
- **Risk Tiering**: High / Medium / Low risk classification
- **Export Capability**: Download flagged transactions as CSV for further investigation

## Feature Engineering

| Feature | Business Logic |
|---------|---------------|
| bet_vs_avg | Detects sudden spikes in a user's betting amount |
| is_late_night | Flags bets placed 1–5 AM (bot/takeover signal) |
| user_bet_count | Identifies high-frequency automated betting |
| user_win_rate | Catches statistically impossible win rates |
| user_avg_odds | Detects insider knowledge on high-odds bets |
| is_new_account | Flags bonus abuse from accounts < 14 days old |

## Business Impact

In a production environment, this system would:
- Reduce fraud investigation time by automating initial screening
- Flag ~15% of transactions for review, focusing analyst effort
- Identify money laundering through bet-size anomaly detection
- Detect bot activity through temporal pattern analysis
- Catch bonus abuse through new-account behavioral profiling

## How to Run Locally
```bash
git clone https://github.com/YOUR_USERNAME/betguard.git
cd betguard
pip install -r requirements.txt
streamlit run app.py
```

## Author

Simran Saran | University of Waterloo | 

