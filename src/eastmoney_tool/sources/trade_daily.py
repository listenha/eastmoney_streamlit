from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

# 机构买卖每日统计
REPORT_NAME = "RPT_ORGANIZATION_TRADE_DETAILSNEW"


@dataclass(frozen=True)
class TradeWindow:
    """UI-friendly window descriptor. We translate it into a filter (usually TRADE_DATE>=...)."""
    label: str
    days_back: int  # 0 means today only (still needs explicit date outside this module)


WINDOW_TODAY = TradeWindow(label="今天", days_back=0)
WINDOW_3D = TradeWindow(label="近三日", days_back=3)
WINDOW_5D = TradeWindow(label="近五日", days_back=5)
WINDOW_10D = TradeWindow(label="近十日", days_back=10)
WINDOW_1M = TradeWindow(label="近一月", days_back=30)


def build_params(
    trade_date_gte: str,
    page_number: int = 1,
    page_size: int = 50,
    sort_columns: str = "NET_BUY_AMT,TRADE_DATE,SECURITY_CODE",
    sort_types: str = "-1,-1,1",
    columns: str = "ALL",
) -> Dict[str, Any]:
    return {
        "reportName": REPORT_NAME,
        "columns": columns,
        "sortColumns": sort_columns,
        "sortTypes": sort_types,
        "pageNumber": page_number,
        "pageSize": page_size,
        "source": "WEB",
        "client": "WEB",
        "filter": f"(TRADE_DATE>='{trade_date_gte}')",
    }
