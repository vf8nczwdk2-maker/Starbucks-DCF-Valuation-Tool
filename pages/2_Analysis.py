import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os

# Ensure we can import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dcf_engine import run_dcf

st.title("Analysis and Heatmaps")

# Retrieve parameters from session state, with fallback to new defaults
rev_growth = st.session_state.get('revenue_growth', 5.8)
ebitda_margin = st.session_state.get('ebitda_margin', 18.0)
wacc = st.session_state.get('wacc_input', 7.0)
g_rate = st.session_state.get('term_growth', 2.2)

st.markdown(f"**Analyzing under current assumptions**: Rev Growth: `{rev_growth}%` | Margin: `{ebitda_margin}%` | WACC: `{wacc}%` | Term Growth: `{g_rate}%`")

with st.spinner("Generating sensitivity analysis..."):
    try:
        results = run_dcf(rev_growth, ebitda_margin, wacc, g_rate)
        intrinsic_val = results['intrinsic_value']
        current_price = results['current_price']
        
        # --- Football Field Chart ---
        st.subheader("Valuation Range (Football Field)")
        
        all_vals = [val for row in results['heatmap_data'] for val in row]
        implied_min = min(all_vals)
        implied_max = max(all_vals)
        
        fig_ff = go.Figure()
        
        # Base DCF Sensitivity Range
        fig_ff.add_trace(go.Bar(
            y=['DCF Sensitivity'],
            x=[implied_max - implied_min],
            base=[implied_min],
            orientation='h',
            name='DCF Range',
            marker=dict(color='#00FF00', line=dict(color='#00FF00', width=1))
        ))
        
        # Current Price Line
        fig_ff.add_vline(x=current_price, line_width=3, line_dash="dash", line_color="red", annotation_text=f"Current: ${current_price:.2f}", annotation_position="top right")
        
        # Base DCF Line
        fig_ff.add_vline(x=intrinsic_val, line_width=3, line_color="white", annotation_text=f"Base DCF: ${intrinsic_val:.2f}", annotation_position="bottom right")

        fig_ff.update_layout(
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='white'),
            xaxis_title="Share Price ($)",
            barmode='overlay',
            height=300,
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_ff, use_container_width=True)
        
        st.markdown("---")
        
        # --- 2D Sensitivity Heatmap ---
        st.subheader("Sensitivity Analysis: WACC vs. Terminal Growth Rate")
        
        # Prepare heatmap labels
        x_labels = [f"{g:.1f}%" for g in results['g_range']] # Terminal Growth
        y_labels = [f"{w:.1f}%" for w in results['wacc_range']] # WACC
        
        fig_heat = go.Figure(data=go.Heatmap(
            z=results['heatmap_data'],
            x=x_labels,
            y=y_labels,
            colorscale='RdYlGn',
            text=[[f"${v:.2f}" for v in row] for row in results['heatmap_data']],
            texttemplate="%{text}",
            showscale=True
        ))
        
        fig_heat.update_layout(
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='white'),
            xaxis_title="Terminal Growth Rate (g)",
            yaxis_title="WACC",
            height=500
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    except Exception as e:
        st.error(f"Error generating analysis: {e}")
