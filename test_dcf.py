import sys
import os
from dcf_engine import run_dcf

try:
    # 5.8% rev growth, 15% margin, 8.5% wacc, 2.2% growth
    result = run_dcf(5.8, 15.0, 8.5, 2.2)
    print(f"Intrinsic Value: ${result['intrinsic_value']:.2f}")
    print(f"Enterprise Value: ${result['enterprise_value']/1e9:.2f}B")
    print(f"Net Debt: ${result['net_debt']/1e9:.2f}B")
except Exception as e:
    print(f"Error: {e}")
