import plotly.graph_objects as go
import streamlit as st


def show_probability_gauge(fraud_prob: float, show_caption: bool = True):
    fraud_prob_percent = fraud_prob * 100

    # Define gauge bar color
    if fraud_prob < 0.3:
        gauge_color, risk_label = "green", "🟢 Low Risk"
    elif fraud_prob < 0.7:
        gauge_color, risk_label = "orange", "🟠 Medium Risk"
    else:
        gauge_color, risk_label = "red", "🔴 High Risk"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=fraud_prob_percent,
            number={'suffix': "%", 'font': {'size': 36, 'color': gauge_color, 'family': "Arial Black"}},
            title={'text': "Fraud Probability", 'font': {'size': 20, 'color': "#333"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "black"},
                'bar': {'color': gauge_color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#666",
                'steps': [
                    {'range': [0, 30], 'color': "#66ff66"},
                    {'range': [30, 70], 'color': "#ffd633"},
                    {'range': [70, 100], 'color': "#ff6666"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': fraud_prob_percent
                }
            }
        )
    )

    # --- Render gauge ---
    st.plotly_chart(fig, use_container_width=True)

    if show_caption:
        st.markdown(
            f"<div style='text-align:center; font-size:18px; font-weight:bold; color:{gauge_color};'>"
            f"{risk_label} ({fraud_prob_percent:.1f}%)</div>",
            unsafe_allow_html=True
        )