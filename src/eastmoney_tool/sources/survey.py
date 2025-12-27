from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

# 机构调研统计
REPORT_NAME = "RPT_ORG_SURVEYNEW"


@dataclass(frozen=True)
class SurveyRange:
    label: str
    days_back: int


RANGE_1W = SurveyRange(label="近一周", days_back=7)
RANGE_1M = SurveyRange(label="近一月", days_back=30)


def build_params(
    receive_start_date_gt: str,
    page_number: int = 1,
    page_size: int = 50,
    sort_columns: str = "SUM,NOTICE_DATE,RECEIVE_START_DATE,SECURITY_CODE",
    sort_types: str = "-1,-1,-1,1",
    columns: str = "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,NOTICE_DATE,RECEIVE_START_DATE,RECEIVE_PLACE,RECEIVE_WAY_EXPLAIN,RECEPTIONIST,SUM",
    quote_columns: Optional[str] = "f2~01~SECURITY_CODE~CLOSE_PRICE,f3~01~SECURITY_CODE~CHANGE_RATE",
    quote_type: int = 0,
    extra_filters: str = '(NUMBERNEW="1")(IS_SOURCE="1")',
) -> Dict[str, Any]:
    return {
        "reportName": REPORT_NAME,
        "columns": columns,
        "sortColumns": sort_columns,
        "sortTypes": sort_types,
        "pageNumber": page_number,
        "pageSize": page_size,
        "quoteColumns": quote_columns,
        "quoteType": quote_type,
        "source": "WEB",
        "client": "WEB",
        "filter": f"{extra_filters}(RECEIVE_START_DATE>'{receive_start_date_gt}')",
    }
