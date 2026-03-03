import streamlit as st
import sys
import os

# Ensure we can import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.title("Methodology: The DRIVER Framework")
st.markdown("This project follows the **DRIVER Framework** for structured development and financial rigor.")

st.markdown("---")

st.header("1. Discover")
st.markdown("""
**Why Starbucks (SBUX)?**
Starbucks presents a fascinating valuation case study in 2026. With the turnaround narrative taking hold, the market is pricing in significant operational improvements and margin expansion. This model allows users to stress-test those assumptions.
""")

st.header("2. Represent")
st.markdown("""
This Discounted Cash Flow (DCF) model simplifies the projection phase while maintaining rigor in the Enterprise Value to Equity Value bridge.
- **Free Cash Flow (FCF)**: Calculated as Net Operating Profit After Taxes (NOPAT) assuming a target Operating Margin.
- **The Lease Liability Edge Case**: Accounting standards now require capitalizing operating leases. SBUX carries roughly $12B in Operating Lease Liabilities. This model explicitly extracts these obligations from the balance sheet (via `yfinance`) and includes them as Debt when calculating Net Debt, ensuring the Equity Value is not artificially inflated.
""")

st.header("3. Implement")
st.markdown("""
**Technical Stack**
- **Core Engine**: Python (Pandas, NumPy)
- **Data Acquisition**: `yfinance` (Real-time financial statement parsing)
- **User Interface**: Streamlit (Reactive state management)
- **Visualizations**: Plotly (Bloomberg-style dark theme, heatmaps, and football field charts)
""")

st.header("4. Validate")
st.markdown("""
The model is anchored to reality by comparing the implied intrinsic value directly against the live trading price (approx. $96 in early 2026). The base assumptions are tailored so that reasonable turnaround figures yield a value contiguous with the market, highlighting what the market is implicitly pricing in.
""")

st.header("5. Evolve")
st.markdown("""
Future iterations of this portfolio piece could include:
- Monte Carlo simulations for probabilistic valuation ranges rather than static sensitivities.
- Automated API fetching of consensus analyst estimates for Revenue and Margin.
- Dynamic parsing of the 10-K to extract Management Discussion and Analysis (MD&A) sentiment.
""")

st.header("6. Reflect")
st.markdown("""
The assumptions in this model are grounded in qualitative financial analysis rather than purely quantitative projections:
- **WACC Calibration (7.0%)**: SBUX benefits from a highly stable, membership-driven revenue base. In a normalized interest rate environment, its mature capital structure and lower risk premium justify a discount rate closer to 7.0%, rather than a generic 8.5% or higher.
- **Terminal Growth Rate (2.2%)**: Anchored strictly to long-term GDP and inflation expectations, capping the perpetual growth phase to remain scientifically grounded.
- **Margin Expansion (18.0%)**: We project an 18% target margin (up from recent lows) assuming management successfully executes on operational efficiencies, store-level automation, and menu optimization.

These specific calibrations ensure the model acts as a rigorous stress-test of the turnaround thesis rather than a mechanical extrapolation of past anomalies.
""")
