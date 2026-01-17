import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os

# Set page configuration
st.set_page_config(page_title="Decision Intelligence Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    # Standard loading - assumes files are in the same folder as app.py
    forecast_df = pd.read_csv('revenue_forecast_scenarios.csv')
    roi_df = pd.read_csv('roi_simulation_results.csv')
    segment_df = pd.read_csv('segment_decision_summary.csv')
    
    # Preprocessing
    forecast_df['Date'] = pd.to_datetime(forecast_df['Date'], dayfirst=True)
    return forecast_df, roi_df, segment_df

# --- HEADER WITH LOGO ---
# We put this before data loading so the UI shows up even if data fails
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try:
        logo = Image.open('Mu_sigma_logo.jpg')
        st.image(logo, width=150)
    except:
        st.warning("Logo not found.")

with col_title:
    st.title("Decision Intelligence Dashboard for Revenue Growth & Risk Management")

st.markdown("---")

# Now attempt to load data
try:
    forecast_df, roi_df, segment_df = load_data()
except Exception as e:
    st.error(f"Data Loading Error: {e}")
    st.info("Ensure all CSV files are uploaded to the same folder as app.py in GitHub.")
    st.stop()

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Executive Summary", "Customer Segmentation", "Revenue Forecasting", "ROI Analysis"])

# --- PAGE 1: EXECUTIVE SUMMARY ---
if page == "Executive Summary":
    st.header("📊 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", f"{int(segment_df['Customer_Count'].sum()):,}")
    col2.metric("Projected Gain", f"${roi_df['Projected_Gain'].sum():,.2f}")
    col3.metric("Avg ROI", f"{roi_df['ROI'].mean():,.1f}x")
    col4.metric("Total Investment", f"${roi_df['Investment'].sum():,.0f}")

    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Customer Distribution")
        fig_seg = px.pie(segment_df, values='Customer_Count', names='Decision_Action', hole=0.4)
        st.plotly_chart(fig_seg, use_container_width=True)
    
    with c2:
        st.subheader("ROI by Segment")
        fig_roi = px.bar(roi_df.sort_values('ROI', ascending=False), x='Segment', y='ROI', color='ROI')
        st.plotly_chart(fig_roi, use_container_width=True)

# --- PAGE 2: CUSTOMER SEGMENTATION ---
elif page == "Customer Segmentation":
    st.header("👥 Customer Segmentation Analysis")
    st.dataframe(segment_df, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(segment_df, x='Avg_Recency', y='Avg_Frequency', size='Customer_Count', color='Decision_Action')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(segment_df, x='Cluster', y='Avg_Monetary', color='Decision_Action')
        st.plotly_chart(fig2, use_container_width=True)

# --- PAGE 3: REVENUE FORECASTING ---
elif page == "Revenue Forecasting":
    st.header("📈 Revenue Forecasting")
    scenarios = st.multiselect("Scenarios", ['Base_Forecast', 'Best_Case', 'Worst_Case'], default=['Base_Forecast'])

    fig = go.Figure()
    for s in scenarios:
        fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df[s], name=s))
    
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE 4: ROI ANALYSIS ---
elif page == "ROI Analysis":
    st.header("💰 ROI Simulation")
    fig = px.bar(roi_df, x='Segment', y=['Investment', 'Projected_Gain'], barmode='group')
    st.plotly_chart(fig, use_container_width=True)
