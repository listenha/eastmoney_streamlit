from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from .config import EastMoneyConfig


@dataclass
class HttpResponse:
    status_code: int
    text: str
    url: str


class HttpClient:
    """Tiny wrapper over requests.Session with optional rate limiting."""

    def __init__(self, cfg: EastMoneyConfig, min_interval_s: float = 0.25) -> None:
        self.cfg = cfg
        self.session = requests.Session()
        self.min_interval_s = min_interval_s
        self._last_ts = 0.0

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
        now = time.time()
        wait = self.min_interval_s - (now - self._last_ts)
        if wait > 0:
            time.sleep(wait)

        h = {"User-Agent": self.cfg.user_agent, "Referer": "https://data.eastmoney.com/"}
        if headers:
            h.update(headers)

        r = self.session.get(url, params=params, headers=h, timeout=self.cfg.timeout_s)
        self._last_ts = time.time()
        return HttpResponse(status_code=r.status_code, text=r.text, url=r.url)
