import streamlit as st
import pandas as pd
import io
from utils import ui 

st.set_page_config(page_title="Sample Dataset Viewer", layout="wide")
ui.inject_css()
ui.page_transition()

# --- Title ---
ui.page_header("📊 Sample Dataset Viewer", subtitle="Inspect and explore uploaded datasets")

# --- File Input ---
uploaded_file = st.file_uploader("📂 Upload a dataset (.pkl)", type=["pkl"])

if uploaded_file:
    df = pd.read_pickle(uploaded_file)
else:
    df = pd.read_pickle("data/2018-04-01.pkl")

# --- Dataset Info ---
ui.page_header("🔍 Dataset Info")

# Capture df.info()
buf = io.StringIO()
df.info(buf=buf)
info_str = buf.getvalue()

with st.expander("📑 DataFrame Info"):
    st.text(info_str)

# Shape & column details in a card
ui.card_start()
ui.two_metrics("Rows", f"{df.shape[0]:,}", "Columns", f"{df.shape[1]:,}")
ui.card_end()

# Column types
with st.expander("🧩 Column Types"):
    st.dataframe(df.dtypes.to_frame("dtype"), use_container_width=True)

# --- Data Preview with filters ---
ui.page_header("👁️ Preview Data")

if st.checkbox("🔧 Filter columns"):
    selected_cols = st.multiselect(
        "Select columns to view",
        df.columns.tolist(),
        default=df.columns.tolist()
    )
    ui.dataframe(df[selected_cols], caption="Filtered preview (first 100 rows)")
else:
    ui.dataframe(df, caption="First 100 rows")

# --- Extra polish: Smooth transitions (CSS) ---
st.markdown(
    """
    <style>
    div[data-testid="stExpander"] {
        transition: all 0.3s ease-in-out;
    }
    </style>
    """,
    unsafe_allow_html=True
)
