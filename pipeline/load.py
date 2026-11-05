"""Load: land the JSONL files into DuckDB `raw` schema. Full refresh, idempotent."""
from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from . import config

log = logging.getLogger("load")

# table -> (glob under data/raw, explicit column types)
RAW_TABLES = {
    "wb_countries": ("worldbank/countries.jsonl",
                     {"country_iso3": "VARCHAR", "iso2": "VARCHAR", "country_name": "VARCHAR",
                      "region": "VARCHAR", "income_level": "VARCHAR"}),
    "wb_indicators": ("worldbank/SE.*.jsonl",
                      {"indicator_code": "VARCHAR", "country_iso3": "VARCHAR", "country_name": "VARCHAR",
                       "year": "INTEGER", "value": "DOUBLE"}),
    "uis_indicators": ("uis/*.jsonl",
                       {"indicator_code": "VARCHAR", "country_iso3": "VARCHAR",
                        "year": "INTEGER", "value": "DOUBLE"}),
    "eurostat_indicators": ("eurostat/*.jsonl",
                            {"dataset": "VARCHAR", "geo": "VARCHAR", "year": "INTEGER", "value": "DOUBLE"}),
}


def load_all(raw_dir: Path = config.RAW_DIR, db_path: Path = config.DB_PATH) -> dict[str, int]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    counts = {}
    for table, (pattern, cols) in RAW_TABLES.items():
        cols_sql = ", ".join(f"'{k}': '{v}'" for k, v in cols.items())
        src = str(raw_dir / pattern).replace("'", "''")
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.{table} AS
            SELECT *, now() AS _loaded_at
            FROM read_json('{src}', format='newline_delimited', columns={{{cols_sql}}})
        """)
        counts[table] = con.execute(f"SELECT count(*) FROM raw.{table}").fetchone()[0]
        log.info("loaded raw.%-20s %7d rows", table, counts[table])
    con.close()
    return counts
