import streamlit as st
import merger
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="COF/Brex Merger Model", layout="wide")

st.title("🏦 M&A Deal Room: Capital One acquires Brex")
st.markdown("### Strategic Integration of AI & B2B Payments")

# --- Sidebar: Deal Assumptions ---
st.sidebar.header("Deal Structure")
offer_price = st.sidebar.number_input("Offer Price ($B)", value=5.15)
pct_cash = st.sidebar.slider("% Cash Consideration", 0.0, 1.0, 0.50, 0.10)
pct_stock = 1.0 - pct_cash
st.sidebar.text(f"% Stock Consideration: {pct_stock:.0%}")

st.sidebar.divider()

st.sidebar.header("Market Assumptions")
cof_price = st.sidebar.number_input("COF Share Price ($)", value=235.0)
brex_growth = st.sidebar.slider("Brex Revenue Growth", 0.10, 0.80, 0.40, 0.05)
dep_synergy = st.sidebar.number_input("Deposit Synergies ($B)", value=13.0)

# --- Calculate Model ---
results = merger.calculate_merger_model(
    offer_price_billion=offer_price,
    pct_cash=pct_cash,
    pct_stock=pct_stock,
    cof_share_price=cof_price,
    brex_revenue_bn=1.0,
    brex_growth=brex_growth,
    synergies_deposit_bn=dep_synergy
)

# --- Output Dashboard ---

# 1. Executive Summary Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Acquisition Price", f"${offer_price}B")
col2.metric("New Shares Issued", f"{results['shares_issued']:.1f}M")
d_color = "normal" if results['accretion_pct'] >= 0 else "inverse"
col3.metric("Accretion / (Dilution)", f"{results['accretion_pct']:.1%}", delta_color=d_color)
col4.metric("Implied Goodwill", f"${results['goodwill']/1000:.2f}B")

st.divider()

# 2. Main Analysis Tabs
tab1, tab2, tab3 = st.tabs(["🏗️ Deal Structure & PPA", "📈 Sensitivity Analysis", "🧠 Strategic Rationale"])

with tab1:
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Sources & Uses")
        src_df = pd.DataFrame({
            "Source": ["Cash on Hand", "New Equity"],
            "Amount ($M)": [results['sources']['Cash'], results['sources']['Equity']]
        })
        use_df = pd.DataFrame({
            "Use": ["Purchase Equity", "Transaction Fees"],
            "Amount ($M)": [results['uses']['Purchase Price'], results['uses']['Fees']]
        })
        
        st.write("**Sources**")
        st.dataframe(src_df, hide_index=True, use_container_width=True)
        st.write("**Uses**")
        st.dataframe(use_df, hide_index=True, use_container_width=True)
        
    with col_r:
        st.subheader("Accretion Logic")
        st.write(f"""
        **Standalone COF EPS**: ${results['standalone_eps']:.2f}
        
        **Pro Forma Impact**:
        - Brex Net Income contribution (negative initially)
        - (+) Synergies (After-Tax): ${results['synergies_after_tax']:.0f}M
        - (-) Foregone Interest on Cash
        - (-) New Intangibles Amortization
        
        **= Pro Forma EPS**: ${results['pro_forma_eps']:.2f}
        """)
        
        if results['accretion_pct'] > 0:
            st.success(f"✅ The deal is **{results['accretion_pct']:.1%} Accretive** due to significant deposit synergies offsetting dilution.")
        else:
            st.error(f"⚠️ The deal is **{results['accretion_pct']:.1%} Dilutive**. Synergies do not yet cover the cost of equity issuance.")

with tab2:
    st.subheader("Sensitivity: Accretion/(Dilution) %")
    st.write("How does COF Share Price and Brex Growth affect the deal math?")
    
    sens = merger.calculate_sensitivity_matrix(cof_price, brex_growth, offer_price, pct_cash)
    
    z = sens['matrix']
    x = [f"{g:.0%}" for g in sens['growths']]
    y = [f"${p:.0f}" for p in sens['prices']]
    
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale='RdBu',
        texttemplate="%{z:.1%}",
        colorbar=dict(title="Accretion %"),
    ))
    
    fig.update_layout(
        xaxis_title="Brex Growth Rate",
        yaxis_title="COF Share Price",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("📝 Deal Memo: Strategic Rationale")
    
    st.markdown("### 1. Executive Summary")
    st.info("""
    **Capital One acquires Brex for $5.15 Billion** to create the world's leading **AI-Native B2B Payments Platform**. 
    By combining COF's fortress balance sheet with Brex's modern software stack, the combined entity will dominate corporate spend management.
    """)
    
    st.divider()
    
    st.markdown("### 2. The Win-Win Analysis")
    col_cof, col_brex = st.columns(2)
    
    with col_cof:
        st.subheader("🏦 For Capital One")
        st.markdown("""
        - **Deposit Synergy**: Instantly lowers cost of funds by moving **$13B** of Brex deposits to COF.
        - **Tech Leapfrog**: Acquires a cloud-native spend management stack, bypassing years of legacy IT upgrades.
        - **Data Advantage**: Brex's real-time transaction data + COF's credit models = **Superior AI Underwriting**.
        """)
        
    with col_brex:
        st.subheader("💳 For Brex")
        st.markdown("""
        - **Cost of Capital**: Access to COF's banking license allows for infinitely cheaper lending to startup clients.
        - **Distribution**: Immediate cross-sell access to COF's **millions of SMB & Commercial** clients.
        - **Survival & Scale**: Eliminates funding risk and provides a massive platform for long-term impact.
        """)
    
    st.divider()
    
    st.markdown("### 3. Long-Term Vision (2030)")
    st.write("""
    The goal is **not just cost savings**. The long-term play is to build the **'Operating System for Business'**:
    1.  **Autonomous Finance**: AI agents (powered by Brex tech) that automatically manage AP/AR, payroll, and cash flow for COF clients.
    2.  **Global Expansion**: Using Brex's multi-currency infrastructure to take Capital One commercial banking global.
    """)
