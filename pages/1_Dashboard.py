import streamlit as st
import sys
import os
import pandas as pd

# Ensure we can import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dcf_engine import run_dcf

st.title("Valuation Dashboard")

# Retrieve parameters from session state, with fallback to defaults
rev_growth = st.session_state.get('revenue_growth', 5.8)
ebitda_margin = st.session_state.get('ebitda_margin', 18.0)
wacc = st.session_state.get('wacc_input', 7.0)
g_rate = st.session_state.get('term_growth', 2.2)

with st.spinner("Calculating intrinsic value..."):
    try:
        results = run_dcf(rev_growth, ebitda_margin, wacc, g_rate)
        
        intrinsic_val = results['intrinsic_value']
        current_price = results['current_price']
        
        # --- Top Row: Big Metric Cards ---
        st.markdown("### Top Line Metrics")
        
        # Upside/Downside Calculation
        upside_pct = ((intrinsic_val / current_price) - 1) * 100
        upside_text = f"{upside_pct:.1f}% Upside" if upside_pct > 0 else f"{abs(upside_pct):.1f}% Downside"
        upside_color = "#00FF00" if upside_pct > 0 else "#FF0000"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Intrinsic Value</h3>
                <h2>${intrinsic_val:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-color: #555;">
                <h3 style="color: #AAA;">Current Price</h3>
                <h2 style="color: #DDD;">${current_price:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-color: {upside_color}55;">
                <h3 style="color: {upside_color};">Implied Return</h3>
                <h2 style="color: {upside_color};">{upside_text}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        # --- Middle Section: The Valuation Bridge ---
        st.markdown("### The Valuation Bridge")
        st.markdown("Expand each section to see the step-by-step mathematical translation from assumptions to share price.")
        
        # Step 1: WACC Breakdown
        with st.expander("Step 1: WACC Breakdown (Discount Rate)"):
            v_e = results.get('market_cap', 0)
            v_d = results.get('net_debt', 0)
            if v_e == 0 and v_d == 0:
                v_total = 1
            else:
                v_total = v_e + v_d
            
            weight_e = (v_e / v_total) * 100 if v_total > 0 else 0
            weight_d = (v_d / v_total) * 100 if v_total > 0 else 0
            
            st.markdown(f"""
            **Weighted Average Cost of Capital (WACC)** formula:
            
            $$ WACC = \\left(\\frac{{V_E}}{{V}}\\right) \\times R_e + \\left(\\frac{{V_D}}{{V}}\\right) \\times R_d \\times (1 - t) $$
            
            *Where:*
            - **$R_e$ (Cost of Equity):** $\\approx 7\\%$ (Based on SBUX's mature, stable membership-driven cash flows in March 2026).
            - **$R_d$ (Cost of Debt):** $\\approx 4.6\\%$ (SBUX corporate bond yields).
            - **$t$ (Tax Rate):** $21\\%$.
            - **$V_E$ (Equity Value):** \\${v_e/1e9:.2f}B ({weight_e:.1f}% weight)
            - **$V_D$ (Debt Value):** \\${v_d/1e9:.2f}B ({weight_d:.1f}% weight)
            
            *For this model, we are using a unified slider input of **{wacc}%**.*
            """)
            
        # Step 2: FCF Projection
        with st.expander("Step 2: Free Cash Flow (FCF) Projections"):
            st.markdown("Forecasted 5-Year Cash Flows based on Revenue Growth and Target Operating Margins (assuming 21% Tax Rate):")
            
            years = [f"Year {i}" for i in range(1, 6)]
            
            df_fcf = pd.DataFrame({
                "Metric ($ Billions)": ["Revenue", "Operating Income (EBITDA proxy)", "Unlevered Free Cash Flow (NOPAT)"],
                "Year 1": [f"${results['proj_revenues'][0]/1e9:.2f}", f"${results['proj_ebitda'][0]/1e9:.2f}", f"${results['proj_fcf'][0]/1e9:.2f}"],
                "Year 2": [f"${results['proj_revenues'][1]/1e9:.2f}", f"${results['proj_ebitda'][1]/1e9:.2f}", f"${results['proj_fcf'][1]/1e9:.2f}"],
                "Year 3": [f"${results['proj_revenues'][2]/1e9:.2f}", f"${results['proj_ebitda'][2]/1e9:.2f}", f"${results['proj_fcf'][2]/1e9:.2f}"],
                "Year 4": [f"${results['proj_revenues'][3]/1e9:.2f}", f"${results['proj_ebitda'][3]/1e9:.2f}", f"${results['proj_fcf'][3]/1e9:.2f}"],
                "Year 5": [f"${results['proj_revenues'][4]/1e9:.2f}", f"${results['proj_ebitda'][4]/1e9:.2f}", f"${results['proj_fcf'][4]/1e9:.2f}"]
            }).set_index("Metric ($ Billions)")
            
            st.dataframe(df_fcf)
            
        # Step 3: Terminal Value Bridge
        with st.expander("Step 3: Terminal Value (Gordon Growth Method)"):
            st.markdown(f"""
            The **Terminal Value (TV)** represents the value of all cash flows beyond Year 5, growing at a perpetual rate ($g$).
            
            $$ TV = \\frac{{FCF_n \\times (1 + g)}}{{WACC - g}} $$
            
            *Calculation:*
            - **Final Year FCF ($FCF_n$):** \\${results['proj_fcf'][-1]/1e9:.2f} Billion
            - **Terminal Growth Rate ($g$):** {g_rate}%
            - **WACC:** {wacc}%
            
            **Present Value of Terminal Value:** \\${results['pv_terminal_value']/1e9:.2f} Billion
            """)
            
        # Step 4: Enterprise Value to Equity
        with st.expander("Step 4: Enterprise Value to Equity Share Price"):
            
            st.markdown(f"""
            <div style="font-family: monospace; font-size: 1.1em; background-color: #111; padding: 20px; border-radius: 10px;">
                <p style="margin:5px 0;">(+) PV of Cash Flows <span style="float:right;">${results['sum_pv_fcf']/1e9:,.2f} B</span></p>
                <p style="margin:5px 0; border-bottom: 1px solid #444; padding-bottom: 5px;">(+) PV of Terminal Value <span style="float:right;">${results['pv_terminal_value']/1e9:,.2f} B</span></p>
                <p style="margin:10px 0; font-weight: bold; font-size: 1.2em; color: #FFF;">(=) Enterprise Value <span style="float:right;">${results['enterprise_value']/1e9:,.2f} B</span></p>
                <p style="margin:5px 0; border-bottom: 1px solid #444; padding-bottom: 5px; color: #FF4444;">(-) Net Debt (including verifed $12B in Leases) <span style="float:right;">-${results['net_debt']/1e9:,.2f} B</span></p>
                <p style="margin:10px 0; font-weight: bold; font-size: 1.2em; color: #00FF00;">(=) Equity Value <span style="float:right;">${results['equity_value']/1e9:,.2f} B</span></p>
                <p style="margin:5px 0; border-top: 1px solid #444; padding-top: 10px; color: #AAA;">(÷) Shares Outstanding <span style="float:right;">{results['shares_outstanding']/1e9:,.2f} B</span></p>
                <p style="margin:10px 0; font-weight: bold; font-size: 1.5em; color: #00FF00; border-top: 2px solid #00FF00; padding-top: 10px;">(=) Intrinsic Value Per Share <span style="float:right;">${intrinsic_val:,.2f}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
    except KeyError as ke:
        st.warning(f"Data Pending: Unable to fetch complete financial data for {ke}. Please wait a moment or check your connection.")
    except Exception as e:
        st.error(f"Error calculating DCF: {e}")
        st.info("Data Pending: Ensure yfinance is successfully fetching the necessary parameters.")
