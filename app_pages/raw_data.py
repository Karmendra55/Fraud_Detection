import os, datetime
import streamlit as st
import pandas as pd
from src.data_loader import list_raw_files, load_raw_data
from utils.ui import page_header, page_transition, card_start, card_end, dataframe, spinner, loading_bar

def show():
    page_transition()
    page_header("📁 Raw Data Viewer", "Browse raw daily transaction files.")

    card_start()
    raw_files = list_raw_files("data")

    if not raw_files:
        st.warning("⚠️ No `.pkl` files found in `data/` folder.")
        card_end()
        return

    # --- File selection ---
    selected_file = st.selectbox("Select a transaction file", raw_files, index=0)

    file_path = f"data/{selected_file}"
    file_stats = os.stat(file_path)

    with spinner(f"Loading `{selected_file}`..."):
        df = load_raw_data(file_path)
    loading_bar("Preparing data", steps=3, delay=0.1)

    # --- File info metrics ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", f"{df.shape[1]}")
    col3.metric("Size (MB)", f"{file_stats.st_size/1e6:.2f}")
    col4.metric("Last Modified", datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime("%b %d, %Y"))

    st.markdown("---")

    # --- Preview Options ---
    st.subheader("🔎 Data Preview Options")

    max_rows = df.shape[0]
    col1, col2 = st.columns([3, 3])
    with col1:
        start_idx = st.number_input("Start row", 0, max_rows - 1, 0)
    with col2:
        end_idx = st.number_input("End row", start_idx + 1, max_rows, min(start_idx + 100, max_rows))

    preview_df = df.iloc[start_idx:end_idx]

    # --- Search filter ---
    search_term = st.text_input("🔍 Search (case-insensitive, across all text columns)", "")
    if search_term.strip():
        mask = df.apply(
            lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1
        )
        preview_df = df[mask].iloc[start_idx:end_idx]

    dataframe(preview_df, caption=f"Rows {start_idx:,} to {end_idx:,}")

    # --- Expanders for more info ---
    with st.expander("📑 Column Information", expanded=False):
        st.write(pd.DataFrame({
            "Column": df.columns,
            "Datatype": [str(dtype) for dtype in df.dtypes],
            "Non-Null Count": df.notnull().sum().values
        }))

    with st.expander("📊 Quick Statistics", expanded=False):
        st.write(df.describe(include="all").transpose())

    card_end()
