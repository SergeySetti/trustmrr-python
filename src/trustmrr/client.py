from __future__ import annotations

from typing import Any, Iterator, Optional

import requests


DEFAULT_BASE_URL = "https://trustmrr.com/api/v1"

_VALID_SORTS = frozenset({
    "revenue-desc", "revenue-asc",
    "price-desc", "price-asc",
    "multiple-asc", "multiple-desc",
    "growth-desc", "growth-asc",
    "listed-desc", "listed-asc",
    "best-deal",
})


class TrustMRRError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class TrustMRRClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or requests.Session()

    def list_startups(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        on_sale: Optional[bool] = None,
        category: Optional[str] = None,
        x_handle: Optional[str] = None,
        min_revenue: Optional[float] = None,
        max_revenue: Optional[float] = None,
        min_mrr: Optional[float] = None,
        max_mrr: Optional[float] = None,
        min_growth: Optional[float] = None,
        max_growth: Optional[float] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> dict:
        if page is not None and page < 1:
            raise ValueError("page must be >= 1")
        if limit is not None and not (1 <= limit <= 50):
            raise ValueError("limit must be between 1 and 50")
        if sort is not None and sort not in _VALID_SORTS:
            raise ValueError(f"sort must be one of {sorted(_VALID_SORTS)}")

        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort
        if on_sale is not None:
            params["onSale"] = "true" if on_sale else "false"
        if category is not None:
            params["category"] = category
        if x_handle is not None:
            params["xHandle"] = x_handle
        if min_revenue is not None:
            params["minRevenue"] = min_revenue
        if max_revenue is not None:
            params["maxRevenue"] = max_revenue
        if min_mrr is not None:
            params["minMrr"] = min_mrr
        if max_mrr is not None:
            params["maxMrr"] = max_mrr
        if min_growth is not None:
            params["minGrowth"] = min_growth
        if max_growth is not None:
            params["maxGrowth"] = max_growth
        if min_price is not None:
            params["minPrice"] = min_price
        if max_price is not None:
            params["maxPrice"] = max_price

        return self._request("GET", "/startups", params=params)

    def iter_startups(self, **kwargs: Any) -> Iterator[dict]:
        page = kwargs.pop("page", 1)
        while True:
            result = self.list_startups(page=page, **kwargs)
            for item in result.get("data", []):
                yield item
            if not result.get("meta", {}).get("hasMore"):
                break
            page += 1

    def _request(self, method: str, path: str, *, params: Optional[dict] = None) -> dict:
        url = f"{self._base_url}/{path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }
        resp = self._session.request(
            method=method,
            url=url,
            headers=headers,
            params=params or {},
            timeout=self._timeout,
        )
        try:
            payload = resp.json()
        except ValueError:
            payload = None
        if not resp.ok:
            msg = f"TrustMRR API error {resp.status_code}"
            if isinstance(payload, dict) and "error" in payload:
                msg = f"{msg}: {payload['error']}"
            raise TrustMRRError(msg, status_code=resp.status_code, payload=payload)
        if payload is None:
            raise TrustMRRError("Empty or non-JSON response", status_code=resp.status_code)
        return payload
