import streamlit as st
import dcf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Educational DCF", layout="wide")

st.title("🎓 Educational DCF Model")
st.markdown("### Learn valuation by doing it.")

# --- Sidebar: Inputs ---
st.sidebar.header("1. Choose Asset")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL", help="Enter the stock ticker symbol (e.g., AAPL, TSLA).").upper()

if st.sidebar.button("Fetch Data"):
    with st.spinner("Fetching financial data..."):
        data = dcf.get_financial_data(ticker)
        if data:
            st.session_state['data'] = data
        else:
            st.error("Could not fetch data. Please try another ticker.")

data = st.session_state.get('data', None)

if data:
    st.sidebar.success(f"Loaded: {data['name']}")
    
    st.sidebar.header("2. Assumptions")
    
    # Stress Test Toggle
    stress_test = st.sidebar.checkbox("🔥 Stress Test Mode", help="Simulate a recession: Growth drops, WACC spikes.")
    
    # Defaults
    fcf = data.get('fcf', 1000000000)
    current_price = data.get('price', 100)
    shares = data.get('shares', 1000000)
    year_high = data.get('year_high', current_price * 1.2)
    year_low = data.get('year_low', current_price * 0.8)
    
    # Determine default values based on mode
    def_growth = -0.05 if stress_test else 0.10
    def_wacc = 0.12 if stress_test else 0.10
    
    if stress_test:
        st.sidebar.warning("⚠️ RECESSION SCENARIO ACTIVE")
    
    # Inputs with Educational Tooltips
    fcf_input = st.sidebar.number_input(
        "Free Cash Flow (Last Year)", 
        value=float(fcf),
        help="The cash a company generates after accounting for cash outflows to support operations and maintain its capital assets."
    )
    
    growth_rate = st.sidebar.slider(
        "Growth Rate (Next 5 Years)", 
        -0.20, 0.50, def_growth, 0.01,
        help="How fast do you expect the company's cash flow to grow each year for the next 5 years?"
    )
    
    terminal_growth = st.sidebar.slider(
        "Terminal Growth Rate", 
        0.0, 0.10, 0.03, 0.01,
        help="The stable rate at which the company will grow forever after year 5. Usually close to inflation (2-3%)."
    )
    
    discount_rate = st.sidebar.slider(
        "Discount Rate (WACC)", 
        0.05, 0.20, def_wacc, 0.01,
        help="The return required by investors. A higher risk means a higher discount rate, which lowers the value today."
    )
    
    # Calculate Base Case
    results = dcf.calculate_dcf(fcf_input, growth_rate, discount_rate, terminal_growth)
    
    if results.get('error'):
        st.error(results['error'])
    else:
        intrinsic_value = results['total_value']
        value_per_share = intrinsic_value / shares
        
        # --- Recommendation Engine ---
        upside_pct = (value_per_share - current_price) / current_price 
        
        if upside_pct > 0.30:
            rec_color = "green"
            rec_text = "STRONG BUY"
            rec_msg = "Significant value! The stock is trading at a deep discount."
        elif upside_pct > 0.10:
            rec_color = "green"
            rec_text = "BUY"
            rec_msg = "The stock appears undervalued with a decent margin of safety."
        elif upside_pct > -0.10:
            rec_color = "orange"
            rec_text = "HOLD / FAIR"
            rec_msg = "The price roughly matches the value. No clear edge here."
        else:
            rec_color = "red"
            rec_text = "SELL / OVERVALUED"
            rec_msg = "The price is significantly higher than the calculated value."

        # --- Main Area: Tabs ---
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Valuation Dashboard", "🧪 Scenario Playground", "🎲 Monte Carlo", "🧠 How it Works"])
        
        with tab1:
            # Recommendation Card
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 0.5rem; background-color: rgba(0,0,0,0.05); border: 1px solid #ddd; margin-bottom: 2rem;">
                <h3 style="margin: 0; color: {rec_color};">{rec_text}</h3>
                <p style="margin: 0;">Verdict: <b>{rec_msg}</b></p>
                {"<p style='color: red; font-weight: bold; margin-top: 5px;'>⚠️ STRESS TEST ACTIVE: Recession Assumptions</p>" if stress_test else ""}
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Price", f"${current_price:,.2f}")
            
            with col2:
                delta = value_per_share - current_price
                st.metric("Intrinsic Value", f"${value_per_share:,.2f}", delta=f"{delta:,.2f}")
                
            with col3:
                st.metric("Potential Upside", f"{upside_pct:.1%}", delta_color="normal")
                
            st.divider()
            
            # --- Plotly Visualization ---
            st.subheader("Visualizing Value vs Price")
            
            # Calculate Per Share PV components for visualization
            factor = 1 / shares
            pv_fcf_per_share = [ (x / ((1+discount_rate)**(i+1))) * factor for i, x in enumerate(results['projected_fcf']) ]
            pv_tv_per_share = results['pv_tv'] * factor
            
            x_axis = [f"Y{i}" for i in range(1, 6)] + ["Terminal"]
            y_axis = pv_fcf_per_share + [pv_tv_per_share]
            
            # Cumulative Sum
            cumulative = [sum(y_axis[:i+1]) for i in range(len(y_axis))]
            
            fig = go.Figure()
            
            # Bar Chart: Value Components
            fig.add_trace(go.Bar(
                x=x_axis, y=y_axis,
                name="Value Contribution",
                marker_color='blue'
            ))
            
            # Line Chart: Cumulative Value
            fig.add_trace(go.Scatter(
                x=x_axis, y=cumulative,
                name="Cumulative Value",
                mode='lines+markers',
                line=dict(color='green', width=3)
            ))
            
            # Horizontal Line: Stock Price
            fig.add_hline(y=current_price, line_dash="dash", line_color="red", annotation_text=f"Price: ${current_price:.2f}")
            
            fig.update_layout(
                title="Cumulative Value Accumulation",
                yaxis_title="Value Per Share ($)",
                legend=dict(x=0, y=1.1, orientation="h"),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with tab4:
            st.header("Step-by-Step Explanation")
            
            st.write("""
            **Valuation is the art of determining what a future stream of cash is worth today.** 
            Here is how we calculated the value of **{}**:
            """.format(ticker))
            
            # ... (Existing explanation code) ...
            st.subheader("1. Projecting the Future")
            st.write(f"We assumed the company starts with **\${fcf_input:,.0f}** in Free Cash Flow and grows at **{growth_rate:.1%}** per year.")
            
            st.table(pd.DataFrame({
                "Year": [1, 2, 3, 4, 5],
                "Projected FCF": [f"${x:,.0f}" for x in results['projected_fcf']]
            }))
            
            st.subheader("2. Discounting to Present")
            st.write(f"""
            Money in the future is worth less than money today. We 'discount' those future cash flows back to today using your **{discount_rate:.1%}** Discount Rate.
            
            Total PV of 5-year Cash Flows: **\${results['pv_fcf']:,.0f}**
            """)
            
            st.subheader("3. The Terminal Value")
            st.write(f"""
            After 5 years, we assume the company grows forever at the Terminal Growth Rate (**{terminal_growth:.1%}**).
            Using the Gordon Growth Model, this 'forever' value is:
            
            $$ \\text{{Terminal Value}} = \\frac{{\\text{{Final FCF}} \\times (1 + g)}}{{r - g}} $$
            
            Terminal Value in Year 5: **\${results['terminal_value']:,.0f}**
            
            Discounted back to today (PV of TV): **\${results['pv_tv']:,.0f}**
            """)
            
            st.subheader("4. The Final Sum")
            st.latex(r"""
            \text{Intrinsic Value} = \text{PV of FCFs} + \text{PV of Terminal Value}
            """)
            
            st.write(f"""
            **\${results['pv_fcf']:,.0f}** + **\${results['pv_tv']:,.0f}** = **\${intrinsic_value:,.0f}**
            
            Dividing by **{shares:,.0f}** shares gives us **\${value_per_share:,.2f}** per share.
            """)
            
        with tab2:
            st.header("Scenario Playground")
            
            # --- Sensitivity Matrix ---
            st.subheader("Sensitivity Matrix: Price at different rates")
            
            grid = dcf.calculate_sensitivity_grid(fcf_input, growth_rate, discount_rate, terminal_growth, shares)
            
            # Prepare data for Heatmap
            z_values = grid['matrix']
            x_values = [f"{x:.1%}" for x in grid['growth_rates']] # Growth
            y_values = [f"{x:.1%}" for x in grid['discount_rates']] # WACC
            
            fig_heat = go.Figure(data=go.Heatmap(
                z=z_values,
                x=x_values,
                y=y_values,
                colorscale='RdBu',
                texttemplate="$%{z:.0f}",
                hoverongaps=False 
            ))
            
            fig_heat.update_layout(
                title="Intrinsic Value Sensitivity (Growth vs WACC)",
                xaxis_title="Growth Rate",
                yaxis_title="Discount Rate (WACC)",
                height=500
            )
            
            st.plotly_chart(fig_heat, use_container_width=True)
            
            # --- Football Field Chart ---
            st.subheader("Valuation Range vs Market")
            
            # Get Min/Max from Sensitivity
            flat_matrix = [item for sublist in grid['matrix'] for item in sublist]
            dcf_min = min(flat_matrix)
            dcf_max = max(flat_matrix)
            
            fig_foot = go.Figure()
            
            # 52-Week Range
            fig_foot.add_trace(go.Bar(
                y=["52-Week Range"],
                x=[year_high - year_low],
                base=[year_low],
                orientation='h',
                name="52-Week Range",
                marker_color='gray',
                opacity=0.6,
                text=f"${year_low:.2f} - ${year_high:.2f}",
                textposition='auto'
            ))
            
            # DCF Range
            fig_foot.add_trace(go.Bar(
                y=["DCF Range"],
                x=[dcf_max - dcf_min],
                base=[dcf_min],
                orientation='h',
                name="DCF Sensitivity Range",
                marker_color='blue',
                opacity=0.8,
                text=f"${dcf_min:.2f} - ${dcf_max:.2f}",
                textposition='auto'
            ))
            
            # Current Price Line
            fig_foot.add_vline(x=current_price, line_width=3, line_dash="dash", line_color="red", annotation_text="Current Price")
            
            fig_foot.update_layout(
                title="Football Field: Valuation vs Market Reality",
                xaxis_title="Share Price ($)",
                barmode='overlay',
                height=400
            )
            
            st.plotly_chart(fig_foot, use_container_width=True)
            
        with tab3:
            st.header("Monte Carlo Simulation")
            st.write("We've run 1,000 simulations varying Growth Rate (+/- 1.5%) and WACC (+/- 1%).")
            
            if st.button("Run Simulation", type="primary"):
                # Run sim
                raw_values = dcf.run_monte_carlo(fcf_input, growth_rate, 0.015, discount_rate, 0.01, terminal_growth)
                sim_prices = [v / shares for v in raw_values]
                
                # Stats
                p5 = np.percentile(sim_prices, 5)
                p50 = np.percentile(sim_prices, 50)
                p95 = np.percentile(sim_prices, 95)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Worst Case (5%)", f"${p5:,.2f}")
                c2.metric("Base Case (Median)", f"${p50:,.2f}")
                c3.metric("Best Case (95%)", f"${p95:,.2f}")
                
                # Histogram
                fig_hist = go.Figure()
                fig_hist.add_trace(go.Histogram(x=sim_prices, nbinsx=30, marker_color='purple'))
                
                fig_hist.add_vline(x=current_price, line_color='red', line_dash='dash', annotation_text="Current Price")
                
                fig_hist.update_layout(
                    title="Probability Distribution of Fair Value",
                    xaxis_title="Fair Value ($)",
                    yaxis_title="Frequency",
                    bargap=0.1
                )
                
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("Click 'Run Simulation' to execute the Monte Carlo analysis.")
    
else:
    st.info("Enter a ticker in the sidebar and click 'Fetch Data' to start.")
