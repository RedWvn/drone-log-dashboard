
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Drone Log Dashboard", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().replace('"', '') for col in df.columns]
    df['Date'] = pd.to_datetime(df['Date (YYYY-MM-DD HH:MM:SS)'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Duration (minutes)'] = df['Duration (seconds)'] / 60
    return df

st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Helvetica Neue', sans-serif;
            background-color: #ffffff;
            color: #222222;
        }
        .block-container {
            padding: 2rem 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🛸 Drone Flight Dashboard")

uploaded_file = st.sidebar.file_uploader("📤 Upload Drone Log CSV", type="csv")

if uploaded_file:
    df = load_data(uploaded_file)

    st.markdown("### ✈️ Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Flights", len(df))
    with col2:
        st.metric("Total Flight Hours", round(df['Duration (minutes)'].sum() / 60, 2))
    with col3:
        st.metric("Avg. Flight Duration (min)", round(df['Duration (minutes)'].mean(), 2))
    with col4:
        st.metric("Max Altitude (m)", int(df['Max Altitude ( m)'].max()))

    st.markdown("---")

    with st.container():
        st.subheader("📅 Daily Flight Count")
        st.caption("Shows the number of flights logged per day to highlight operational intensity over time.")
        daily_counts = df.groupby(df['Date'].dt.date).size().reset_index(name='Flight Count')
        fig1 = px.line(daily_counts, x='Date', y='Flight Count', title="Flights Per Day")
        st.plotly_chart(fig1, use_container_width=True)

    with st.container():
        st.subheader("⏱️ Daily Total Flight Duration")
        st.caption("Visualizes the total flight time in minutes for each day.")
        daily_durations = df.groupby(df['Date'].dt.date)['Duration (minutes)'].sum().reset_index()
        fig2 = px.line(daily_durations, x='Date', y='Duration (minutes)', title="Daily Flight Duration (minutes)")
        st.plotly_chart(fig2, use_container_width=True)

    with st.container():
        st.subheader("🌤️ Weather Impact on Flight Duration")
        st.caption("Correlates various weather factors with flight duration to evaluate environmental impacts.")
        weather_cols = ['Cloud Cover %', 'Temperature', 'Wind', 'Humidity']
        for col in weather_cols:
            if col in df.columns:
                fig = px.scatter(df, x=col, y='Duration (minutes)', title=f"{col} vs Duration")
                st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.subheader("🧑‍✈️ Flights Per Pilot")
        st.caption("Distribution of flights conducted by each pilot.")
        if 'Pilot in Command Email' in df.columns:
            pilot_stats = df['Pilot in Command Email'].value_counts().reset_index()
            pilot_stats.columns = ['Pilot', 'Flights']
            fig = px.bar(pilot_stats, x='Pilot', y='Flights', title='Flights by Pilot')
            st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.subheader("📍 Flights Per Project")
        st.caption("Total number of flights associated with each project.")
        if 'ProjectGUID' in df.columns:
            project_stats = df['ProjectGUID'].value_counts().reset_index()
            project_stats.columns = ['Project', 'Flights']
            fig = px.bar(project_stats, x='Project', y='Flights', title='Flights by Project')
            st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.subheader("📊 Flight Type Breakdown")
        st.caption("Categorical breakdown of flight types logged in the dataset.")
        if 'Flight Type' in df.columns:
            type_counts = df['Flight Type'].value_counts().reset_index()
            type_counts.columns = ['Type', 'Count']
            fig = px.pie(type_counts, names='Type', values='Count', title='Flight Types')
            st.plotly_chart(fig, use_container_width=True)
