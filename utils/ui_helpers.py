import streamlit as st
import time
import pandas as pd

# -------------------------------
# Page Transitions / Animations
# -------------------------------
def page_transition():
    """Apply a smooth fade-in animation when navigating to a new page."""
    st.markdown("""
        <style>
            .fade-in {
                animation: fadeIn 0.6s ease-in-out;
            }
            @keyframes fadeIn {
                0% {opacity: 0;}
                100% {opacity: 1;}
            }
        </style>
        <div class="fade-in"></div>
    """, unsafe_allow_html=True)


# -------------------------------
# Progress + Loading Animation
# -------------------------------
def loading_with_progress(task_name: str, steps: int = 5, delay: float = 0.3):
    """Show a progress bar with % completion for long-running tasks."""
    progress = st.progress(0)
    status = st.empty()
    for i in range(steps):
        pct = int((i + 1) / steps * 100)
        status.text(f"{task_name}... {pct}%")
        time.sleep(delay)
        progress.progress((i + 1) / steps)
    status.success(f"✅ {task_name} complete!")
    progress.empty()


# ----------------------
# DataFrame Preview
# ----------------------
def show_dataframe(df: pd.DataFrame, max_rows: int = 100):
    """Safely display a DataFrame preview with limited rows."""
    if df is not None and not df.empty:
        st.dataframe(df.head(max_rows), use_container_width=True)
    else:
        st.info("⚠️ No data available to display.")


# -------------------------
# Fraud Ratio Summary
# -------------------------
def show_fraud_ratio(df: pd.DataFrame, target_col: str = "TX_FRAUD"):
    """Display fraud vs non-fraud ratio using Streamlit metrics."""
    if target_col not in df.columns:
        st.warning(f"Column `{target_col}` not found in DataFrame.")
        return

    fraud_counts = df[target_col].value_counts(normalize=True) * 100
    col1, col2 = st.columns(2)
    col1.metric("Non-Fraud %", f"{fraud_counts.get(0, 0):.2f}%")
    col2.metric("Fraud %", f"{fraud_counts.get(1, 0):.2f}%")

# --- Toast Notifications ---

def notify(message: str, icon: str = "ℹ️"):
    """Quick toast notification wrapper."""
    try:
        st.toast(f"{icon} {message}")
    except Exception:
        # fallback for older streamlit versions
        st.info(f"{icon} {message}")
