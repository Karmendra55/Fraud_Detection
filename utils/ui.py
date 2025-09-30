import time
from contextlib import contextmanager
import streamlit as st
import pandas as pd

def inject_css():
    st.markdown(
        """
        <style>
            /* App background + typography */
            .main, .stApp {
                background: #0f1117;
                color: #e6e6e6;
                font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
            }

            /* Cards */
            .ui-card {
                background: #151826;
                border: 1px solid #23263a;
                border-radius: 16px;
                padding: 18px 18px 14px 18px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.25);
                margin-bottom: 1.2rem;
            }

            /* Section titles */
            .ui-section h2, .ui-section h3 {
                margin-top: 0.2rem;
                margin-bottom: 0.6rem;
                font-weight: 700;
                letter-spacing: 0.2px;
            }

            /* Metric tweaks */
            .stMetric {
                background: #151826;
                border: 1px solid #23263a;
                border-radius: 16px;
                padding: 10px 12px;
            }

            /* Dataframe corners */
            .stDataFrame, .stTable {
                border-radius: 16px !important;
                overflow: hidden !important;
            }

            /* Smooth fade-in */
            .fade-in {
                animation: fadeIn 420ms ease-in-out;
            }
            @keyframes fadeIn {
                0% { opacity: 0; transform: translateY(4px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            /* Sidebar polish */
            section[data-testid="stSidebar"] {
                background: #0c0e14;
                border-right: 1px solid #23263a;
            }

            /* Remove top padding jiggle */
            .block-container {
                padding-top: 1.2rem;
                padding-bottom: 2rem;
                max-width: 1400px;
            }

            /* Buttons */
            div.stButton > button {
                border-radius: 12px;
                background: linear-gradient(90deg, #0072ff, #00c6ff);
                color: white;
                border: none;
                font-weight: 600;
                transition: 0.2s ease-in-out;
            }
            div.stButton > button:hover {
                transform: scale(1.02);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def page_header(title: str, subtitle: str | None = None, icon: str | None = None):
    icon_html = f"<span style='margin-right:.5rem'>{icon}</span>" if icon else ""
    sub_html = f"<div style='color:#9aa4b5;margin-top:.25rem'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class="fade-in ui-section">
            <h2>{icon_html}{title}</h2>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_start():
    st.markdown('<div class="ui-card fade-in">', unsafe_allow_html=True)


def card_end():
    st.markdown('</div>', unsafe_allow_html=True)


def page_transition():
    st.markdown('<div class="fade-in"></div>', unsafe_allow_html=True)


# --- LOADING HELPERS ---
@contextmanager
def spinner(message: str = "Loading..."):
    with st.spinner(message):
        yield


def loading_bar(task_name: str = "Working...", steps: int = 6, delay: float = 0.15):
    progress = st.progress(0)
    status = st.empty()
    for i in range(steps):
        pct = int((i + 1) / steps * 100)
        status.write(f"{task_name} {pct}%")
        time.sleep(delay)
        progress.progress((i + 1) / steps)
    status.empty()
    progress.empty()


# ---COMMON WIDGETS ---
def dataframe(df: pd.DataFrame, caption: str | None = None, max_rows: int = 100):
    if caption:
        st.caption(caption)
    if df is not None and not df.empty:
        st.dataframe(df.head(max_rows), use_container_width=True)
    else:
        st.info("⚠️ No data available to display.")


def two_metrics(title_left: str, value_left: str, title_right: str, value_right: str):
    c1, c2 = st.columns(2)
    with c1:
        st.metric(title_left, value_left)
    with c2:
        st.metric(title_right, value_right)


def fraud_ratio_metrics(df: pd.DataFrame, target_col="TX_FRAUD"):
    if target_col not in df.columns:
        st.warning(f"Column `{target_col}` not found in DataFrame.")
        return
    vc = (df[target_col].value_counts(normalize=True) * 100).round(2)
    non_fraud = f"{vc.get(0, 0.0):.2f}%"
    fraud = f"{vc.get(1, 0.0):.2f}%"
    two_metrics("Non-Fraud", non_fraud, "Fraud", fraud)
