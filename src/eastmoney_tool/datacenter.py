from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

import pandas as pd

from .config import EastMoneyConfig
from .http import HttpClient


_JSONP_RE = re.compile(r"^[^(]*\((.*)\)\s*;?\s*$", re.DOTALL)


class EastMoneyDataCenter:
    """EastMoney datacenter-web API client.

    Endpoint (base):
      https://datacenter-web.eastmoney.com/api/data/v1/get

    It sometimes returns JSONP if 'callback' is provided.
    We support both JSON and JSONP responses.
    """

    def __init__(self, cfg: Optional[EastMoneyConfig] = None, http: Optional[HttpClient] = None) -> None:
        self.cfg = cfg or EastMoneyConfig()
        self.http = http or HttpClient(self.cfg)

    @staticmethod
    def _loads_json_or_jsonp(text: str) -> Dict[str, Any]:
        text = text.strip()
        if text.startswith("{") or text.startswith("["):
            return json.loads(text)
        m = _JSONP_RE.match(text)
        if not m:
            raise ValueError("Response is neither JSON nor JSONP.")
        return json.loads(m.group(1))

    def get_raw(self, params: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.http.get(self.cfg.base_url, params=params)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} for {resp.url}\nBody: {resp.text[:300]}")
        return self._loads_json_or_jsonp(resp.text)

    def get_result_df(self, params: Dict[str, Any]) -> pd.DataFrame:
        payload = self.get_raw(params)
        # Typical schema: {"result": {"data": [...], "pages": ..., "total": ...}, "success": True, ...}
        result = payload.get("result") or {}
        data = result.get("data") or []
        return pd.DataFrame(data)

    def get_all_pages_df(self, params: Dict[str, Any], page_size: int = 500, max_pages: int = 20) -> pd.DataFrame:
        """Fetch multiple pages and concat. Use carefully to avoid heavy traffic."""
        page = 1
        frames = []
        while page <= max_pages:
            p = dict(params)
            p["pageNumber"] = page
            p["pageSize"] = page_size
            df = self.get_result_df(p)
            if df.empty:
                break
            frames.append(df)
            page += 1
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
