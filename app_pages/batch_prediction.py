import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image
import time

from app_pages.prediction import load_assets, preprocess_input

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        padding: 20px;
    }
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .metric-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        background-color: white;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)

# --- Helpers ---
@st.cache_resource
def cached_assets():
    return load_assets()

@st.cache_data
def read_csv_file(file):
    return pd.read_csv(file)

def get_template_df():
    return pd.DataFrame([
        {"TX_AMOUNT": 120.0, "TX_TIME_SECONDS": 5000, "TX_TIME_DAYS": 100,
         "TX_HOUR": 14, "TX_WEEKDAY": 2, "TX_MONTH": 5, "IS_WEEKEND": 0,
         "TX_AMOUNT_BIN": "100-500", "TX_COUNT": 7},
        {"TX_AMOUNT": 2500.0, "TX_TIME_SECONDS": 36000, "TX_TIME_DAYS": 150,
         "TX_HOUR": 3, "TX_WEEKDAY": 6, "TX_MONTH": 8, "IS_WEEKEND": 1,
         "TX_AMOUNT_BIN": "1000-5000", "TX_COUNT": 25}
    ])

def generate_pdf_with_charts(results_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # --- Report title & timestamp ---
    elements.append(Paragraph("Batch Fraud Prediction Report", styles["Title"]))
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Report Generated On: {report_date}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # --- Compute TX_DATETIME if time columns exist ---
    if "TX_TIME_DAYS" in results_df.columns and "TX_TIME_SECONDS" in results_df.columns:
        base_date = pd.Timestamp("2020-01-01") 
        results_df["TX_DATETIME"] = (
            base_date
            + pd.to_timedelta(results_df["TX_TIME_DAYS"], unit="D")
            + pd.to_timedelta(results_df["TX_TIME_SECONDS"], unit="s")
        )
    else:
        results_df["TX_DATETIME"] = None

    # --- Fraud Pattern Statistics ---
    fraud_df = results_df[results_df["prediction_label"] == "Fraud"]

    fraud_rate = len(fraud_df) / len(results_df) if len(results_df) > 0 else 0
    avg_fraud_amount = fraud_df["TX_AMOUNT"].mean() if not fraud_df.empty else 0
    common_hour = fraud_df["TX_HOUR"].mode()[0] if "TX_HOUR" in fraud_df.columns and not fraud_df.empty else "-"
    common_day = fraud_df["TX_WEEKDAY"].mode()[0] if "TX_WEEKDAY" in fraud_df.columns and not fraud_df.empty else "-"

    kpi_data = [
        ["Metric", "Value"],
        ["% Fraudulent Transactions", f"{fraud_rate:.2%}"],
        ["Average Fraud Amount", f"${avg_fraud_amount:,.2f}"],
        ["Most Common Fraud Hour", common_hour],
        ["Most Common Fraud Day (0=Mon)", common_day]
    ]

    kpi_table = Table(kpi_data)
    kpi_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER")
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 12))

    # --- Fraud Count Chart ---
    count_buf = io.BytesIO()
    counts = results_df["prediction_label"].value_counts()
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(counts.index, counts.values, color=["red", "green"])
    ax.set_ylabel("Count")
    ax.set_title("Fraud vs Non-Fraud")
    plt.tight_layout()
    plt.savefig(count_buf, format="png")
    plt.close(fig)
    count_buf.seek(0)
    elements.append(Image(count_buf, width=300, height=200))
    elements.append(Spacer(1, 12))

    # --- Probability Distribution Chart ---
    prob_buf = io.BytesIO()
    fig2, ax2 = plt.subplots(figsize=(4, 3))
    ax2.hist(results_df["fraud_probability"], bins=20, color="blue", alpha=0.7)
    ax2.set_xlabel("Fraud Probability")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Fraud Probability Distribution")
    plt.tight_layout()
    plt.savefig(prob_buf, format="png")
    plt.close(fig2)
    prob_buf.seek(0)
    elements.append(Image(prob_buf, width=300, height=200))
    elements.append(Spacer(1, 12))

    # --- Detailed Table ---
    table_data = [["TX_AMOUNT", "Fraud Probability", "Prediction Label", "TX_DATETIME"]]
    for _, row in results_df.iterrows():
        tx_dt_str = row["TX_DATETIME"].strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(row["TX_DATETIME"]) else "-"
        table_data.append([
            row["TX_AMOUNT"],
            f"{row['fraud_probability']:.2%}",
            row["prediction_label"],
            tx_dt_str
        ])
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER")
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer



def generate_detailed_single_pdf(input_data, prob, pred_label, shap_values=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # --- Title ---
    elements.append(Paragraph("Single Transaction Fraud Prediction Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"<b>Prediction:</b> {pred_label}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Fraud Probability:</b> {prob:.2%}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # --- Gauge Chart for probability ---
    gauge_buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(3, 1.5))
    ax.barh([0], [prob], color="red" if prob > 0.5 else "green")
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel("Fraud Probability")
    ax.set_title("Fraud Risk Gauge")
    plt.tight_layout()
    plt.savefig(gauge_buf, format="png")
    plt.close(fig)
    gauge_buf.seek(0)
    elements.append(Image(gauge_buf, width=200, height=100))
    elements.append(Spacer(1, 12))

    # --- SHAP/Feature Importance chart ---
    if shap_values:
        shap_buf = io.BytesIO()
        features = list(shap_values.keys())
        values = list(shap_values.values())
        fig2, ax2 = plt.subplots(figsize=(4, 3))
        ax2.barh(features, values, color="blue")
        ax2.set_title("Feature Impact (SHAP values)")
        ax2.set_xlabel("Impact")
        plt.tight_layout()
        plt.savefig(shap_buf, format="png")
        plt.close(fig2)
        shap_buf.seek(0)
        elements.append(Image(shap_buf, width=300, height=200))
        elements.append(Spacer(1, 12))

    # --- Feature Table ---
    table_data = [["Feature", "Value"]] + [[k, v] for k, v in input_data.items()]
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER")
    ]))
    elements.append(table)

    # Build PDF ---
    doc.build(elements)
    buffer.seek(0)
    return buffer

def show():
    st.title("📂 Batch Fraud Prediction")
    st.markdown("Easily upload a CSV file to score multiple transactions at once.")

    model, encoders, _ = cached_assets()
    with st.expander("📄 Download Input Template"):
        st.write("Use this template format to prepare your CSV for batch prediction.")
        template_df = get_template_df()
        csv_buffer = io.StringIO()
        template_df.to_csv(csv_buffer, index=False)
        st.download_button(
            "📥 Download CSV Template",
            csv_buffer.getvalue(),
            file_name="fraud_batch_template.csv",
            mime="text/csv"
        )

    uploaded_file = st.file_uploader("📤 Upload your CSV file", type=["csv"])

    if uploaded_file:
        try:
            with st.spinner("📊 Reading and preprocessing data..."):
                input_df = read_csv_file(uploaded_file)
                required_cols = [
                    "TX_AMOUNT", "TX_TIME_SECONDS", "TX_TIME_DAYS",
                    "TX_HOUR", "TX_WEEKDAY", "TX_MONTH", "IS_WEEKEND",
                    "TX_AMOUNT_BIN", "TX_COUNT"
                ]
                missing_cols = [col for col in required_cols if col not in input_df.columns]

                if missing_cols:
                    st.error(f"⚠️ Your file is missing required columns: {', '.join(missing_cols)}, Please Download the Templete and Update it accordingly.")
                    st.stop()

                if input_df.isnull().values.any():
                    st.warning("⚠️ Missing values detected — they will be filled with defaults.")
                    input_df = input_df.fillna({
                        "TX_AMOUNT": 0,
                        "TX_TIME_SECONDS": 0,
                        "TX_TIME_DAYS": 0,
                        "TX_HOUR": 0,
                        "TX_WEEKDAY": 0,
                        "TX_MONTH": 1,
                        "IS_WEEKEND": 0,
                        "TX_AMOUNT_BIN": "Unknown",
                        "TX_COUNT": 0
                    })

                processed_df = preprocess_input(input_df, encoders)

            progress_text = "Running batch predictions..."
            my_bar = st.progress(0, text=progress_text)
            for pct in range(100):
                time.sleep(0.01)
                my_bar.progress(pct + 1, text=progress_text)
            my_bar.empty()

            try:
                proba = model.predict_proba(processed_df)[:, 1]
                preds = model.predict(processed_df)
            except Exception:
                st.error("⚠️ Model could not process this dataset. Please check column formats.")
                st.stop()

            results_df = pd.DataFrame({
                "TX_AMOUNT": input_df.get("TX_AMOUNT", np.nan),
                "TX_HOUR": input_df.get("TX_HOUR", np.nan),
                "TX_WEEKDAY": input_df.get("TX_WEEKDAY", np.nan),
                "fraud_probability": proba,
                "prediction": preds,
                "prediction_label": np.where(preds == 1, "Fraud", "Not Fraud")
            })

            st.toast("✅ Predictions complete!", icon="🎉")
            st.subheader("📋 Results Preview")
            st.dataframe(results_df.head(50), use_container_width=True)

            mode = st.radio("Choose Analysis Mode", ["Basic Mode", "Detailed Mode"])

            # --- Basic Mode ---
            if mode == "Basic Mode":
                csv_output = io.StringIO()
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                results_df.to_csv(csv_output, index=False)
                st.download_button("💾 Download Results (CSV)",
                                   csv_output.getvalue(),
                                   f"fraud_batch_result_{timestamp}.csv",
                                   "text/csv")

            # --- Detailed Mode ---
            else:
                st.subheader("📊 Fraud Insights")

                # --- KPI Metrics ---
                fraud_df = results_df[results_df["prediction_label"] == "Fraud"]
                fraud_pct = len(fraud_df) / len(results_df) * 100 if len(results_df) else 0
                avg_fraud_amt = fraud_df["TX_AMOUNT"].mean() if not fraud_df.empty else 0
                common_hour = int(fraud_df["TX_HOUR"].mode()[0]) if not fraud_df.empty else "-"
                common_day = int(fraud_df["TX_WEEKDAY"].mode()[0]) if not fraud_df.empty else "-"

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("% Fraudulent", f"{fraud_pct:.1f}%")
                col2.metric("Avg Fraud Amount", f"${avg_fraud_amt:,.2f}")
                col3.metric("Most Common Hour", common_hour, help="Hour of day with most frauds")
                col4.metric("Most Common Day", common_day, help="0=Mon, 6=Sun")

                with st.expander("🚨 Top Suspicious Transactions"):
                    top_frauds = results_df.sort_values("fraud_probability", ascending=False).head(5)
                    st.dataframe(top_frauds, use_container_width=True)

                    top_csv = io.StringIO()
                    top_frauds.to_csv(top_csv, index=False)
                    st.download_button("⬇️ Download Suspicious Transactions (CSV)",
                                       top_csv.getvalue(),
                                       "top_suspicious_transactions.csv",
                                       "text/csv")

                # *--- Charts ---
                with st.expander("📉 Fraud vs Non-Fraud Count"):
                    counts = results_df["prediction_label"].value_counts()
                    fig, ax = plt.subplots(figsize=(4, 3))
                    ax.bar(counts.index, counts.values, color=["red", "green"])
                    ax.set_ylabel("Count")
                    ax.set_title("Fraud vs Non-Fraud")
                    st.pyplot(fig)

                with st.expander("📊 Fraud Probability Distribution"):
                    fig2, ax2 = plt.subplots(figsize=(4, 3))
                    ax2.hist(results_df["fraud_probability"], bins=20, color="blue", alpha=0.7)
                    ax2.set_xlabel("Fraud Probability")
                    ax2.set_ylabel("Frequency")
                    st.pyplot(fig2)

                # --- Transaction Timeline ---
                with st.expander("⏳ Transactions Over Time"):
                    if "TX_DATETIME" not in results_df.columns and "TX_TIME_DAYS" in input_df.columns:
                        base_date = pd.Timestamp("2020-01-01")
                        results_df["TX_DATETIME"] = (
                            base_date
                            + pd.to_timedelta(input_df["TX_TIME_DAYS"], unit="D")
                            + pd.to_timedelta(input_df["TX_TIME_SECONDS"], unit="s")
                        )
                    if "TX_DATETIME" in results_df.columns:
                        fig, ax = plt.subplots(figsize=(6, 3))
                        ax.scatter(results_df["TX_DATETIME"], results_df["TX_AMOUNT"],
                                c=(results_df["prediction_label"] == "Fraud"),
                                cmap="coolwarm", alpha=0.6)
                        ax.set_title("Transactions Timeline (Fraud vs Non-Fraud)")
                        ax.set_ylabel("TX_AMOUNT")
                        ax.set_xlabel("TX_DATETIME")
                        st.pyplot(fig)

                # --- Fraud Amount Distribution ---
                with st.expander("💵 Fraud Amount Distribution"):
                    fig, ax = plt.subplots(figsize=(5, 3))
                    fraud_df = results_df[results_df["prediction_label"] == "Fraud"]
                    nonfraud_df = results_df[results_df["prediction_label"] == "Not Fraud"]
                    ax.hist([fraud_df["TX_AMOUNT"], nonfraud_df["TX_AMOUNT"]],
                            bins=30, stacked=True, label=["Fraud", "Not Fraud"], alpha=0.7)
                    ax.legend()
                    ax.set_title("Fraud vs Non-Fraud Amount Distribution")
                    st.pyplot(fig)

                # --- Top Customers by Fraud Count ---
                if "CUSTOMER_ID" in input_df.columns:
                    with st.expander("👥 Top Fraudulent Customers"):
                        top_customers = (
                            results_df[results_df["prediction_label"] == "Fraud"]
                            .groupby("CUSTOMER_ID")
                            .size().nlargest(10)
                        )
                        st.bar_chart(top_customers)

                # --- TX_AMOUNT Range Analysis ---
                with st.expander("📊 Fraud Count by Amount Ranges"):
                    max_amount = results_df["TX_AMOUNT"].max()
                    bins = [0, 100, 500, 1000, 5000, 10000]
                    bins.append(max_amount + 1)
                    bins = sorted(set(bins))

                    labels = ["<100", "100-500", "500-1000", "1000-5000", "5000-10000", "10k+"]

                    if len(labels) > len(bins) - 1:
                        labels = labels[:len(bins) - 1]
                    elif len(labels) < len(bins) - 1:
                        labels += [f"{bins[i]}-{bins[i+1]}" for i in range(len(labels), len(bins) - 1)]

                    results_df["AmountRange"] = pd.cut(
                        results_df["TX_AMOUNT"],
                        bins=bins,
                        labels=labels,
                        include_lowest=True
                    )

                    fraud_by_range = (
                        results_df.groupby(["AmountRange", "prediction_label"])
                        .size()
                        .unstack(fill_value=0)
                    )
                    st.bar_chart(fraud_by_range)

                # --- Correlation Heatmap ---
                with st.expander("🔗 Feature Correlation Heatmap"):
                    numeric_cols = results_df.select_dtypes(include=["int64", "float64"]).columns
                    if len(numeric_cols) > 1:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        corr = results_df[numeric_cols].corr()
                        cax = ax.matshow(corr, cmap="coolwarm")
                        plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=90)
                        plt.yticks(range(len(numeric_cols)), numeric_cols)
                        fig.colorbar(cax)
                        st.pyplot(fig)
                
                # --- Downloads ---
                st.subheader("⬇️ Export Results")
                csv_output = io.StringIO()
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                results_df.to_csv(csv_output, index=False)
                st.download_button("💾 Download CSV", csv_output.getvalue(),
                                   f"fraud_batch_result_{timestamp}.csv", "text/csv")

                pdf_output = generate_pdf_with_charts(results_df)
                st.download_button("📄 Download PDF", pdf_output,
                                   f"fraud_batch_predictions_{timestamp}.pdf", "application/pdf")

        except Exception as e:
            st.error("⚠️ Something went wrong while processing your file. Please check formatting.")
            st.exception(e)