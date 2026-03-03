#!/usr/bin/env python3
import argparse
import sys
import os

# Ensure app directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import dcf
from guru import GuruAnalysis

def main():
    parser = argparse.ArgumentParser(description="Financial Researcher Tool")
    parser.add_argument("ticker", nargs="?", help="Stock Ticker Symbol")
    parser.add_argument("--full", action="store_true", help="Run full 7-guru analysis")
    parser.add_argument("--quick", action="store_true", help="Run quick metrics analysis")
    
    args = parser.parse_args()
    
    ticker = args.ticker
    mode = "interactive"
    
    if args.full:
        mode = "full"
    elif args.quick:
        mode = "quick"
        
    if not ticker:
        # Check if we can input?
        # For now, just error if no ticker provided in args implies interactive need
        try:
            ticker = input("Enter ticker symbol: ").strip().upper()
        except EOFError:
            print("Error: No ticker provided and cannot read from stdin.")
            sys.exit(1)
            
    if mode == "interactive" and not args.full and not args.quick:
        print(f"analyzing {ticker}...")
        print("Select mode:")
        print("1. Full 7-Guru Analysis")
        print("2. Quick Metrics")
        try:
            choice = input("Choice [1/2]: ").strip()
            if choice == "1":
                mode = "full"
            else:
                mode = "quick"
        except EOFError:
            mode = "full" # Default if non-interactive
            
    print(f"\nFetching data for {ticker}...")
    data = dcf.get_financial_data(ticker)
    
    if not data:
        print("Failed to fetch data.")
        sys.exit(1)
        
    print(f"Name: {data['name']}")
    print(f"Price: {data['currency']} {data['price']}")
    
    if mode == "quick":
        print("\n--- Quick Metrics ---")
        print(f"FCF: {data['fcf']:,.0f}")
        print(f"Shares: {data['shares']:,.0f}")
        print(f"52-Week Range: {data['year_low']} - {data['year_high']}")
        
    elif mode == "full":
        print("\n--- 7-Guru Analysis ---")
        guru = GuruAnalysis(data)
        results = guru.analyze()
        
        for name, result in results.items():
            print(f"{name}: {result}")
            
        print("\n--- DCF Valuation (Base Case) ---")
        # Basic DCF runs with defaults
        dcf_res = dcf.calculate_dcf(data['fcf'], 0.10, 0.10, 0.03)
        if dcf_res.get('error'):
            print(f"DCF Error: {dcf_res['error']}")
        else:
            intrinsic_val = dcf_res['total_value'] / data['shares']
            upside = (intrinsic_val - data['price']) / data['price']
            print(f"Intrinsic Value: {intrinsic_val:.2f}")
            print(f"Upside: {upside:.1%}")

if __name__ == "__main__":
    main()
