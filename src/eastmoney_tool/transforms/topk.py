from __future__ import annotations

import pandas as pd


def topk(df: pd.DataFrame, col: str, k: int = 10, ascending: bool = False) -> pd.DataFrame:
    if df.empty:
        return df
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found. Available: {list(df.columns)[:20]} ...")
    return df.sort_values(col, ascending=ascending, kind="mergesort").head(k).reset_index(drop=True)
