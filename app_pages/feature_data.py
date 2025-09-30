import os, datetime
import streamlit as st
import pandas as pd
from src.feature_engineering import load_processed_data
from utils.ui import (
    page_header, page_transition, card_start, card_end,
    dataframe, fraud_ratio_metrics, loading_bar, spinner
)

# --- Safe Loader ---
@st.cache_data(show_spinner=False)
def _load_feature_df(path: str) -> pd.DataFrame:
    df = load_processed_data(path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def show():
    page_transition()
    page_header("🔧 Feature Engineered Data", "Explore engineered features and class balance.")

    feature_path = "processed/feature_engineered_df.pkl"

    # -- Load with spinner ---
    try:
        with spinner("Loading feature-engineered dataset..."):
            df = _load_feature_df(feature_path)
        if df is None or df.empty:
            st.warning("⚠️ Loaded dataset is empty.")
            return
        loading_bar("Finalizing view…", steps=3, delay=0.08)
    except FileNotFoundError:
        st.error(f"❌ Could not find **{feature_path}**. Please generate it first.")
        return
    except Exception as e:
        st.exception(e)
        return

    # --- Dataset Overview ---
    card_start()
    st.markdown("### 📋 Dataset Overview")

    file_info = os.stat(feature_path)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Rows", f"{df.shape[0]:,}")
    with c2: st.metric("Columns", f"{df.shape[1]}")
    with c3: st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1_048_576:.2f} MB")
    with c4: st.metric("Last Updated", datetime.datetime.fromtimestamp(file_info.st_mtime).strftime("%b %d, %Y"))

    with st.expander("⚙️ Columns & Data Types", expanded=False):
        dtype_df = pd.DataFrame({
            "Column": df.columns,
            "Dtype": df.dtypes.astype(str),
            "Non-Null Count": df.notnull().sum().values
        })
        st.dataframe(dtype_df, use_container_width=True, height=320)

    card_end()

    # --- Fraud Ratio ---
    card_start()
    st.markdown("### ⚖️ Class Balance")
    if "TX_FRAUD" in df.columns:
        fraud_ratio_metrics(df, target_col="TX_FRAUD")
    
    # Exploratory Graphs 
    st.markdown("### 📊 Exploratory Graphs")
    graph1, graph2 = st.columns([1,1])

    with graph1:
        with st.expander("📈 Number of Transactions Over Time", expanded=False):
            if "TX_DATETIME" in df.columns:
                try:
                    df["TX_DATETIME"] = pd.to_datetime(df["TX_DATETIME"], errors="coerce")
                    tx_per_day = df.groupby(df["TX_DATETIME"].dt.date).size()
                    st.line_chart(tx_per_day, height=300, use_container_width=True)
                except Exception as e:
                    st.warning("Could not plot TX_DATETIME series.")
                    st.exception(e)
            else:
                st.info("`TX_DATETIME` column not found.")

        with st.expander("💵 Transaction Amount Distribution", expanded=False):
            if "TX_AMOUNT" in df.columns:
                bins = [0, 10, 50, 100, 500, 1000, 5000, 10000, float("inf")]
                labels = ["0-10", "10-50", "50-100", "100-500", "500-1k", "1k-5k", "5k-10k", "10k+"]
                df["AMOUNT_BIN"] = pd.cut(df["TX_AMOUNT"], bins=bins, labels=labels, include_lowest=True)
                amount_counts = df["AMOUNT_BIN"].value_counts().sort_index()
                st.bar_chart(amount_counts, height=300, use_container_width=True)
            else:
                st.info("`TX_AMOUNT` column not found.")

        with st.expander("👥 Top 10 Customers by Number of Transactions", expanded=False):
            if "CUSTOMER_ID" in df.columns:
                top_customers = df["CUSTOMER_ID"].value_counts().head(10)
                st.bar_chart(top_customers, height=300, use_container_width=True)
            else:
                st.info("`CUSTOMER_ID` column not found.")

    with graph2: 
        with st.expander("🏦 Top 10 Merchants by Number of Transactions", expanded=False):
            if "TERMINAL_ID" in df.columns:
                top_merchants = df["TERMINAL_ID"].value_counts().head(10)
                st.bar_chart(top_merchants, height=300, use_container_width=True)
            else:
                st.info("`TERMINAL_ID` column not found.")

        with st.expander("⏰ Transactions by Hour of Day", expanded=False):
            if "TX_HOUR" in df.columns:
                tx_per_hour = df["TX_HOUR"].value_counts().sort_index()
                st.bar_chart(tx_per_hour, height=300, use_container_width=True)
            else:
                st.info("`TX_HOUR` column not found.")

        with st.expander("📆 Transactions by Weekday", expanded=False):
            if "TX_WEEKDAY" in df.columns:
                tx_per_wd = df["TX_WEEKDAY"].value_counts().sort_index()
                st.bar_chart(tx_per_wd, height=300, use_container_width=True)
            else:
                st.info("`TX_WEEKDAY` column not found.")

    card_end()

    # --- Data Preview ----
    card_start()
    st.markdown("### 👀 Data Preview")
    
    with st.popover("💡 Tips"):
        st.markdown(
            "- Adjust the **row slider** to control preview size.\n"
            "- Use **column selector** to reduce load.\n"
            "- Download the preview for external analysis."
        )

    row_count = st.slider("Rows to preview", min_value=5, max_value=100, value=50, step=5)
    
    selected_cols = st.multiselect("Columns to display", df.columns.tolist(), default=df.columns.tolist()[:10])
    preview_df = df[selected_cols].head(row_count)

    dataframe(preview_df, caption=f"Showing first {row_count} rows and {len(selected_cols)} columns")

    csv_bytes = preview_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "💾 Download preview as CSV",
        data=csv_bytes,
        file_name="feature_data_preview.csv",
        mime="text/csv",
    )
    card_end()

    # --- Footer ---
    st.caption(
        "ℹ️ For deeper insights, use **Batch Prediction** to score CSV files "
        "or **Fraud Prediction** to test individual transactions."
    )
