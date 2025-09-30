import streamlit as st
import joblib
import pandas as pd
import numpy as np
import shap
import altair as alt

from src.probability_gauge import show_probability_gauge
from utils.ui import (
    inject_css, page_header, page_transition, spinner,
    loading_bar, card_end, card_start
)

# ---------------------------
# Cached assets
# ---------------------------
@st.cache_resource
def load_assets():
    try:
        saved = joblib.load("models/fraud_detection_model.pkl")
        return (
            saved["model"],
            saved["encoders"],
            saved.get("categorical_cols", []),
        )
    except Exception as e:
        st.error("❌ Could not load model assets.")
        st.exception(e)
        st.stop()

@st.cache_resource
def get_explainer(_model):
    try:
        return shap.Explainer(_model)
    except Exception:
        return None

# ---------------------------
# Helpers
# ---------------------------
def preprocess_input(data: pd.DataFrame, encoders: dict) -> pd.DataFrame:
    data = data.copy()
    for col, le in encoders.items():
        if col in data.columns:
            mapping = dict(zip(le.classes_, le.transform(le.classes_)))
            data[col] = data[col].map(mapping).fillna(-1).astype(int)
    feature_order = [
        "TX_AMOUNT",
        "TX_TIME_SECONDS",
        "TX_TIME_DAYS",
        "TX_HOUR",
        "TX_WEEKDAY",
        "TX_MONTH",
        "IS_WEEKEND",
        "TX_AMOUNT_BIN",
        "TX_COUNT",
    ]
    for c in list(data.columns):
        if c not in feature_order:
            data.drop(columns=[c], inplace=True)
    for c in feature_order:
        if c not in data.columns:
            data[c] = 0

    return data[feature_order]

def compute_shap_for_row(explainer, processed_row: pd.DataFrame) -> pd.Series:
    shap_values = explainer(processed_row)
    row_vals = shap_values.values[0]

    if row_vals.ndim == 2 and row_vals.shape[1] > 1:
        row_vals = row_vals[:, 1]
    elif row_vals.ndim == 2:
        row_vals = row_vals[:, 0]

    return pd.Series(row_vals, index=processed_row.columns)

def shap_bar_chart(shap_series: pd.Series, orig_row: pd.Series, top_n: int = 10):
    df = pd.DataFrame({
        "feature": shap_series.index,
        "shap": shap_series.values,
        "abs_shap": np.abs(shap_series.values),
        "value": [orig_row.get(f, None) for f in shap_series.index]
    }).sort_values("abs_shap", ascending=False).head(top_n)

    df["value_str"] = df["value"].astype(str)

    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("shap:Q", title="SHAP contribution (toward Fraud=1)"),
            y=alt.Y("feature:N", sort=df["feature"].tolist(), title="Feature"),
            tooltip=[
                alt.Tooltip("feature:N"),
                alt.Tooltip("value_str:N", title="Value"),
                alt.Tooltip("shap:Q", title="Contribution"),
                alt.Tooltip("abs_shap:Q", title="|Contribution|"),
            ],
            color=alt.condition("datum.shap > 0", alt.value("#d62728"), alt.value("#1f77b4")),
        )
        .properties(height=max(220, 20*len(df)), width="container")
    )

def init_store():
    if "saved_predictions" not in st.session_state:
        st.session_state["saved_predictions"] = [] 

def show():
    inject_css()
    page_transition()
    page_header("🔮 Fraud Prediction", "Single-transaction prediction with feature contributions.")

    model, encoders, categorical_cols = load_assets()
    explainer = get_explainer(model)
    init_store()

    # --- Input Form ---
    with st.form("single_tx_form"):
        st.subheader("Enter Transaction Details")

        TX_AMOUNT = st.number_input( "Transaction Amount", min_value=0.0, value=100.0, step=1.0, 
                                    help="The total value of the transaction in USD. Higher amounts can indicate higher fraud risk." ) 
        col1, col2, col3 = st.columns(3) 
        with col1: 
            TX_HOUR = st.slider( "Hour of Day (24-Hours)", 0, 23, 12, 
                                help="The hour (0-23) when the transaction took place. Some fraud patterns happen at odd hours." ) 
        with col2: 
            TX_MONTH = st.slider( "Month (Jan=1, Dec=12)", 1, 12, 6, 
                                 help="The month (1=January, 12=December) when the transaction occurred." ) 
        with col3: 
            TX_WEEKDAY = st.slider( "Weekday (0=Mon, 6=Sun)", 0, 6, 3, 
                                   help="The day of the week (0=Monday, 6=Sunday). Fraud patterns may differ between weekdays and weekends." ) 
        
        col4, col5 = st.columns(2) 
        with col4: 
            IS_WEEKEND = st.selectbox( "Is Weekend(0=No, 1=Yes)", [0, 1], index=0, 
                                      help="1 if the transaction occurred on a weekend, 0 otherwise." ) 
        with col5: 
            TX_AMOUNT_BIN = st.selectbox( "Amount Bin (Range of Transaction)", ["0-10", "10-50", "50-100", "100-500", "500-1000", "1000-5000", "5000+"], index=3, 
                                         help="Predefined range of the transaction amount. Helps model understand amount categories." ) 
        
        col6, col7, col8 = st.columns(3) 
        with col6: 
            TX_COUNT = st.number_input( "Customer's Tax Count", min_value=0, value=10, step=1, 
                                       help="The number of transactions the customer made before this one." ) 
        with col7: 
            TX_TIME_DAYS = st.number_input( "Time (in Days)", min_value=0, value=100, step=1, 
                                           help="Time since the start of the dataset in days." ) 
        with col8: 
            TX_TIME_SECONDS = st.number_input( "Time (in Seconds)", min_value=0, value=10_000, step=1_000, 
                                              help="Time since the start of the month in seconds. Can help spot unusual timing." )

        submitted = st.form_submit_button("🔍 Predict")

    if not submitted:
        st.info("Fill the fields and click **Predict** to see results.")
        return

    # --- Build Input ---
    raw_row = pd.Series({
        "TX_AMOUNT": TX_AMOUNT,
        "TX_TIME_SECONDS": TX_TIME_SECONDS,
        "TX_TIME_DAYS": TX_TIME_DAYS,
        "TX_HOUR": TX_HOUR,
        "TX_WEEKDAY": TX_WEEKDAY,
        "TX_MONTH": TX_MONTH,
        "IS_WEEKEND": IS_WEEKEND,
        "TX_AMOUNT_BIN": TX_AMOUNT_BIN,
        "TX_COUNT": TX_COUNT,
    })
    input_df = pd.DataFrame([raw_row])
    processed_df = preprocess_input(input_df, encoders)

    # --- Predict --
    with spinner("Scoring transaction..."):
        loading_bar("Processing", steps=5, delay=0.1)
        try:
            proba = float(model.predict_proba(processed_df)[:, 1][0])
            pred = int(model.predict(processed_df)[0])
        except Exception as e:
            st.error("❌ Prediction failed.")
            st.exception(e)
            return

    # --- Results ---
    show_probability_gauge(proba)

    st.metric(
        "Fraud Result",
        value="🛑 Fraud" if pred == 1 else "✅ Not Fraud",

        delta_color="normal" if pred == 1 else "inverse",
    )

    # --- Model Input ---
    card_start()
    st.markdown("### Model Input (Encoded)")
    st.dataframe(processed_df, use_container_width=True)
    card_end()

    # --- SHAP Explanation ---
    card_start()
    st.subheader("Top Feature Contributions (SHAP)")
    try:
        if explainer:
            shap_series = compute_shap_for_row(explainer, processed_df)
            st.altair_chart(shap_bar_chart(shap_series, raw_row, top_n=10), use_container_width=True)

            with st.expander("📊 View raw SHAP values"):
                shap_df = pd.DataFrame({
                    "feature": shap_series.index,
                    "value": [raw_row.get(f, None) for f in shap_series.index],
                    "shap": shap_series.values,
                    "abs_shap": np.abs(shap_series.values),
                }).sort_values("abs_shap", ascending=False)
                st.dataframe(shap_df, use_container_width=True)
        else:
            st.info("SHAP explanation not available for this model type.")
    except Exception as e:
        st.warning("⚠️ SHAP explanation failed.")
        st.exception(e)
    card_end()
