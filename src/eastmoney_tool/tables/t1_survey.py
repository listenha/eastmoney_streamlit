"""Table 1: 机构调研统计 (Survey Statistics)"""

from __future__ import annotations

import datetime as dt
from typing import Optional

import pandas as pd

from ..datacenter import EastMoneyDataCenter
from ..sources.survey import build_params, RANGE_1W, RANGE_1M, SurveyRange


def get_survey_data(
    dc: EastMoneyDataCenter,
    range_type: SurveyRange,
    page_size: int = 200,
) -> pd.DataFrame:
    """获取机构调研统计数据，并按SUM（接待机构数量）降序排序。
    
    Args:
        dc: EastMoneyDataCenter实例
        range_type: 时间范围（RANGE_1W或RANGE_1M）
        page_size: 每页大小
        
    Returns:
        按SUM降序排序的DataFrame
    """
    today = dt.date.today()
    date_gt = (today - dt.timedelta(days=range_type.days_back)).strftime("%Y-%m-%d")
    
    params = build_params(receive_start_date_gt=date_gt, page_size=page_size)
    df = dc.get_result_df(params)
    
    # 按SUM降序排序（如果API已经排序，这里作为保障）
    if 'SUM' in df.columns and len(df) > 0:
        df = df.sort_values('SUM', ascending=False, kind='mergesort')
    
    return df.reset_index(drop=True)

