"""Build a self-contained dashboard/index.html from the dbt marts.

    python dashboard/build.py [path/to/eduwarehouse.duckdb]
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
DB = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "data" / "eduwarehouse.duckdb"


def rows(con, sql):
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def main():
    con = duckdb.connect(str(DB), read_only=True)
    data = {
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "indicators": rows(con, "select indicator_key, indicator_name, unit, theme, source from marts.dim_indicator order by theme, indicator_name"),
        "latest": rows(con, """select indicator_key, country_iso3 as iso3, country_name as name, region,
                               latest_year as year, round(latest_value, 2) as value
                               from marts.mart_country_latest"""),
        "trends": rows(con, "select indicator_key, region, year, avg_value as v, n_countries as n from marts.mart_region_trends order by year"),
        "coverage": rows(con, "select * from marts.mart_data_coverage order by source, indicator_key"),
        "reconciliation": rows(con, """select count(*) as n_pairs, round(median(abs_diff), 1) as median_diff,
                                       round(100.0 * count(*) filter (abs_diff > 5) / count(*), 0) as pct_over_5
                                       from marts.mart_source_reconciliation""")[0],
    }
    html = (HERE / "template.html").read_text(encoding="utf-8")
    out = HERE / "index.html"
    out.write_text(html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"))), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
