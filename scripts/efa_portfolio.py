# -*- coding: utf-8 -*-

import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from sklearn.preprocessing import StandardScaler
import numpy as np
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
import matplotlib.pyplot as plt

import warnings

# Silence the sklearn FutureWarning about force_all_finite → ensure_all_finite
warnings.filterwarnings(
    "ignore",
    message=".*force_all_finite.*",
    category=FutureWarning
)



def main():
  # 1. Download monthly prices for stocks and risk-free proxy
  tickers = ["AAPL","MSFT","AMZN","JPM","GE","KO","WMT","PFE"]
  prices = yf.download(tickers, start="2015-01-01", end="2024-12-31", auto_adjust=False)

  prices = prices['Adj Close']
  # prices.columns.name = None
  # 2. Resample to month-end and compute returns
  prices_m = prices.resample("ME").last()
  rets_m = prices_m.pct_change().dropna()

  # 3. Fetch 3-month Treasury yield from FRED
  rf_yield = pdr.DataReader("DGS3MO", "fred", start="2015-01-01", end="2024-12-31")
  rf_m = rf_yield.resample("ME").last().ffill() / 100  

  # 4. Convert discount yield to monthly holding-period return:
  #    HPR ≈ (1 - D/360 * days)⁻¹ - 1; for 91-day T-bill ≈ rf_m * (91/360)
  hpr_rf = rf_m * (91/360)

  # 5. Align and form excess returns
  hpr_rf = hpr_rf.reindex(rets_m.index).ffill()
  excess = rets_m.sub(hpr_rf["DGS3MO"], axis=0)

  # 6. Standardize series
  scaler = StandardScaler()
  X = scaler.fit_transform(excess)
  X = pd.DataFrame(X, index=excess.index, columns=excess.columns)
  #7 Determine optimal n_components via eigenvalues

  #7a Compute correlation matrix
  corr = X.corr()
  eigs, _ = np.linalg.eigh(corr)
  eigs = np.sort(eigs)[::-1]

  # 7b. Cumulative variance explained
  cumvar = np.cumsum(eigs) / len(eigs)
  # Prepare display
  ev_df = pd.DataFrame({
      'Factor': np.arange(1, len(eigs) + 1),
      'Eigenvalue': eigs,
      'Cumulative Variance': cumvar
  })
  print(ev_df)

  # c. Kaiser rule (eigenvalue > 1)
  n_kaiser = np.sum(eigs > 1)

  # 7d. Cumulative‐variance rule (>= 65%)
  n_cum = np.argmax(cumvar >= 0.65) + 1

  # Print decisions
  print(f"\nKaiser criterion suggests n_factors = {n_kaiser}\n")
  print(f"Cumulative variance (>=65%) suggests n_factors = {n_cum}")


  # 8. Test factorability

  chi2, bartlett_p = calculate_bartlett_sphericity(X)
  kmo_all, kmo_model = calculate_kmo(X)
  print(f"Bartlett’s test p-value: {bartlett_p:.4f}")
  print(f"KMO measure: {kmo_model:.3f}")

  #9. Proceed only if tests pass
  if bartlett_p < 0.05 and kmo_model >= 0.6:
      print(f"\nData are factorable — extracting factors…\n")
      fa = FactorAnalyzer(n_factors=3, rotation="varimax")
      fa.fit(X)
      loadings = pd.DataFrame(fa.loadings_, index=X.columns,
                              columns=["Factor1","Factor2","Factor3"])
      print("\nVarimax Loadings:\n", loadings.round(2))
  else:
      print(f"\nFactor analysis not recommended (fails Bartlett/KMO).\n\n")


  # 10. Plot loadings for interpretation
  loadings.plot.bar(figsize=(8,4))
  plt.title("Stock Loadings on Latent Factors")
  plt.ylabel("Loading")
  plt.show()


  # 11. regress an equal-weight portfolio on these factors
  scores = pd.DataFrame(fa.transform(X),
                        index=X.index,
                        columns=loadings.columns)

  port = excess.mean(axis=1)
  import statsmodels.api as sm
  res = sm.OLS(port, sm.add_constant(scores)).fit()
  print(res.summary())

if __name__ == "__main__":
    main()

