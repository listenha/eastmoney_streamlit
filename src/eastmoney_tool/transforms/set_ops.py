from __future__ import annotations

import pandas as pd


def intersect_by_key(a: pd.DataFrame, b: pd.DataFrame, key: str = "SECURITY_CODE") -> pd.DataFrame:
    if a.empty or b.empty:
        return a.iloc[0:0].copy()
    if key not in a.columns or key not in b.columns:
        raise KeyError(f"Missing key '{key}' in one of the frames.")
    return a.merge(b[[key]].drop_duplicates(), on=key, how="inner")

def union_by_key(frames: list[pd.DataFrame], key: str = "SECURITY_CODE") -> pd.DataFrame:
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    if key in df.columns:
        df = df.drop_duplicates(subset=[key], keep="first")
    return df.reset_index(drop=True)

def difference_by_key(a: pd.DataFrame, b: pd.DataFrame, key: str = "SECURITY_CODE") -> pd.DataFrame:
    if a.empty:
        return a
    if b.empty:
        return a.reset_index(drop=True)
    if key not in a.columns or key not in b.columns:
        raise KeyError(f"Missing key '{key}' in one of the frames.")
    bkeys = set(b[key].dropna().astype(str).tolist())
    mask = ~a[key].astype(str).isin(bkeys)
    return a.loc[mask].reset_index(drop=True)
