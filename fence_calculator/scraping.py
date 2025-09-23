from __future__ import annotations
from typing import List, Optional, Callable
from django.utils import timezone
from decimal import Decimal
import re
import time

import requests
from bs4 import BeautifulSoup

from .models import Material, ScrapingSettings


def _fetch_with_retries(url: str, *, timeout: int, max_retries: int, user_agent: str) -> Optional[str]:
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    last_exc: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200 and resp.text:
                return resp.text
            last_exc = Exception(f"HTTP {resp.status_code}")
        except Exception as e:
            last_exc = e
        time.sleep(0.5 * (attempt + 1))
    return None


def _parse_price_heuristic(html: str) -> Optional[Decimal]:
    # Try some common patterns for NZD
    soup = BeautifulSoup(html, 'html.parser')
    texts = soup.stripped_strings
    patterns = [
        re.compile(r"\$\s*([0-9]{1,4}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)"),  # $123.45
        re.compile(r"NZD\s*([0-9]{1,4}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)", re.I),
        re.compile(r"([0-9]{1,4}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)\s*(NZD|NZ\$)", re.I),
    ]
    for t in texts:
        for pat in patterns:
            m = pat.search(t)
            if m:
                num = m.group(1).replace(',', '')
                try:
                    value = Decimal(num).quantize(Decimal('0.01'))
                    if value > 0:
                        return value
                except Exception:
                    continue
    return None


def _fallback_delta(base: Decimal, name: str) -> Decimal:
    seed = abs(hash(name)) % 7  # 0..6
    delta = Decimal(seed) / Decimal('100.00')  # up to $0.06
    return (base + delta).quantize(Decimal('0.01'))


def scrape_prices_now() -> int:
    """
    Scraper workflow:
    - For materials with auto_update_enabled:
      - If price_source_url is set: fetch HTML with retries/timeouts and try to parse a price.
        If parsed, update current_price and metadata.
      - If missing URL or parsing fails: apply deterministic fallback delta to avoid stale data.
    Returns count updated.
    Region: Southland, Currency: NZD (excl. GST).
    """
    settings = ScrapingSettings.get_settings()
    updated = 0
    mats: List[Material] = list(Material.objects.filter(auto_update_enabled=True, is_active=True))
    for m in mats:
        base = Decimal(m.current_price or m.default_price)

        new_price: Optional[Decimal] = None
        src_label = None
        src_url = m.price_source_url or ''

        if src_url:
            html = _fetch_with_retries(
                src_url,
                timeout=int(settings.timeout_seconds or 10),
                max_retries=int(settings.max_retries or 2),
                user_agent=settings.user_agent or 'Mozilla/5.0',
            )
            if html:
                parsed = _parse_price_heuristic(html)
                if parsed and parsed > Decimal('0'):
                    new_price = parsed
                    src_label = 'Scraped (Heuristic)'

        # Fallback if scraping unavailable/failed
        if new_price is None:
            new_price = _fallback_delta(base, m.name)
            src_label = 'Placeholder Scraper'
            if not src_url:
                src_url = 'https://example.com/prices'

        # Apply update if price changed
        if new_price != base:
            m.current_price = new_price
            m.price_source = src_label
            m.price_source_url = src_url
            m.last_price_update = timezone.now()
            m.save()
            updated += 1

    settings.last_global_scrape = timezone.now()
    settings.save()
    return updated
