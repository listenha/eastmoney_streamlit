from __future__ import annotations

import pandas as pd


def filter_netbuy_ratio(df: pd.DataFrame, ratio_col: str, threshold: float = 10.0) -> pd.DataFrame:
    """Filter rows where '机构净买额占总成交额占比' > threshold.
    Many EastMoney columns are string-typed; we coerce to numeric safely.
    """
    if df.empty:
        return df
    if ratio_col not in df.columns:
        raise KeyError(f"Column '{ratio_col}' not found. Available: {list(df.columns)[:20]} ...")

    s = pd.to_numeric(df[ratio_col].astype(str).str.replace("%", "", regex=False), errors="coerce")
    return df.loc[s > threshold].reset_index(drop=True)
