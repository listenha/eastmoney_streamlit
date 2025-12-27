"""Table 3: 机构买卖每日统计 (Trade Daily) - 多窗口去重合并"""

from __future__ import annotations

import datetime as dt

import pandas as pd

from ..datacenter import EastMoneyDataCenter
from ..sources.trade_daily import build_params
from ..transforms.trade_filters import filter_netbuy_ratio


# 预定义的时间窗口
WINDOWS = [
    ("today", 0),
    ("3d", 3),
    ("5d", 5),
    ("10d", 10),
    ("1m", 30),
]


def get_trade_netbuy_ratio_filtered(
    dc: EastMoneyDataCenter,
    ratio_col: str = "RATIO",
    threshold: float = 10.0,
    page_size: int = 200,
) -> pd.DataFrame:
    """获取表三：从所有窗口内找出净买额占比 > threshold 的股票，去重合并
    
    Args:
        dc: EastMoneyDataCenter实例
        ratio_col: 占比字段名，默认"RATIO"
        threshold: 占比阈值（百分比），默认10.0
        page_size: 每页大小
        
    Returns:
        去重后的DataFrame（以SECURITY_CODE为键）
    """
    today = dt.date.today()
    frames = []
    
    for label, days in WINDOWS:
        date_gte = (today - dt.timedelta(days=days)).strftime("%Y-%m-%d")
        params = build_params(trade_date_gte=date_gte, page_size=page_size)
        df = dc.get_result_df(params)
        
        # 过滤占比 > threshold
        df_filtered = filter_netbuy_ratio(df, ratio_col=ratio_col, threshold=threshold)
        
        if not df_filtered.empty:
            frames.append(df_filtered)
    
    if not frames:
        return pd.DataFrame()
    
    # 合并并去重（以SECURITY_CODE为键）
    # 过滤掉空DataFrame以避免FutureWarning
    non_empty_frames = [f for f in frames if not f.empty]
    if not non_empty_frames:
        return pd.DataFrame()
    combined = pd.concat(non_empty_frames, ignore_index=True)
    key_col = "SECURITY_CODE"
    
    if key_col in combined.columns:
        deduped = combined.drop_duplicates(subset=[key_col], keep="first")
        return deduped.reset_index(drop=True)
    else:
        # 如果没有SECURITY_CODE字段，直接返回合并结果
        return combined.reset_index(drop=True)

