"""Offline unit tests for the parsers (no network)."""
from pipeline.extract import parse_jsonstat, parse_uis, parse_worldbank, parse_worldbank_countries


def test_worldbank_parses_and_keeps_nulls():
    payload = [{"page": 1}, [
        {"indicator": {"id": "X"}, "country": {"value": "Zimbabwe"}, "countryiso3code": "ZWE", "date": "2019", "value": 88.8},
        {"indicator": {"id": "X"}, "country": {"value": "Zimbabwe"}, "countryiso3code": "ZWE", "date": "2020", "value": None},
    ]]
    rows = parse_worldbank(payload)
    assert [r["year"] for r in rows] == [2019, 2020]
    assert rows[1]["value"] is None and rows[0]["country_iso3"] == "ZWE"


def test_worldbank_empty_payload():
    assert parse_worldbank([{"message": "x"}, None]) == []
    assert parse_worldbank([{"message": [{"id": "120"}]}]) == []


def test_worldbank_countries():
    payload = [{}, [{"id": "ZWE", "iso2Code": "ZW", "name": "Zimbabwe",
                     "region": {"value": "Sub-Saharan Africa"}, "incomeLevel": {"value": "Lower middle income"}}]]
    assert parse_worldbank_countries(payload)[0]["region"] == "Sub-Saharan Africa"


def test_uis():
    payload = {"records": [{"indicatorId": "CR.1", "geoUnit": "ZWE", "year": 2015, "value": 88.07}]}
    assert parse_uis(payload) == [{"indicator_code": "CR.1", "country_iso3": "ZWE", "year": 2015, "value": 88.07}]
    assert parse_uis({"records": []}) == []


def test_jsonstat_decodes_flat_index():
    # 2 geos x 3 years, row-major (geo outer, time inner); flat index 4 = geo[1], time[1]
    payload = {
        "id": ["geo", "time"], "size": [2, 3],
        "dimension": {
            "geo": {"category": {"index": {"DE": 0, "FR": 1}}},
            "time": {"category": {"index": {"2020": 0, "2021": 1, "2022": 2}}},
        },
        "value": {"0": 10.0, "4": 20.0},
    }
    rows = {(r["geo"], r["year"]): r["value"] for r in parse_jsonstat(payload, "ds")}
    assert rows == {("DE", 2020): 10.0, ("FR", 2021): 20.0}


def test_jsonstat_ignores_singleton_dimensions():
    payload = {
        "id": ["freq", "geo", "time"], "size": [1, 2, 2],
        "dimension": {
            "freq": {"category": {"index": {"A": 0}}},
            "geo": {"category": {"index": {"DE": 0, "FR": 1}}},
            "time": {"category": {"index": {"2021": 0, "2022": 1}}},
        },
        "value": {"3": 5.5},
    }
    assert parse_jsonstat(payload, "ds") == [{"dataset": "ds", "geo": "FR", "year": 2022, "value": 5.5}]
