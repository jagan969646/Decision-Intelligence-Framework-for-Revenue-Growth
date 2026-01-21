import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os

# Set page configuration
st.set_page_config(
    page_title="Decision Intelligence Dashboard", 
    page_icon="📊",
    layout="wide"
)

# --- DYNAMIC PATH HANDLING ---
# This locates the folder where app.py is sitting on the server
current_dir = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    return os.path.join(current_dir, filename)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    forecast_df = pd.read_csv(get_file_path('revenue_forecast_scenarios.csv'))
    roi_df = pd.read_csv(get_file_path('roi_simulation_results.csv'))
    segment_df = pd.read_csv(get_file_path('segment_decision_summary.csv'))
    
    # Ensure Date column is in datetime format
    forecast_df['Date'] = pd.to_datetime(forecast_df['Date'], dayfirst=True)
    return forecast_df, roi_df, segment_df

# --- UI HEADER (Logo and Title Above Navigation) ---
header_col1, header_col2 = st.columns([1, 4])

with header_col1:
    try:
        logo_path = get_file_path('Mu_sigma_logo.jpg')
        logo_img = Image.open(logo_path)
        st.image(logo_img, width=160)
    except Exception:
        st.info("Logo Placeholder")

with header_col2:
    st.markdown("""
        <div style="padding-top: 10px;">
            <h1 style='margin-bottom: 0px;'>Decision Intelligence Dashboard</h1>
            <p style='font-size: 1.3rem; color: #666;'>Revenue Growth & Risk Management</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Global Data Load
try:
    forecast_df, roi_df, segment_df = load_data()
except Exception as e:
    st.error(f"⚠️ Critical Error: Data files not found. Error details: {e}")
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.header("Navigation")
page = st.sidebar.radio("Navigate to:", 
    ["Executive Summary", "Customer Segmentation", "Revenue Forecasting", "ROI Analysis"])

# --- PAGE 1: EXECUTIVE SUMMARY ---
if page == "Executive Summary":
    st.header("📊 Executive Summary")
    
    # Top Level KPI Metrics
    m1, m2, m3, m4 = st.columns(4)
    total_customers = int(segment_df['Customer_Count'].sum())
    total_gain = roi_df['Projected_Gain'].sum()
    avg_roi = roi_df['ROI'].mean()
    total_inv = roi_df['Investment'].sum()

    m1.metric("Total Customers", f"{total_customers:,}")
    m2.metric("Projected Gain", f"${total_gain:,.0f}")
    m3.metric("Avg ROI Multiplier", f"{avg_roi:,.1f}x")
    m4.metric("Total Investment", f"${total_inv:,.0f}")

    st.markdown("### Strategic Overview")
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(segment_df, values='Customer_Count', names='Decision_Action', 
                         title="Customers by Strategic Action", hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with c2:
        fig_bar = px.bar(roi_df.sort_values('ROI', ascending=False), x='Segment', y='ROI', 
                         title="ROI Efficiency per Segment", color='ROI', 
                         color_continuous_scale='GnBu')
        st.plotly_chart(fig_bar, use_container_width=True)

# --- PAGE 2: CUSTOMER SEGMENTATION ---
elif page == "Customer Segmentation":
    st.header("👥 Customer Segmentation Analysis")
    
    st.subheader("Segment Performance Data")
    try:
        # Styled dataframe (requires matplotlib in requirements.txt)
        st.dataframe(segment_df.style.background_gradient(subset=['Avg_Monetary'], cmap='Blues'), use_container_width=True)
    except ImportError:
        # Fallback if matplotlib isn't detected yet
        st.dataframe(segment_df, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("RFM: Recency vs Frequency")
        fig_scat = px.scatter(segment_df, x='Avg_Recency', y='Avg_Frequency', 
                             size='Customer_Count', color='Decision_Action',
                             hover_name='Decision_Action', text='Cluster')
        st.plotly_chart(fig_scat, use_container_width=True)
    
    with col2:
        st.subheader("Monetary Value by Cluster")
        fig_mon = px.bar(segment_df, x='Cluster', y='Avg_Monetary', color='Decision_Action')
        st.plotly_chart(fig_mon, use_container_width=True)

# --- PAGE 3: REVENUE FORECASTING ---
elif page == "Revenue Forecasting":
    st.header("📈 Revenue Forecasting Scenarios")
    
    scenarios = st.multiselect("Select Scenarios to Compare:", 
                               ['Base_Forecast', 'Best_Case', 'Worst_Case'], 
                               default=['Base_Forecast'])

    fig_forecast = go.Figure()

    # Add Shaded 95% Confidence Interval
    fig_forecast.add_trace(go.Scatter(
        x=forecast_df['Date'].tolist() + forecast_df['Date'].tolist()[::-1],
        y=forecast_df['Upper_CI'].tolist() + forecast_df['Lower_CI'].tolist()[::-1],
        fill='toself', fillcolor='rgba(100,100,100,0.1)', 
        line_color='rgba(255,255,255,0)', name='95% Confidence Interval'
    ))

    # Add Line Scenarios
    colors = {'Base_Forecast': '#1f77b4', 'Best_Case': '#2ca02c', 'Worst_Case': '#d62728'}
    for scenario in scenarios:
        fig_forecast.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df[scenario], 
                                         name=scenario, line=dict(width=3, color=colors[scenario])))

    fig_forecast.update_layout(
        title="6-Month Revenue Projection",
        xaxis_title="Timeline", yaxis_title="Revenue ($)",
        hovermode="x unified", template="plotly_white"
    )
    st.plotly_chart(fig_forecast, use_container_width=True)
    st.info("Shaded area represents the statistical variance of the Base Forecast.")

# --- PAGE 4: ROI ANALYSIS ---
elif page == "ROI Analysis":
    st.header("💰 Investment & ROI Simulation")
    
    st.subheader("Investment Efficiency (Investment vs Gain)")
    fig_roi_bar = go.Figure(data=[
        go.Bar(name='Investment', x=roi_df['Segment'], y=roi_df['Investment'], marker_color='indianred'),
        go.Bar(name='Projected Gain', x=roi_df['Segment'], y=roi_df['Projected_Gain'], marker_color='lightseagreen')
    ])
    fig_roi_bar.update_layout(barmode='group', template="plotly_white")
    st.plotly_chart(fig_roi_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Segment Deep Dive")
    sel_seg = st.selectbox("Select Segment for Detailed Metrics:", roi_df['Segment'].unique())
    seg_data = roi_df[roi_df['Segment'] == sel_seg].iloc[0]
    
    d1, d2, d3 = st.columns(3)
    d1.metric("ROI Ratio", f"{seg_data['ROI']:.2f}x")
    d2.metric("Break-Even Revenue", f"${seg_data['BreakEven_Revenue']:,.2f}")
    
    efficiency_score = seg_data['Projected_Gain'] / seg_data['Investment']
    d3.metric("Profit Multiplier", f"{efficiency_score:.1f}x")
