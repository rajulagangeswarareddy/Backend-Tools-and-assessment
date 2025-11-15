# services/hubspot_api_service.py
import time
import logging
import requests
from typing import Dict, Generator, Optional, List
from collections import deque

LOG = logging.getLogger(__name__)

class HubSpotCredentialError(Exception):
    pass

class HubSpotAPIError(Exception):
    pass

class RateLimiter:
    def __init__(self, max_requests: int = 150, window_seconds: int = 10):
        self.max_requests = max_requests
        self.window = window_seconds
        self.timestamps = deque()

    def wait_if_needed(self):
        now = time.time()
        while self.timestamps and (now - self.timestamps[0]) > self.window:
            self.timestamps.popleft()

        if len(self.timestamps) >= self.max_requests:
            earliest = self.timestamps[0]
            sleep_for = (earliest + self.window) - now
            LOG.warning("Rate limit hit: sleeping for %.2fs", sleep_for)
            time.sleep(max(0.01, sleep_for))

        self.timestamps.append(time.time())


class HubSpotAPIService:
    DEFAULT_BASE = "https://api.hubapi.com"
    DEALS_PATH = "/crm/v3/objects/deals"

    def __init__(self, access_token: str, base_url: Optional[str] = None, timeout: int = 30):
        if not access_token:
            raise HubSpotCredentialError("Missing HubSpot Access Token")

        self.access_token = access_token
        self.base_url = base_url or self.DEFAULT_BASE
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "hubspot-deals-etl/1.0"
        })

        self.rate_limiter = RateLimiter(max_requests=150, window_seconds=10)

    def validate_credentials(self) -> bool:
        url = f"{self.base_url}{self.DEALS_PATH}"
        resp = self.session.get(url, params={"limit": 1})
        if resp.status_code == 401:
            raise HubSpotCredentialError("Invalid token (401)")
        if resp.status_code == 403:
            raise HubSpotCredentialError("Token missing crm.objects.deals.read scope (403)")

        return resp.status_code < 400

    def get_deals_page(self, limit=100, after=None, properties=None):
        params = {"limit": limit}
        if after:
            params["after"] = after
        if properties:
            params["properties"] = ",".join(properties)

        url = f"{self.base_url}{self.DEALS_PATH}"

        self.rate_limiter.wait_if_needed()
        resp = self.session.get(url, params=params, timeout=self.timeout)

        if resp.status_code == 429:
            time.sleep(1)
            return self.get_deals_page(limit, after, properties)

        if resp.status_code >= 400:
            raise HubSpotAPIError(f"Error {resp.status_code}: {resp.text}")

        return resp.json()

    def get_all_deals(self, properties=None, limit=100):
        after = None
        while True:
            page = self.get_deals_page(limit, after, properties)
            results = page.get("results", [])

            for d in results:
                yield d

            next_page = page.get("paging", {}).get("next", {})
            after = next_page.get("after")
            if not after:
                break
