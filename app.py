import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
import numpy as np

# ---- Page Setup ----
st.set_page_config(
    page_title="BetGuard | Fraud & Risk Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Custom CSS ----
st.markdown('''
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a5276;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
''', unsafe_allow_html=True)

# ---- Title ----
st.markdown('<div class="main-header">🛡️ BetGuard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Betting Fraud & Risk Monitoring Dashboard</div>', unsafe_allow_html=True)

# ---- File Upload ----
uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Betting Data (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("👉 Upload an Excel file using the sidebar to get started.")
    st.stop()

df = pd.read_excel(uploaded_file)

# ---- Data Cleaning ----
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.day_name()
df['date'] = df['timestamp'].dt.date

# ---- Feature Engineering ----
user_avg_bet = df.groupby('user_id')['bet_amount'].transform('mean')
df['bet_vs_avg'] = df['bet_amount'] / user_avg_bet

df['is_late_night'] = df['hour'].apply(lambda h: 1 if 1 <= h <= 5 else 0)

df['user_bet_count'] = df.groupby('user_id')['transaction_id'].transform('count')

df['user_win_rate'] = df.groupby('user_id')['outcome'].transform(
    lambda x: (x == 'Win').mean()
)

df['user_avg_odds'] = df.groupby('user_id')['odds'].transform('mean')

df['is_new_account'] = (df['account_age_days'] < 14).astype(int)

# ---- Anomaly Detection ----
features = ['bet_amount', 'hour', 'bet_vs_avg', 'is_late_night',
            'user_bet_count', 'user_win_rate', 'user_avg_odds',
            'is_new_account', 'account_age_days']

X = df[features].fillna(0)

model = IsolationForest(
    n_estimators=100,
    contamination=0.15,
    random_state=42
)

df['anomaly_score'] = model.fit_predict(X)
df['risk_flag'] = df['anomaly_score'].apply(
    lambda x: 'Suspicious' if x == -1 else 'Normal'
)

df['risk_score'] = model.decision_function(X)
df['risk_level'] = pd.cut(
    df['risk_score'],
    bins=[-float('inf'), -0.15, -0.05, float('inf')],
    labels=['High Risk', 'Medium Risk', 'Low Risk']
)

# ---- KPI Metrics ----
st.markdown('### 📊 Key Performance Indicators')

col1, col2, col3, col4 = st.columns(4)

total_bets = len(df)
flagged = len(df[df['risk_flag'] == 'Suspicious'])
total_wagered = df['bet_amount'].sum()
flagged_amount = df[df['risk_flag'] == 'Suspicious']['bet_amount'].sum()

col1.metric('Total Transactions', f'{total_bets:,}')
col2.metric('Flagged Suspicious', f'{flagged}',
            delta=f'{flagged/total_bets*100:.1f}%', delta_color='inverse')
col3.metric('Total Wagered', f'${total_wagered:,.2f}')
col4.metric('Flagged Amount', f'${flagged_amount:,.2f}')

# ---- Charts ----
st.markdown('---')
st.markdown('### 📈 Risk Analysis')

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    risk_counts = df['risk_level'].value_counts()
    fig_pie = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title='Transaction Risk Distribution',
        color_discrete_sequence=['#e74c3c', '#f39c12', '#27ae60'],
        hole=0.4
    )
    fig_pie.update_layout(font=dict(size=14))
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    fig_box = px.box(
        df, x='risk_flag', y='bet_amount',
        color='risk_flag',
        title='Bet Amount Distribution: Normal vs Suspicious',
        color_discrete_map={'Normal': '#27ae60', 'Suspicious': '#e74c3c'}
    )
    fig_box.update_layout(font=dict(size=14))
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown('### ⏰ Temporal Patterns')
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    hourly = df.groupby(['hour', 'risk_flag']).size().reset_index(name='count')
    fig_hour = px.bar(
        hourly, x='hour', y='count', color='risk_flag',
        title='Betting Activity by Hour of Day',
        color_discrete_map={'Normal': '#3498db', 'Suspicious': '#e74c3c'},
        barmode='stack'
    )
    fig_hour.update_layout(
        xaxis_title='Hour (24h)',
        yaxis_title='Number of Bets',
        font=dict(size=14)
    )
    st.plotly_chart(fig_hour, use_container_width=True)

with chart_col4:
    fig_scatter = px.scatter(
        df, x='account_age_days', y='bet_amount',
        color='risk_flag', size='bet_amount',
        title='Bet Amount vs Account Age',
        color_discrete_map={'Normal': '#3498db', 'Suspicious': '#e74c3c'},
        hover_data=['user_id', 'sport', 'bet_type']
    )
    fig_scatter.update_layout(font=dict(size=14))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ---- Flagged Transactions Table ----
st.markdown('---')
st.markdown('### 🚨 Flagged Transactions')

flagged_df = df[df['risk_flag'] == 'Suspicious'][
    ['transaction_id', 'user_id', 'timestamp', 'bet_amount',
     'sport', 'bet_type', 'odds', 'outcome', 'risk_level',
     'account_age_days', 'is_late_night', 'bet_vs_avg']
].sort_values('bet_amount', ascending=False)

st.dataframe(
    flagged_df.style.format({
        'bet_amount': '${:,.2f}',
        'odds': '{:.2f}',
        'bet_vs_avg': '{:.1f}x'
    }),
    use_container_width=True,
    height=400
)

# ---- User Risk Profiles ----
st.markdown('---')
st.markdown('### 👤 User Risk Profiles')

user_summary = df.groupby('user_id').agg(
    total_bets=('transaction_id', 'count'),
    total_wagered=('bet_amount', 'sum'),
    avg_bet=('bet_amount', 'mean'),
    win_rate=('outcome', lambda x: (x == 'Win').mean()),
    suspicious_count=('risk_flag', lambda x: (x == 'Suspicious').sum()),
    account_age=('account_age_days', 'first')
).round(2).sort_values('suspicious_count', ascending=False)

st.dataframe(
    user_summary.style.format({
        'total_wagered': '${:,.2f}',
        'avg_bet': '${:,.2f}',
        'win_rate': '{:.1%}'
    }),
    use_container_width=True
)

# ---- Download Button ----
st.markdown('---')
st.download_button(
    label='📥 Download Flagged Transactions as CSV',
    data=flagged_df.to_csv(index=False),
    file_name='betguard_flagged_transactions.csv',
    mime='text/csv'
)

# ---- Footer ----
st.markdown('---')
st.markdown(
    '<div style="text-align: center; color: #95a5a6; padding: 1rem;">'
    'Built with Streamlit | BetGuard v1.0 | Portfolio Project by Shivansh'
    '</div>',
    unsafe_allow_html=True
)
