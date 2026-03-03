import numpy as np
import pandas as pd

def calculate_merger_model(
    offer_price_billion,
    pct_cash,
    pct_stock,
    cof_share_price,
    brex_revenue_bn,
    brex_growth,
    synergies_deposit_bn,
    transaction_fees_million=50
):
    """
    Calculates the detailed merger model.
    """
    # --- 1. Deal Structure ---
    equity_value = offer_price_billion * 1000 # to millions
    cash_consideration = equity_value * pct_cash
    stock_consideration = equity_value * pct_stock
    
    # Shares Issued
    new_shares_issued = stock_consideration / cof_share_price # millions of shares
    
    # Fees
    total_uses = equity_value + transaction_fees_million
    
    # Sources
    sources_cash = cash_consideration + transaction_fees_million
    sources_equity = stock_consideration
    
    # --- 2. PPA (Purchase Price Allocation) ---
    # Assume Brex Book Value is small (tech startup), say $200M
    brex_book_value = 200 
    write_up_intangibles = 500 # Assume some tech IP
    deferred_tax_liability = write_up_intangibles * 0.21 # Tax shield impact
    
    adjusted_net_assets = brex_book_value + write_up_intangibles - deferred_tax_liability
    goodwill = equity_value - adjusted_net_assets
    
    # --- 3. Financial Forecasts (2026) ---
    # COF Assumptions (Standalone)
    cof_net_income = 5500 # Estimate: $5.5B Net Income
    cof_shares_outstanding = 380 # Estimate
    cof_eps_standalone = cof_net_income / cof_shares_outstanding
    
    # Brex Assumptions (Standalone)
    # Revenue growing at entered rate
    brex_rev_2026 = brex_revenue_bn * 1000 * (1 + brex_growth)
    # Assume Net Margin 0% (Breakeven) -> improving to 10% with scale? 
    # Let's assume standalone they are losing $50M
    brex_net_income = -50 
    
    # --- 4. Pro Forma Adjustments ---
    # A. Synergies
    # Revenue Synergies: $13B deposits * 4% Net Interest Margin (NIM)
    nim_spread = 0.04
    deposit_synergy_pretax = (synergies_deposit_bn * 1000) * nim_spread
    
    # Cost Synergies: Assume 20% of Brex OpEx (Revenue - Income)
    # Brex OpEx ~ Revenue + 50M loss = 1400 + 50 = 1450
    # Let's be conservative: $100M cost synergies
    cost_synergies_pretax = 100
    
    total_synergies_pretax = deposit_synergy_pretax + cost_synergies_pretax
    
    # B. Foregone Interest on Cash
    # 4% yield on cash used
    foregone_interest = sources_cash * 0.04
    
    # C. New Intangible Amortization
    amortization = write_up_intangibles / 10 # 10 year useful life
    
    # D. Tax Effect
    tax_rate = 0.21
    pretax_adjustments = total_synergies_pretax - foregone_interest - amortization
    after_tax_adjustments = pretax_adjustments * (1 - tax_rate)
    
    # --- 5. Pro Forma EPS ---
    pro_forma_net_income = cof_net_income + brex_net_income + after_tax_adjustments
    pro_forma_shares = cof_shares_outstanding + new_shares_issued
    
    pro_forma_eps = pro_forma_net_income / pro_forma_shares
    
    # Accretion / Dilution
    accretion_dollar = pro_forma_eps - cof_eps_standalone
    accretion_pct = accretion_dollar / cof_eps_standalone
    
    return {
        "sources": {"Cash": sources_cash, "Equity": sources_equity, "Total": sources_cash + sources_equity},
        "uses": {"Purchase Price": equity_value, "Fees": transaction_fees_million, "Total": total_uses},
        "goodwill": goodwill,
        "shares_issued": new_shares_issued,
        "standalone_eps": cof_eps_standalone,
        "pro_forma_eps": pro_forma_eps,
        "accretion_pct": accretion_pct,
        "synergies_after_tax": total_synergies_pretax * (1 - tax_rate)
    }

def calculate_sensitivity_matrix(base_cof_price, base_growth, offer_price, cash_pct):
    """
    Generates Accretion/Dilution matrix.
    Rows: COF Price ($210 - $260)
    Cols: Brex Growth (30% - 50%)
    """
    prices = np.linspace(210, 260, 5)
    growths = np.linspace(0.30, 0.50, 5)
    
    matrix = []
    
    for p in prices:
        row = []
        for g in growths:
            # Recalculate model
            res = calculate_merger_model(
                offer_price_billion=offer_price,
                pct_cash=cash_pct,
                pct_stock=(1-cash_pct),
                cof_share_price=p,
                brex_revenue_bn=1.0,
                brex_growth=g,
                synergies_deposit_bn=13
            )
            row.append(res['accretion_pct'])
        matrix.append(row)
        
    return {
        "prices": prices,
        "growths": growths,
        "matrix": matrix
    }
