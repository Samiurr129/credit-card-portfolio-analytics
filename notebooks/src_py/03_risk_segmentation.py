# %% [markdown]
# # 03 · Risk segmentation
#
# **Question:** can the portfolio be split into a few risk tiers that need different actions?
#
# K-Means groups customers on five behaviour features: utilisation, months late, worst
# arrears, payment ratio and credit limit (log). The clusters are then ranked by their
# observed default rate and labelled Tier 1 (lowest risk) to Tier 4 (highest).
# Each customer also carries the out-of-fold model PD from notebook 02.

# %%
import re
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
IMG = ROOT / "images"
SEED = 42
sns.set_theme(style="whitegrid")

df = pd.read_csv(ROOT / "data" / "clean" / "credit_card_clients_clean.csv")
pd_scores = pd.read_csv(ROOT / "data" / "output" / "pd_scores.csv")
df = df.merge(pd_scores, on="ID", validate="one_to_one")

seg_features = pd.DataFrame({
    "utilisation": df["UTILISATION"].clip(upper=1.5),
    "months_late": df["MONTHS_LATE_6M"],
    "max_delinquency": df["MAX_DELINQUENCY_6M"].clip(upper=4),
    "payment_ratio": df["PAYMENT_RATIO_6M"],
    "log_limit": np.log(df["LIMIT_BAL"]),
})
Z = StandardScaler().fit_transform(seg_features)

# %% [markdown]
# ## Choosing the number of clusters

# %%
rng = np.random.default_rng(SEED)
idx = rng.choice(len(Z), 5000, replace=False)
scores = []
for k in range(2, 8):
    km = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(Z)
    scores.append({"k": k, "inertia": km.inertia_,
                   "silhouette": silhouette_score(Z[idx], km.labels_[idx])})
pd.DataFrame(scores).round(3)

# %% [markdown]
# Four clusters is chosen for business use: it gives four actionable tiers and keeps a
# reasonable silhouette score. The scores above show the trade-off.

# %%
km = KMeans(n_clusters=4, n_init=20, random_state=SEED).fit(Z)
df["cluster"] = km.labels_
order = df.groupby("cluster")["DEFAULT_NEXT_MONTH"].mean().sort_values().index
names = ["Tier 1 - Low", "Tier 2 - Moderate", "Tier 3 - Elevated", "Tier 4 - High"]
df["RISK_TIER"] = df["cluster"].map(dict(zip(order, names)))

profile = (df.groupby("RISK_TIER")
             .agg(customers=("ID", "size"),
                  default_rate=("DEFAULT_NEXT_MONTH", "mean"),
                  avg_model_pd=("PD_SCORE", "mean"),
                  avg_utilisation=("UTILISATION", "mean"),
                  avg_months_late=("MONTHS_LATE_6M", "mean"),
                  avg_payment_ratio=("PAYMENT_RATIO_6M", "mean"),
                  avg_limit_ntd=("LIMIT_BAL", "mean")))
profile.insert(1, "portfolio_share", profile["customers"] / len(df))
profile.round(3)

# %% [markdown]
# ## Tier reporting in SQL
# The tiers are written back to SQLite and reported with `sql/03_segmentation_queries.sql`.

# %%
con = sqlite3.connect(ROOT / "data" / "portfolio.db")
con.execute("DELETE FROM risk_tiers")
df[["ID", "RISK_TIER", "PD_SCORE"]].to_sql("risk_tiers", con, if_exists="append", index=False)
con.commit()
df[["ID", "RISK_TIER", "PD_SCORE"]].to_csv(ROOT / "data" / "output" / "risk_tiers.csv", index=False)

text = (ROOT / "sql" / "03_segmentation_queries.sql").read_text()
seg = {}
for block in re.split(r"^-- name: ", text, flags=re.M)[1:]:
    name, sql = block.split("\n", 1)
    seg[name.strip()] = pd.read_sql(sql, con)
seg["tier_summary"]

# %%
seg["exposure_at_default_by_tier"]

# %%
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
ts = seg["tier_summary"]
sns.barplot(data=ts, x="risk_tier", y="portfolio_share_pct", color="#9bb7d4", ax=axes[0])
axes[0].set(xlabel="", ylabel="% of customers", title="Share of portfolio")
sns.barplot(data=ts, x="risk_tier", y="default_rate_pct", color="#b5483f", ax=axes[1])
axes[1].set(xlabel="", ylabel="Default rate next month (%)", title="Observed default rate")
for ax in axes:
    ax.tick_params(axis="x", rotation=15)
fig.suptitle("Four behaviour-based risk tiers", y=1.02)
plt.tight_layout()
plt.savefig(IMG / "risk_segments.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Candidate risk appetite metrics
# Simple, monitorable thresholds suggested by the data.

# %%
high_util = df["UTILISATION"] >= 0.8
late2 = df["PAY_1"] >= 2
appetite = pd.DataFrame({
    "metric": ["Utilisation >= 80%", "2+ months in arrears (Sept)", "Tier 4 share of customers"],
    "share_of_customers_pct": [high_util.mean() * 100, late2.mean() * 100,
                               (df["RISK_TIER"] == names[-1]).mean() * 100],
    "default_rate_pct": [df.loc[high_util, "DEFAULT_NEXT_MONTH"].mean() * 100,
                         df.loc[late2, "DEFAULT_NEXT_MONTH"].mean() * 100,
                         df.loc[df["RISK_TIER"] == names[-1], "DEFAULT_NEXT_MONTH"].mean() * 100],
}).round(1)
appetite.to_csv(ROOT / "data" / "output" / "risk_appetite_metrics.csv", index=False)
profile.round(4).to_csv(ROOT / "data" / "output" / "tier_profile.csv")
appetite
