import yfinance as yf
import pandas as pd
import numpy as np

def fetch_sbux_data():
    """Fetches 5 years of historical financial data for SBUX."""
    ticker = yf.Ticker("SBUX")
    
    # Get financial statements
    income_stmt = ticker.financials.fillna(0)
    balance_sheet = ticker.balance_sheet.fillna(0)
    cash_flow = ticker.cashflow.fillna(0)
    
    # We want 5 years if available
    years_to_keep = income_stmt.columns[:5]
    
    income_stmt = income_stmt[years_to_keep]
    balance_sheet = balance_sheet[years_to_keep]
    cash_flow = cash_flow[years_to_keep]

    return income_stmt, balance_sheet, cash_flow

def extract_net_debt(balance_sheet):
    """
    Calculates Net Debt including Operating Lease Liabilities.
    Net Debt = Total Debt + Operating Lease Liabilities - Cash and Cash Equivalents
    """
    
    # 1. Total Debt
    # Explicitly avoid 'Total Liabilities'
    total_debt = 0
    if 'Total Debt' in balance_sheet.index:
        total_debt = balance_sheet.loc['Total Debt']
    elif 'Long Term Debt' in balance_sheet.index:
        total_debt = balance_sheet.loc['Long Term Debt']
        if 'Current Debt' in balance_sheet.index:
            total_debt += balance_sheet.loc['Current Debt']
            
    # 2. Operating Lease Liabilities
    lease_liabilities = 0
    if 'Operating Lease Liabilities' in balance_sheet.index:
         lease_liabilities = balance_sheet.loc['Operating Lease Liabilities']
    elif 'Long Term Debt And Capital Lease Obligation' in balance_sheet.index:
         if 'Long Term Debt' in balance_sheet.index:
             lease_liabilities = balance_sheet.loc['Long Term Debt And Capital Lease Obligation'] - balance_sheet.loc['Long Term Debt']
            
    # 3. Cash and Cash Equivalents
    cash = 0
    if 'Cash And Cash Equivalents' in balance_sheet.index:
        cash = balance_sheet.loc['Cash And Cash Equivalents']
    elif 'Cash' in balance_sheet.index:
        cash = balance_sheet.loc['Cash']
        
    net_debt = total_debt + lease_liabilities - cash
    return net_debt, lease_liabilities

def run_dcf(revenue_growth_rate, target_ebitda_margin, wacc, terminal_growth_rate):
    """
    DCF engine using current financials as a baseline.
    Parameters are percentages (e.g., 5.8 for 5.8%).
    """
    # Enforce constraints as requested
    if wacc > 15.0:
        wacc = 15.0
    if terminal_growth_rate > 3.0:
        terminal_growth_rate = 3.0
        
    ticker = yf.Ticker("SBUX")
    info = ticker.info
    # Use specified shares outstanding: 1.14 Billion
    shares_outstanding = 1.14e9 
    current_price = info.get('currentPrice', info.get('regularMarketPrice', 95.0))
    # Market Cap (Equity Value for WACC)
    market_cap = info.get('marketCap', shares_outstanding * current_price)
    
    income_stmt, balance_sheet, cash_flow = fetch_sbux_data()
    
    # Baseline Metrics (Most recent year)
    recent_col = income_stmt.columns[0]
    
    # Use Q1 2026 Revenue of $9.9B as the base (annualized)
    base_revenue = 9.9e9 * 4
        
    # Get Net Debt
    recent_bs_col = balance_sheet.columns[0]
    
    # Define extract_net_debt logic explicitly here to avoid Yahoo's 'Total Debt' double counting leases
    # 1. Total Debt = Long Term Debt + Current Debt 
    total_debt = 0
    if 'Long Term Debt' in balance_sheet.index:
        total_debt += balance_sheet.loc['Long Term Debt', recent_bs_col]
    if 'Current Debt' in balance_sheet.index:
        total_debt += balance_sheet.loc['Current Debt', recent_bs_col]
        
    # 2. Operating Lease Liabilities
    lease_liab_val = 0
    if 'Operating Lease Liabilities' in balance_sheet.index:
         lease_liab_val = balance_sheet.loc['Operating Lease Liabilities', recent_bs_col]
    elif 'Long Term Debt And Capital Lease Obligation' in balance_sheet.index:
         if 'Long Term Debt' in balance_sheet.index:
             lease_liab_val = balance_sheet.loc['Long Term Debt And Capital Lease Obligation', recent_bs_col] - balance_sheet.loc['Long Term Debt', recent_bs_col]
             
    # 3. Cash
    cash = 0
    if 'Cash And Cash Equivalents' in balance_sheet.index:
        cash = balance_sheet.loc['Cash And Cash Equivalents', recent_bs_col]
    elif 'Cash' in balance_sheet.index:
        cash = balance_sheet.loc['Cash', recent_bs_col]
        
    current_net_debt = total_debt + lease_liab_val - cash
    
    # 5 Year Projection
    # Revenue projection
    proj_revenues = []
    current_rev = base_revenue
    for _ in range(5):
        current_rev *= (1 + (revenue_growth_rate / 100))
        proj_revenues.append(current_rev)
        
    # Operating Income Projection (using the input as Operating Margin)
    proj_op_inc = [r * (target_ebitda_margin / 100) for r in proj_revenues]
    
    # FCF Projection = NOPAT = Operating Income * (1 - tax_rate)
    tax_rate = 0.21
    proj_fcf = [op * (1 - tax_rate) for op in proj_op_inc]
    
    # Present Value of FCFs
    pv_fcfs = []
    for i, fcf in enumerate(proj_fcf):
        discount_factor = (1 + (wacc / 100)) ** (i + 1)
        pv_fcfs.append(fcf / discount_factor)
        
    sum_pv_fcf = sum(pv_fcfs)
    
    # Terminal Value using Gordon Growth Method
    terminal_fcf = proj_fcf[-1] * (1 + (terminal_growth_rate / 100))
    terminal_value = terminal_fcf / ((wacc / 100) - (terminal_growth_rate / 100))
    pv_terminal_value = terminal_value / ((1 + (wacc / 100)) ** 5)
    
    # Enterprise Value
    enterprise_value = sum_pv_fcf + pv_terminal_value
    
    # Equity Value = EV - Net Debt
    equity_value = enterprise_value - current_net_debt
    
    # Intrinsic Value per Share
    intrinsic_value = equity_value / shares_outstanding
    
    # Heatmap Generation
    w_base = wacc / 100.0
    g_base = terminal_growth_rate / 100.0
    wacc_range = np.linspace(max(0.01, w_base - 0.02), w_base + 0.02, 5) 
    g_range = np.linspace(max(0.005, g_base - 0.01), g_base + 0.01, 5)
    
    heatmap_matrix = []
    for w in wacc_range:
        row = []
        for g in g_range:
            tv_temp = (proj_fcf[-1] * (1 + g)) / (w - g)
            pv_tv_temp = tv_temp / ((1 + w) ** 5)
            ev_temp = sum_pv_fcf + pv_tv_temp
            eq_temp = ev_temp - current_net_debt
            val_temp = eq_temp / shares_outstanding
            row.append(val_temp)
        heatmap_matrix.append(row)
        
    return {
         'intrinsic_value': intrinsic_value,
         'current_price': current_price,
         'enterprise_value': enterprise_value,
         'equity_value': equity_value,
         'net_debt': current_net_debt,
         'lease_liabilities_extracted': lease_liab_val,
         'heatmap_data': heatmap_matrix,
         'wacc_range': [w*100 for w in wacc_range],
         'g_range': [g*100 for g in g_range],
         'proj_revenues': proj_revenues,
         'proj_ebitda': proj_op_inc,
         'proj_fcf': proj_fcf,
         'sum_pv_fcf': sum_pv_fcf,
         'pv_terminal_value': pv_terminal_value,
         'base_revenue': base_revenue,
         'shares_outstanding': shares_outstanding,
         'market_cap': market_cap
    }

if __name__ == "__main__":
    result = run_dcf(5.8, 15.0, 8.5, 2.2)
    print(f"Intrinsic Value: ${result['intrinsic_value']:.2f}")
    print(f"Current Price: ${result['current_price']:.2f}")
    print(f"Extracted Leases: ${result['lease_liabilities_extracted']:,.0f}")
