import streamlit as st
import sqlite3
import pandas as pd
import os
import datetime

# Define database path
backup_dir = os.path.join(os.path.dirname(__file__), 'DB_Backup')
os.makedirs(backup_dir, exist_ok=True)
db_path = os.path.join(backup_dir, 'etf_analysis.db')

# Function to get data from database
def get_data(query):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)

# Function to save uploaded CSV to a new table
def save_uploaded_csv(file):
    df = pd.read_csv(file)
    required_columns = ['NAME', 'SYMBOL', 'MT MULTIPLE', 'MAX ALLOWED EXPOSURE IN CR']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    table_name = f"Uploaded_{os.path.splitext(file.name)[0].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, index=False)
    return table_name, df

# Function to list all user-uploaded tables (those starting with 'Uploaded_')
def list_uploaded_tables():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Uploaded_%'")
        tables = [row[0] for row in cursor.fetchall()]
    return tables

# UI Header
st.set_page_config(page_title="ETF Analysis Dashboard", layout="wide")
st.title("📈 ETF Analysis Dashboard")

# Tabs for different reports
tabs = st.tabs(["Daily Status", "ROI Summary", "Trade Log", "📤 Upload CSV", "📂 View Uploads"])

# Tab 1: ETF_Daily_Status
with tabs[0]:
    st.subheader("📅 ETF Daily Status")
    try:
        df_daily = get_data("SELECT * FROM ETF_Daily_Status")
        st.dataframe(df_daily)
    except Exception as e:
        st.error(f"Failed to load Daily Status: {e}")

# Tab 2: ROI Summary
with tabs[1]:
    st.subheader("💹 ROI Summary by Symbol")
    try:
        df_roi = get_data("SELECT * FROM ETF_ROI")
        st.dataframe(df_roi)
        st.bar_chart(df_roi.set_index('Symbol')['ROI'])
    except Exception as e:
        st.error(f"Failed to load ROI Summary: {e}")

# Tab 3: Trade Log
with tabs[2]:
    st.subheader("📜 ETF Trade Log")
    try:
        df_trades = get_data("SELECT * FROM ETF_Trade_Log")
        st.dataframe(df_trades)
    except Exception as e:
        st.error(f"Failed to load Trade Log: {e}")

# Tab 4: Upload CSV
with tabs[3]:
    st.subheader("📤 Upload CSV File")
    uploaded_file = st.file_uploader("Upload CSV with ETF data (including NAME, SYMBOL, MT MULTIPLE, MAX ALLOWED EXPOSURE IN CR, and Date Columns)", type=["csv"])
    if uploaded_file:
        try:
            table_name, df_uploaded = save_uploaded_csv(uploaded_file)
            st.success(f"File uploaded and saved to table: {table_name}")
            st.dataframe(df_uploaded)
        except Exception as e:
            st.error(f"Failed to upload file: {e}")

# Tab 5: View Previous Uploads
with tabs[4]:
    st.subheader("📂 View Previously Uploaded Data")
    tables = list_uploaded_tables()
    selected_table = st.selectbox("Choose a table to view:", tables)
    if selected_table:
        try:
            df_selected = get_data(f"SELECT * FROM {selected_table}")
            st.dataframe(df_selected)
        except Exception as e:
            st.error(f"Failed to load table: {e}")
