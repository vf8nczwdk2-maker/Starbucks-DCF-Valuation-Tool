import pandas as pd

class GuruAnalysis:
    def __init__(self, data):
        """
        data: Dictionary returned by dcf.get_financial_data, must include 'raw_info'.
        """
        self.data = data
        self.info = data.get('raw_info', {})
        self.ticker = data.get('symbol', 'Unknown') # dcf.py doesn't return symbol explicitly in top level but uses it for lookup
        self.price = data.get('price', 0)
        
    def analyze(self):
        """
        Runs all guru checks and returns a summary.
        """
        results = {}
        
        results['Peter Lynch'] = self._check_lynch()
        results['Benjamin Graham'] = self._check_graham()
        results['Warren Buffett'] = self._check_buffett()
        results['James O\'Shaughnessy'] = self._check_oshaughnessy()
        results['David Dreman'] = self._check_dreman()
        results['Martin Zweig'] = self._check_zweig()
        results['Kenneth Fisher'] = self._check_fisher()
        
        return results

    def _get(self, key, default=None):
        return self.info.get(key, default)

    def _check_lynch(self):
        """
        Peter Lynch: PEG Ratio < 1.0 is good. < 0.5 is excellent.
        """
        peg = self._get('pegRatio')
        if peg is None:
            return "N/A (Missing PEG)"
        
        if peg < 0.5:
            return f"PASS (Excellent PEG: {peg})"
        elif peg < 1.0:
            return f"PASS (Good PEG: {peg})"
        else:
            return f"FAIL (High PEG: {peg})"

    def _check_graham(self):
        """
        Benjamin Graham: 
        1. Price < 1.5 * NCAV (Net Current Asset Value) - Deep Value
        2. P/E * P/B < 22.5 - Moderate Value
        """
        # NCAV = (Current Assets - Total Liabilities) / Shares
        # This is hard to get from just 'info', need balance sheet. 
        # Fallback to P/E * P/B
        
        pe = self._get('trailingPE')
        pb = self._get('priceToBook')
        
        if pe is None or pb is None:
            return "N/A (Missing P/E or P/B)"
        
        graham_number = pe * pb
        if graham_number < 22.5:
            return f"PASS (P/E*P/B = {graham_number:.2f} < 22.5)"
        else:
            return f"FAIL (P/E*P/B = {graham_number:.2f} > 22.5)"

    def _check_buffett(self):
        """
        Warren Buffett: High ROE (>15%), High Profit Margins (>20% is great, depends on sector).
        """
        roe = self._get('returnOnEquity')
        margin = self._get('profitMargins')
        
        if roe is None or margin is None:
            return "N/A (Missing ROE or Margin)"
        
        score = 0
        details = []
        if roe > 0.15:
            score += 1
            details.append(f"ROE {roe:.1%} > 15%")
        else:
            details.append(f"ROE {roe:.1%} < 15%")
            
        if margin > 0.20:
            score += 1
            details.append(f"Margin {margin:.1%} > 20%")
        elif margin > 0.10: # Reasonable 
             details.append(f"Margin {margin:.1%} (Good)")
        else:
             details.append(f"Margin {margin:.1%} (Low)")
             
        if score >= 1:
             return f"PASS ({', '.join(details)})"
        else:
             return f"FAIL ({', '.join(details)})"

    def _check_oshaughnessy(self):
        """
        James O'Shaughnessy: Price/Sales < 1.5
        """
        ps = self._get('priceToSalesTrailing12Months')
        if ps is None:
            return "N/A (Missing P/S)"
        
        if ps < 1.5:
            return f"PASS (P/S {ps:.2f} < 1.5)"
        else:
            return f"FAIL (P/S {ps:.2f} > 1.5)"

    def _check_dreman(self):
        """
        David Dreman: Low P/E (Bottom 20% of market, let's say < 12 approx)
        """
        pe = self._get('trailingPE')
        if pe is None:
            return "N/A (Missing P/E)"
            
        if pe < 12:
            return f"PASS (Low P/E: {pe:.2f})"
        else:
            return f"FAIL (P/E {pe:.2f} > 12)"

    def _check_zweig(self):
        """
        Martin Zweig: P/E < Growth Rate (similar to PEG but often uses trailing PE vs estimated growth)
        """
        pe = self._get('trailingPE')
        growth = self._get('earningsGrowth') # Quarterly yoy
        
        if pe is None or growth is None:
            return "N/A"
            
        # Growth is decimal, e.g. 0.20
        # P/E e.g. 30
        # If P/E 30 and Growth 20% (0.20), specific Zweig comparisons vary but simplistic is PE < Growth*100 ?
        # Actually Lynch uses Growth rate as integer 20 for PE 20.
        # Let's use PEG as proxy or check if Earnings Growth is positive and strong
        
        if growth > 0.15:
            return f"PASS (Strong Earnings Growth: {growth:.1%})"
        else:
            return f"FAIL (Growth {growth:.1%} < 15%)"

    def _check_fisher(self):
        """
        Kenneth Fisher: Price/Sales < 0.75 (Super Stock), < 1.5 (Good) AND Low Debt
        """
        ps = self._get('priceToSalesTrailing12Months')
        de = self._get('debtToEquity')
        
        if ps is None:
            return "N/A"
            
        details = []
        is_pass = False
        
        if ps < 0.75:
            details.append(f"P/S {ps:.2f} < 0.75")
            is_pass = True
        elif ps < 1.5:
            details.append(f"P/S {ps:.2f} < 1.5")
            is_pass = True
        else:
            details.append(f"P/S {ps:.2f} > 1.5")
            
        if de is not None:
             if de < 50: # Debt to Equity ratio often returned as percentage or decimal? 
                 # yfinance usually returns it as a number e.g. 150 (for 150%) or 1.5? 
                 # Checking typical yfinance output: 'debtToEquity': 180.5
                 details.append(f"D/E {de}")
             else:
                 details.append(f"D/E {de} (High)")
                 if ps > 0.75: is_pass = False # Strict Fisher requires both for "Super Stock" but looser for generally good
        
        if is_pass:
            return f"PASS ({', '.join(details)})"
        else:
            return f"FAIL ({', '.join(details)})"
