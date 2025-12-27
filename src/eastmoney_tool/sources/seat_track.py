from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

# 机构席位追踪
REPORT_NAME = "RPT_ORGANIZATION_SEATNEW"


@dataclass(frozen=True)
class SeatCycle:
    """Matches STATISTICSCYCLE codes observed on the webpage.
    NOTE: these codes may change; verify via network when needed.
    """
    code: str  # e.g., "02" for 近一月
    label: str


CYCLE_1M = SeatCycle(code="02", label="近一月")
CYCLE_3M = SeatCycle(code="03", label="近三月")
CYCLE_6M = SeatCycle(code="04", label="近六月")


def build_params(
    cycle: SeatCycle,
    page_number: int = 1,
    page_size: int = 50,
    sort_columns: str = "ONLIST_TIMES,SECURITY_CODE",
    sort_types: str = "-1,1",
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
        "filter": f'(STATISTICSCYCLE="{cycle.code}")',
        # omit callback to get JSON directly (works in most cases)
    }
