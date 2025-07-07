# efa-portfolio
# Exploratory Factor Analysis Portfolio Risk Model

This project delivers a robust pipeline for uncovering latent **Market**, **Size**, and **Value** drivers through Exploratory Factor Analysis on stock excess returns, and demonstrates their explanatory power via portfolio regression.


This project demonstrates how to extract **Market**, **Size**, and **Value** risk factors from stock excess-returns using **Exploratory Factor Analysis (EFA)** and validate them in a sample portfolio regression.

## 📖 Overview

1. **Data**

   - Monthly adjusted close prices for 8 large-cap stocks (AAPL, MSFT, AMZN, JPM, GE, KO, WMT, PFE)
   - 3-month US Treasury yield (`DGS3MO`) from FRED

2. **Method**

   - Compute monthly **excess returns**: `R_i - R_f`
   - **Z-score** each series (mean 0, SD 1)
   - **Eigenvalue diagnostics** (Kaiser >1 & ≥65% cumulative variance) → choose 3 factors
   - Run **EFA** with varimax–style rotation to obtain interpretable loadings
   - Compute **factor scores** and **regress** an equal-weight portfolio on them

3. **Results**

   - Three latent factors explain ≈67% of return variance and 97.5% of portfolio variation
   - All factors highly significant (t ≫ 30) with a modest residual alpha

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Othnielobasi/efa-portfolio-risk-model.git
cd efa-portfolio-risk-model
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Acquire data

- Either download your own monthly price CSVs into `data/`,
- Or let the script pull directly via `yfinance` and `pandas-datareader` (FRED).

### 4. Run the analysis

#### Script

```bash
python scripts/efa_portfolio.py
```

#### Notebook

Open `notebooks/efa_portfolio.ipynb` in JupyterLab or VSCode and run all cells.

## 📂 File Descriptions

- **`scripts/efa_portfolio.py`**
  Standalone script that:
  1. Fetches prices & T-bill yields
  2. Computes excess returns & standardizes
  3. Performs eigenvalue diagnostics
  4. Runs EFA (3 factors)
  5. Displays loadings & regressions

- **`notebooks/efa_portfolio.ipynb`**
  Interactive walkthrough with plots (scree, loadings bar chart, regression diagnostics).

- **`requirements.txt`**

  ```text
  pandas
  numpy
  matplotlib
  scikit-learn
  factor_analyzer
  pandas-datareader
  yfinance
  statsmodels
  ```

## ⚠️ Silencing Deprecation Warnings

If a scikit-learn `FutureWarning` appears about `force_all_finite`, add this at the **top** of `scripts/efa_portfolio.py`:

```python
import warnings
warnings.filterwarnings(
    "ignore",
    message=".*force_all_finite.*",
    category=FutureWarning
)
```

Feel free to adapt the tickers, date ranges, or number of factors for your own teaching or research projects!
