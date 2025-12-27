"""格式化工具：用于UI显示的数据格式化"""

from __future__ import annotations

import pandas as pd


# 金额字段的模式（用于识别需要转换的列）
AMOUNT_COLUMN_PATTERNS = [
    'AMT',  # AMOUNT的缩写
    'AMOUNT',
]


def format_amount_to_wan(df: pd.DataFrame) -> pd.DataFrame:
    """将DataFrame中所有金额字段从"元"转换为"万元"
    
    识别所有包含AMT或AMOUNT的列，将其除以10000。
    同时更新列名，添加"(万元)"后缀以明确单位。
    
    Args:
        df: 原始DataFrame
        
    Returns:
        格式化后的DataFrame（金额字段已转换为万元，列名已更新）
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # 找出所有金额字段
    amount_cols = []
    for col in df.columns:
        col_upper = col.upper()
        if any(pattern in col_upper for pattern in AMOUNT_COLUMN_PATTERNS):
            amount_cols.append(col)
    
    # 转换金额字段
    for col in amount_cols:
        if col in df.columns:
            # 转换为数值型
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # 除以10000转换为万元
            df[col] = df[col] / 10000
            # 更新列名，添加"(万元)"后缀
            new_col_name = f"{col}(万元)"
            df = df.rename(columns={col: new_col_name})
    
    return df

