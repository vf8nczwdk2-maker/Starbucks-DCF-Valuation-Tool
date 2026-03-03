import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="SBUX DCF Valuation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Optional: Add custom CSS for the "Bloomberg Terminal" aesthetic
def set_dark_theme():
    st.markdown("""
        <style>
        .reportview-container {
            background: #000000;
        }
        .main {
            background-color: #000000;
            color: #FFFFFF;
        }
        .sidebar .sidebar-content {
            background-color: #1E1E1E;
        }
        h1, h2, h3, h4, h5, h6, p, div {
            color: #FFFFFF;
        }
        .css-1d391kg {
             background-color: #1E1E1E;
        }
        /* Custom Metric Card Style */
        .metric-card {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #333;
            margin-bottom: 20px;
        }
        .metric-card h3 {
            margin-bottom: 0px;
            color: #888;
            font-size: 1.2rem;
        }
        .metric-card h2 {
            margin-top: 10px;
            color: #FFF;
            font-size: 2.5rem;
        }
        .metric-card p {
            color: #00FF00;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# Call the theme function
set_dark_theme()

st.sidebar.title("SBUX DCF Model")
st.sidebar.markdown("Adjust Assumptions:")

revenue_growth = st.sidebar.slider("Revenue Growth (Yr 1-5) %", min_value=3.0, max_value=12.0, value=5.8, step=0.1)
ebitda_margin = st.sidebar.slider("Target EBITDA Margin %", min_value=10.0, max_value=25.0, value=18.0, step=0.5)
wacc_input = st.sidebar.slider("WACC (Discount Rate) %", min_value=5.0, max_value=12.0, value=7.0, step=0.1)
term_growth = st.sidebar.slider("Terminal Growth Rate (g) %", min_value=1.0, max_value=3.0, value=2.2, step=0.1)

st.session_state['revenue_growth'] = revenue_growth
st.session_state['ebitda_margin'] = ebitda_margin
st.session_state['wacc_input'] = wacc_input
st.session_state['term_growth'] = term_growth

st.sidebar.markdown("---")
st.sidebar.markdown("Select an Analysis Page")

st.title("SBUX DCF Valuation Model")
st.markdown("Dynamic DCF valuation framework modeling the Starbucks (SBUX) 2026 Turnaround Scenario.")
