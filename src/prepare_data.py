"""Clean the UCI credit card default data and load it into SQLite.

Run from the repository root:
    python src/prepare_data.py

Inputs:  data/raw/default_of_credit_card_clients.csv
Outputs: data/clean/credit_card_clients_clean.csv
         data/portfolio.db  (SQLite, built from sql/01_create_tables.sql)
"""
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "default_of_credit_card_clients.csv"
CLEAN = ROOT / "data" / "clean" / "credit_card_clients_clean.csv"
DB = ROOT / "data" / "portfolio.db"

PAY_STATUS = [f"PAY_{i}" for i in range(1, 7)]   # 1 = Sep 2005 ... 6 = Apr 2005
BILLS = [f"BILL_AMT{i}" for i in range(1, 7)]
PAYMENTS = [f"PAY_AMT{i}" for i in range(1, 7)]


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.rename(columns={"PAY_0": "PAY_1",
                             "default payment next month": "DEFAULT_NEXT_MONTH"}).copy()

    # Undocumented codes are grouped into the documented "other" category.
    df["EDUCATION"] = df["EDUCATION"].replace({0: 4, 5: 4, 6: 4})
    df["MARRIAGE"] = df["MARRIAGE"].replace({0: 3})

    # Engineered behaviour features.
    df["UTILISATION"] = (df["BILL_AMT1"] / df["LIMIT_BAL"]).clip(lower=0)
    df["MONTHS_LATE_6M"] = (df[PAY_STATUS] >= 1).sum(axis=1)
    df["MAX_DELINQUENCY_6M"] = df[PAY_STATUS].clip(lower=0).max(axis=1)
    billed = df[BILLS].clip(lower=0).sum(axis=1)
    paid = df[PAYMENTS].sum(axis=1)
    df["PAYMENT_RATIO_6M"] = np.where(billed > 0, (paid / billed).clip(upper=1), 1.0)
    return df


def main() -> None:
    raw = pd.read_csv(RAW)
    assert raw.shape == (30000, 25), raw.shape
    df = clean(raw)
    assert df["ID"].is_unique
    assert df.isna().sum().sum() == 0
    CLEAN.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN, index=False)

    DB.unlink(missing_ok=True)
    with sqlite3.connect(DB) as con:
        con.executescript((ROOT / "sql" / "01_create_tables.sql").read_text())
        df.to_sql("customers", con, if_exists="append", index=False)
        n = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    print(f"Clean rows: {len(df):,}; loaded into SQLite: {n:,}")
    print(f"Default rate: {df['DEFAULT_NEXT_MONTH'].mean():.1%}")


if __name__ == "__main__":
    main()
