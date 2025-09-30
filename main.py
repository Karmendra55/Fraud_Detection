import streamlit as st
import random, time, importlib

from app_pages import home
from streamlit_option_menu import option_menu
from utils.ui import inject_css, page_transition

# --- Page Config & Caching ---
st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🛡️",
    layout=st.session_state.get("layout", "centered")
)

@st.cache_resource
def load_global_ui():
    inject_css()
    page_transition()

load_global_ui()

# --- Page Registry ---
PAGES = {
    "🏠 Home": "app_pages.home",
    "📁 Raw Data Viewer": "app_pages.raw_data",
    "🔧 Feature Engineered Data": "app_pages.feature_data",
    "🤖 Fraud Prediction": "app_pages.prediction",
    "📃 Batch Fraud Prediction": "app_pages.batch_prediction",
}

# --- Sidebar Navigation ---
with st.sidebar:
    st.header("📜 Dashboard")
    selected = option_menu(
        menu_title="Navbar",
        options=list(PAGES.keys()),
        menu_icon="menu-up",
        default_index=0,
        orientation="vertical",
    )
    st.markdown("---")

# --- Page Loader ---
def load_page(page_module: str):
    """Dynamically import and display a page."""
    try:
        module = importlib.import_module(page_module)
        if hasattr(module, "show"):
            module.show()
        else:
            st.error(f"⚠️ Page `{page_module}` is missing a `show()` function.")
    except ImportError as e:
        st.error(f"⚠️ Failed to load the page: `{e}`")
    except Exception as e:
        st.error(f"🚨 Unexpected error: {e}")


# --- Render Selected Page ----
load_page(PAGES[selected])
    
with st.sidebar:    
    # Sidebar caption
    if "sidebar_caption" not in st.session_state:
        st.session_state.sidebar_caption = random.choice(home.captions())
        st.session_state.caption_time = time.time()
    if time.time() - st.session_state.caption_time > 120:
        st.session_state.sidebar_caption = random.choice(home.captions())
        st.session_state.caption_time = time.time()
        st.rerun()
    st.markdown(f"<small>{st.session_state.sidebar_caption}</small>", unsafe_allow_html=True)