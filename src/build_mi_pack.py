"""Build the Excel MI pack from the analysis outputs.

Run from the repository root, after the three notebooks:
    python src/build_mi_pack.py

Output: excel/portfolio_mi_pack.xlsx
"""
from pathlib import Path
import re
import sqlite3

import pandas as pd
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "output"


def named_queries(path: Path, con) -> dict:
    out = {}
    for block in re.split(r"^-- name: ", path.read_text(), flags=re.M)[1:]:
        name, sql = block.split("\n", 1)
        out[name.strip()] = pd.read_sql(sql, con)
    return out


def main() -> None:
    con = sqlite3.connect(ROOT / "data" / "portfolio.db")
    kpi = named_queries(ROOT / "sql" / "02_portfolio_kpis.sql", con)
    seg = named_queries(ROOT / "sql" / "03_segmentation_queries.sql", con)

    sheets = {
        "Overview": kpi["portfolio_overview"],
        "Risk tiers": seg["tier_summary"],
        "Defaulted balance": seg["exposure_at_default_by_tier"],
        "By arrears status": kpi["default_rate_by_current_status"],
        "By utilisation": kpi["default_rate_by_utilisation_band"],
        "By age band": kpi["default_rate_by_age_band"],
        "By limit band": kpi["limit_band_exposure_share"],
        "Risk appetite": pd.read_csv(OUT / "risk_appetite_metrics.csv"),
        "Model results": pd.read_csv(OUT / "model_results.csv"),
    }

    path = ROOT / "excel" / "portfolio_mi_pack.xlsx"
    path.parent.mkdir(exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        for name, frame in sheets.items():
            frame.to_excel(xw, sheet_name=name, index=False, startrow=2)
            ws = xw.sheets[name]
            ws["A1"] = f"{name} | UCI credit card clients, Taiwan 2005 (NT$)"
            ws["A1"].font = Font(bold=True, size=12)
            for i, col in enumerate(frame.columns, start=1):
                ws.column_dimensions[get_column_letter(i)].width = max(14, len(str(col)) + 2)
            # Red-amber-green colour scale on any default-rate column.
            for i, col in enumerate(frame.columns, start=1):
                if col == "default_rate_pct":
                    letter = get_column_letter(i)
                    rng = f"{letter}4:{letter}{len(frame) + 3}"
                    ws.conditional_formatting.add(rng, ColorScaleRule(
                        start_type="min", start_color="63BE7B",
                        mid_type="percentile", mid_value=50, mid_color="FFEB84",
                        end_type="max", end_color="F8696B"))
    print(f"Wrote {path.relative_to(ROOT)} with {len(sheets)} sheets")


if __name__ == "__main__":
    main()
