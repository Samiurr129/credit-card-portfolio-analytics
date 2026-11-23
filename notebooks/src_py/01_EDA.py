# %% [markdown]
# # 01 · Portfolio KPIs and exploratory analysis
#
# **Question:** what does the portfolio look like, and which behaviours go with default?
#
# Data: UCI *Default of Credit Card Clients* (Yeh and Lien, 2009). 30,000 card holders
# in Taiwan, April to September 2005. Amounts are in New Taiwan dollars (NT$).
# The target is default in October 2005.
#
# The KPIs are computed in SQL (`sql/02_portfolio_kpis.sql`) against a SQLite copy of the
# cleaned data. Run `python src/prepare_data.py` first.

# %%
import re
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid", context="notebook")

con = sqlite3.connect(ROOT / "data" / "portfolio.db")
df = pd.read_csv(ROOT / "data" / "clean" / "credit_card_clients_clean.csv")


def run_named_queries(path):
    """Return {query_name: DataFrame} for a file of '-- name:' blocks."""
    text = Path(path).read_text()
    out = {}
    for block in re.split(r"^-- name: ", text, flags=re.M)[1:]:
        name, sql = block.split("\n", 1)
        out[name.strip()] = pd.read_sql(sql, con)
    return out


kpi = run_named_queries(ROOT / "sql" / "02_portfolio_kpis.sql")
kpi["portfolio_overview"]

# %% [markdown]
# ## Default rate by current repayment status
# Arrears in September are the clearest warning sign.

# %%
status = kpi["default_rate_by_current_status"]
status

# %%
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(data=status, x="september_status", y="default_rate_pct", color="#3b6ea5", ax=ax)
ax.axhline(df["DEFAULT_NEXT_MONTH"].mean() * 100, ls="--", c="grey", lw=1)
ax.text(4.4, df["DEFAULT_NEXT_MONTH"].mean() * 100 + 1.5, "portfolio average", ha="right", color="grey")
ax.set(xlabel="", ylabel="Default rate next month (%)",
       title="Customers two months behind default five times as often as those up to date")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(IMG / "default_rate_by_status.png", dpi=150)
plt.show()

# %%
late2 = df.loc[df["PAY_1"] >= 2, "DEFAULT_NEXT_MONTH"].mean()
not_late = df.loc[df["PAY_1"] <= 0, "DEFAULT_NEXT_MONTH"].mean()
print(f"Default rate, 2+ months late in September: {late2:.1%}")
print(f"Default rate, not late in September:       {not_late:.1%}")
print(f"Ratio: {late2 / not_late:.1f}x")

# %% [markdown]
# ## Utilisation
# Default rises with utilisation, but the effect is much weaker than arrears.

# %%
kpi["default_rate_by_utilisation_band"]

# %%
fig, ax = plt.subplots(figsize=(7, 4))
u = kpi["default_rate_by_utilisation_band"]
sns.barplot(data=u, x="utilisation_band", y="default_rate_pct", color="#3b6ea5", ax=ax)
ax.set(xlabel="September balance / credit limit", ylabel="Default rate next month (%)",
       title="Default rate rises from 18% to 30% as utilisation passes 100%")
plt.tight_layout()
plt.savefig(IMG / "default_rate_by_utilisation.png", dpi=150)
plt.show()

# %% [markdown]
# ## Roll rates (August to September)
# A data-quality note: in this dataset the "1 month late" status almost never appears for
# August to April (`PAY_2` to `PAY_6`). Only 28 customers were 1 month late in August.
# Roll rates out of that bucket are therefore not reliable. This is a known quirk of the
# UCI file.

# %%
roll = kpi["delinquency_roll_rates"].pivot(index="aug_bucket", columns="sep_bucket",
                                           values="pct_of_aug_bucket").fillna(0)
roll

# %% [markdown]
# ## Age, credit limit and exposure

# %%
kpi["default_rate_by_age_band"]

# %%
kpi["limit_band_exposure_share"]

# %% [markdown]
# ## Correlation of behaviour features with default

# %%
cols = ["LIMIT_BAL", "AGE", "PAY_1", "PAY_2", "UTILISATION", "MONTHS_LATE_6M",
        "MAX_DELINQUENCY_6M", "PAYMENT_RATIO_6M", "DEFAULT_NEXT_MONTH"]
corr = df[cols].corr()
fig, ax = plt.subplots(figsize=(8, 6.5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax)
ax.set_title("Arrears history correlates most with default")
plt.tight_layout()
plt.savefig(IMG / "correlation_heatmap.png", dpi=150)
plt.show()
corr["DEFAULT_NEXT_MONTH"].drop("DEFAULT_NEXT_MONTH").sort_values(ascending=False).round(3)
