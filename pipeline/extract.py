"""Extract: pull each API into newline-delimited JSON files under data/raw/.

Every parser is a pure function (payload in, flat rows out) so it can be unit
tested offline. Network code is kept in thin `fetch_*` wrappers.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Iterable

import requests

from . import config

log = logging.getLogger("extract")

WB_BASE = "https://api.worldbank.org/v2"
UIS_BASE = "https://api.uis.unesco.org/api/public/data/indicators"
ESTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


# ---------------------------------------------------------------- http
def get_json(url: str, params: dict | None = None, retries: int = 4, timeout: int = 90):
    """GET with exponential backoff. Raises after the last retry so CI fails loudly."""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, timeout=timeout,
                             headers={"User-Agent": "eduwarehouse/1.0 (portfolio ETL project)"})
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt == retries:
                raise
            wait = 2 ** attempt
            log.warning("%s failed (%s); retry %d/%d in %ds", url, exc, attempt, retries, wait)
            time.sleep(wait)


# ---------------------------------------------------------------- parsers
def parse_worldbank(payload: list) -> list[dict]:
    """World Bank v2 returns [meta, rows]; rows is null when nothing matches."""
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        return []
    return [
        {
            "indicator_code": r["indicator"]["id"],
            "country_iso3": r["countryiso3code"] or None,
            "country_name": r["country"]["value"],
            "year": int(r["date"]),
            "value": r["value"],
        }
        for r in payload[1]
    ]


def parse_worldbank_countries(payload: list) -> list[dict]:
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        return []
    return [
        {
            "country_iso3": r["id"],
            "iso2": r["iso2Code"],
            "country_name": r["name"],
            "region": r["region"]["value"],
            "income_level": r["incomeLevel"]["value"],
        }
        for r in payload[1]
    ]


def parse_uis(payload: dict) -> list[dict]:
    return [
        {
            "indicator_code": r["indicatorId"],
            "country_iso3": r["geoUnit"],
            "year": int(r["year"]),
            "value": r["value"],
        }
        for r in payload.get("records", [])
    ]


def parse_jsonstat(payload: dict, dataset: str) -> list[dict]:
    """Flatten a Eurostat JSON-stat 2.0 cube to one row per geo/time observation.

    Values are keyed by a flat index; we decode it with the dimension sizes
    (row-major order) rather than assuming a fixed dimension order.
    """
    ids, sizes = payload["id"], payload["size"]
    cats = {d: sorted(payload["dimension"][d]["category"]["index"].items(), key=lambda kv: kv[1])
            for d in ids}
    rows = []
    for flat, value in payload.get("value", {}).items():
        rem = int(flat)
        coords = {}
        for dim, size in zip(reversed(ids), reversed(sizes)):
            rem, pos = divmod(rem, size)
            coords[dim] = cats[dim][pos][0]
        rows.append({
            "dataset": dataset,
            "geo": coords["geo"],
            "year": int(coords["time"]),
            "value": value,
        })
    return rows


# ---------------------------------------------------------------- fetchers
def fetch_worldbank(indicator: str) -> list[dict]:
    payload = get_json(
        f"{WB_BASE}/country/all/indicator/{indicator}",
        {"format": "json", "per_page": 20000, "date": f"{config.START_YEAR}:{_this_year()}"},
    )
    return parse_worldbank(payload)


def fetch_worldbank_countries() -> list[dict]:
    return parse_worldbank_countries(get_json(f"{WB_BASE}/country", {"format": "json", "per_page": 400}))


def fetch_uis(indicator: str) -> list[dict]:
    payload = get_json(UIS_BASE, {"indicator": indicator, "start": config.START_YEAR, "end": _this_year()})
    return parse_uis(payload)


def fetch_eurostat(dataset: str, filters: dict) -> list[dict]:
    params = {"format": "JSON", "lang": "EN", "sinceTimePeriod": config.START_YEAR, **filters}
    return parse_jsonstat(get_json(f"{ESTAT_BASE}/{dataset}", params), dataset)


def _this_year() -> int:
    return time.gmtime().tm_year


# ---------------------------------------------------------------- landing
def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def extract_all(raw_dir: Path = config.RAW_DIR) -> dict[str, int]:
    """Run every extraction; returns {landing file: row count}."""
    counts: dict[str, int] = {}
    counts["worldbank/countries"] = write_jsonl(raw_dir / "worldbank" / "countries.jsonl", fetch_worldbank_countries())
    for code in config.WORLD_BANK_INDICATORS:
        counts[f"worldbank/{code}"] = write_jsonl(raw_dir / "worldbank" / f"{code}.jsonl", fetch_worldbank(code))
    for code in config.UIS_INDICATORS:
        counts[f"uis/{code}"] = write_jsonl(raw_dir / "uis" / f"{code}.jsonl", fetch_uis(code))
    for ds, filters in config.EUROSTAT_DATASETS.items():
        counts[f"eurostat/{ds}"] = write_jsonl(raw_dir / "eurostat" / f"{ds}.jsonl", fetch_eurostat(ds, filters))
    for name, n in counts.items():
        log.info("landed %-28s %7d rows", name, n)
        if n == 0:
            raise RuntimeError(f"{name} returned 0 rows; refusing to continue with an empty source")
    return counts
