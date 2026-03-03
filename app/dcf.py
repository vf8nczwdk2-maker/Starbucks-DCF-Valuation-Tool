import numpy_financial as npf
import pandas as pd
import yfinance as yf
import numpy as np

def get_financial_data(ticker_symbol):
    """
    Fetches key financial data for a ticker using yfinance.
    Returns a dictionary or None if failed.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        
        # Try to get free cash flow from cashflow statement
        cashflow = stock.cashflow
        if cashflow is not None and not cashflow.empty:
            # Look for Free Cash Flow (Total Cash From Operating Activities - Capital Expenditures)
            # yfinance often has 'Free Cash Flow' row or we calculate it
            if 'Free Cash Flow' in cashflow.index:
                w_fcf = cashflow.loc['Free Cash Flow'].iloc[0] # Most recent
            else:
                 # Fallback calc
                 operating_cash = cashflow.loc['Total Cash From Operating Activities'].iloc[0] if 'Total Cash From Operating Activities' in cashflow.index else 0
                 capex = cashflow.loc['Capital Expenditures'].iloc[0] if 'Capital Expenditures' in cashflow.index else 0
                 w_fcf = operating_cash + capex # Capex is usually negative
        else:
            w_fcf = 1000000 # Dummy fallback
            
        shares = info.get('sharesOutstanding', 1000000)
        price = info.get('currentPrice', 0)
        currency = info.get('currency', 'USD')
        
        return {
            "fcf": w_fcf,
            "shares": shares,
            "price": price,
            "currency": currency,
            "name": info.get('longName', ticker_symbol),
            "year_high": info.get('fiftyTwoWeekHigh', price),
            "year_low": info.get('fiftyTwoWeekLow', price),
            "raw_info": info
        }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_dcf(fcf, growth_rate, discount_rate, terminal_growth_rate, projection_years=5):
    """
    Performs a simple DCF calculation.
    """
    # Safety Check: Discount rate must be > Terminal Growth
    if discount_rate <= terminal_growth_rate:
        return {
            "projected_fcf": [],
            "terminal_value": 0,
            "pv_fcf": 0,
            "pv_tv": 0,
            "total_value": 0,
            "error": "Discount Rate must be > Terminal Growth"
        }

    future_fcf = []
    current_fcf = fcf
    
    # projection phase
    for i in range(1, projection_years + 1):
        current_fcf = current_fcf * (1 + growth_rate)
        future_fcf.append(current_fcf)
        
    # Terminal Value (Gordon Growth Model)
    terminal_value = future_fcf[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    
    # Discounting
    # PV of FCFs
    pv_fcf = 0
    for i, val in enumerate(future_fcf):
        pv_fcf += val / ((1 + discount_rate) ** (i + 1))
        
    # PV of Terminal Value
    pv_tv = terminal_value / ((1 + discount_rate) ** projection_years)
    
    total_value = pv_fcf + pv_tv
    
    return {
        "projected_fcf": future_fcf,
        "terminal_value": terminal_value,
        "pv_fcf": pv_fcf,
        "pv_tv": pv_tv,
        "total_value": total_value
    }

def calculate_sensitivity_grid(base_fcf, base_growth, base_discount, terminal_growth, shares, steps=5, step_size_growth=0.01, step_size_discount=0.01):
    """
    Generates a matrix of share prices for varying Growth and Discount Rates.
    """
    # Create ranges
    mid_idx = steps // 2
    
    # Growth Rates (Columns)
    growth_rates = [base_growth + (i - mid_idx) * step_size_growth for i in range(steps)]
    
    # Discount Rates (Rows)
    discount_rates = [base_discount + (i - mid_idx) * step_size_discount for i in range(steps)]
    
    matrix = []
    
    for r in discount_rates:
        row_prices = []
        for g in growth_rates:
            res = calculate_dcf(base_fcf, g, r, terminal_growth)
            if res.get('error'):
                row_prices.append(0)
            else:
                share_price = res['total_value'] / shares
                row_prices.append(share_price)
        matrix.append(row_prices)
        
    return {
        "growth_rates": growth_rates,
        "discount_rates": discount_rates,
        "matrix": matrix
    }

def run_monte_carlo(fcf, growth_mean, growth_std, discount_mean, discount_std, terminal_growth, iterations=1000):
    """
    Runs Monte Carlo simulation for DCF valuation.
    """
    valuations = []
    
    # Generate random distributions
    g_rates = np.random.normal(growth_mean, growth_std, iterations)
    d_rates = np.random.normal(discount_mean, discount_std, iterations)
    
    for i in range(iterations):
        g = g_rates[i]
        d = d_rates[i]
        
        # Ensure discount > terminal growth + buffer to avoid inf
        if d <= terminal_growth + 0.005: 
             d = terminal_growth + 0.005
             
        res = calculate_dcf(fcf, g, d, terminal_growth)
        valuations.append(res['total_value'])
        
    return valuations
