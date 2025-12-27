"""Table 4: 表三 ∩ 表二 (Trade x Seat Intersection)"""

from __future__ import annotations

import pandas as pd

from ..datacenter import EastMoneyDataCenter
from ..sources.seat_track import SeatCycle, CYCLE_1M, CYCLE_3M, CYCLE_6M
from ..transforms.set_ops import intersect_by_key
from .t2_seat import get_seat_topk_intersection
from .t3_trade import get_trade_netbuy_ratio_filtered


def get_trade_x_seat_intersection(
    dc: EastMoneyDataCenter,
    cycle: SeatCycle,
    t3_ratio_col: str = "RATIO",
    t3_threshold: float = 10.0,
    t2_k: int = 10,
    t2_netbuy_col: str = "NET_BUY_AMT",
    t2_buycnt_col: str = "BUY_TIMES",
    key_col: str = "SECURITY_CODE",
    page_size: int = 200,
) -> pd.DataFrame:
    """获取表四：表三 ∩ 表二
    
    Args:
        dc: EastMoneyDataCenter实例
        cycle: 表二的统计周期（CYCLE_1M, CYCLE_3M, CYCLE_6M）
        t3_ratio_col: 表三的占比字段名
        t3_threshold: 表三的占比阈值
        t2_k: 表二的TopK数量
        t2_netbuy_col: 表二的净买额字段名
        t2_buycnt_col: 表二的买入次数字段名
        key_col: 交集键字段名
        page_size: 每页大小
        
    Returns:
        表三 ∩ 表二的交集结果
    """
    # 获取表三（单一结果表）
    t3_df = get_trade_netbuy_ratio_filtered(
        dc, ratio_col=t3_ratio_col, threshold=t3_threshold, page_size=page_size
    )
    
    # 获取表二（对应周期的交集结果）
    _, _, t2_inter = get_seat_topk_intersection(
        dc, cycle=cycle, k=t2_k, netbuy_col=t2_netbuy_col, 
        buycnt_col=t2_buycnt_col, key_col=key_col, page_size=page_size
    )
    
    # 表三 ∩ 表二
    result = intersect_by_key(t3_df, t2_inter, key=key_col)
    
    return result

