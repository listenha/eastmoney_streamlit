"""Table 2: 机构席位追踪 (Seat Tracking) - TopK交集"""

from __future__ import annotations

import pandas as pd

from ..datacenter import EastMoneyDataCenter
from ..sources.seat_track import build_params, SeatCycle, CYCLE_1M, CYCLE_3M, CYCLE_6M
from ..transforms.topk import topk
from ..transforms.set_ops import intersect_by_key


def get_seat_topk_intersection(
    dc: EastMoneyDataCenter,
    cycle: SeatCycle,
    k: int = 10,
    netbuy_col: str = "NET_BUY_AMT",
    buycnt_col: str = "BUY_TIMES",
    key_col: str = "SECURITY_CODE",
    page_size: int = 200,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """获取表二：TopK交集
    
    Args:
        dc: EastMoneyDataCenter实例
        cycle: 统计周期（CYCLE_1M, CYCLE_3M, CYCLE_6M）
        k: TopK数量，默认10
        netbuy_col: 净买额字段名
        buycnt_col: 买入次数字段名
        key_col: 交集键字段名
        page_size: 每页大小
        
    Returns:
        (top10_netbuy, top10_buycnt, intersection) 三个DataFrame
    """
    params = build_params(cycle=cycle, page_size=page_size)
    df = dc.get_result_df(params)
    
    # Top10 by 净买额
    top10_netbuy = topk(df, netbuy_col, k=k, ascending=False)
    
    # Top10 by 买入次数
    top10_buycnt = topk(df, buycnt_col, k=k, ascending=False)
    
    # 交集
    inter = intersect_by_key(top10_netbuy, top10_buycnt, key=key_col)
    
    return top10_netbuy, top10_buycnt, inter

