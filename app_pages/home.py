# app_pages/home.py
import streamlit as st
import random, datetime
from utils.ui import page_header, page_transition

@st.cache_data
def _get_app_info():
    return {
        "title": "🛡️ Fraud Detection Dashboard",
        "intro": """
            Welcome to the **Fraud Detection Web App**!  

            This interactive platform helps you **analyze transactions**, **detect fraud patterns**, 
            and **visualize insights** — all in one place.
        """,
        "objective": """
            ### 🎯 Objective
            To build an **AI-powered fraud detection system** that flags suspicious transactions in real-time.
        """,
        "fraud_rules": [
            "💰 Transactions over **$220** are flagged as high-risk.",
            "🏧 Certain terminals show fraudulent activity for **28 consecutive days**.",
            "👤 High-value frauds detected for certain customers over **14 days**."
        ],
        "faq": {
            "📘 What is this app?": """
                The **Fraud Detection Dashboard** helps you identify potentially fraudulent transactions
                using machine learning. You can analyze single or batch transactions and generate
                PDF reports with visual insights.
            """,
            "🤖 How does it predict?": """
                The model evaluates transaction patterns, amounts, terminal usage, and time-based trends.
                It then outputs:
                - **Fraud Probability** (% chance of being fraudulent)
                - **Fraud / Not Fraud Label**
            """,
            "🧠 Model Details": """
                - **Algorithm**: Random Forest Classifier (fine-tuned)  
                - **Training Data**: Historical transaction data with engineered fraud scenarios  
                - **Preprocessing**: Encoding + scaling + temporal feature extraction  
                - **Evaluation Metric**: ROC-AUC, Precision, Recall  
            """,
            "📄 Outputs & Features": """
                - CSV & PDF report generation  
                - Fraud trend visualizations  
                - Fraud mapping by location  
                - Detailed probability distribution analysis  
            """,
            "📬 Feedback & Credits": """
                - Developed by **Karmendra Bahadur Srivastava**  
                - Dataset by Unified Mentor & scenarios simulated for demonstration  
                - Email: **[Click Here](mailto:karmendra5902@gmail.com)**  
            """,
        },
    }


def captions():
    return [
        "🧭 Navigate the different features from the sidebar.",
        "👋 Use the sidebar to navigate across pages.",
        "📧 Want to send Feedback? Check the About → Feedback & Credits section.",
        "🧮 The About section explains everything about this project.",
        "❓ Did you know? Transactions over $220 are marked as high-risk.",
        "📂 Use the Raw Data Viewer to preview the dataset before analysis.",
        "💾 Raw Data shows original saved data without alteration.",
        "⚙ Feature Engineering gives dataset overview & downloadable files.",
        "🤖 Prediction lets you enter variables for instant fraud check.",
        "📊 Single prediction results include graphs, SHAP, and raw features.",
        "📟 Batch Prediction parses many transactions in one go.",
        "🧾 Batch results summarize fraud outcomes for all transactions.",
    ]


def show():
    page_transition()
    info = _get_app_info()

    # --- Sidebar Greeting ---
    with st.sidebar:
        st.sidebar.success("👋 Use the sidebar to navigate across pages.")
        st.markdown("---")

    # --- Header ---
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "☀️ Good Morning!"
    elif hour < 18:
        greeting = "🌤️ Good Afternoon!"
    else:
        greeting = "🌙 Good Evening!"

    page_header(info["title"], greeting)

    st.markdown(info["intro"])
    st.markdown("---")

    st.markdown(info["objective"])
    st.markdown("#### Simulated Fraud Scenarios in Our Model:")
    for rule in info["fraud_rules"]:
        st.markdown(f"- {rule}")

    st.markdown("---")
    st.subheader("📊 Features")

    # --- Custom CSS for card styling ---
    card_style = """
    <style>
    .feature-card {
        background-color: #000000;
        padding: 20px 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        text-align: center;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)
    # ---- Display feature cards ----
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="feature-card">🔧 Feature Engineering Data</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="feature-card">🤖 Fraud Prediction System</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="feature-card">📃 Batching Fraud Prediction</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("ℹ️ About This App")

    for title, content in info["faq"].items():
        with st.expander(title, expanded=False):
            st.markdown(content)

    # --- ooter ---
    st.markdown("---")
    st.caption("💡 Tip: Use the sidebar to explore all available tools and datasets.")
