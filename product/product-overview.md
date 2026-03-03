# DCF Educational App

## The Problem
Valuation concepts are often abstract and intimidating for students.
Textbook examples use static numbers ("Assume growth is 5%"), detaching students from the reality of how these inputs affect real companies.

## Success Looks Like
A student can search for "AAPL", see a baseline DCF, and then *play* with the inputs (Growth, Discount Rate) to see how the value changes.
They understand *why* the value changed because the interface explains it step-by-step.

## Building On (Existing Foundations)
- **`yfinance`**: For fetching real Income Statement and Balance Sheet data.
- **`numpy-financial`**: For robust time-value-of-money calculations.
- **Streamlit**: For immediate interactivity without complex frontend code.

## The Unique Part
**"Educational Mode"**:
- Not just a calculator, but a guided tour.
- "Why did this calculation happen?" tooltips.
- Sensitivity Analysis visuals (Heatmaps) to show that valuation is a range, not a number.

## Tech Stack
- **UI:** Streamlit
- **Backend:** Python (Local)
- **Key Libraries:** `yfinance`, `numpy-financial`, `pandas`, `plotly` (for heatmaps)
