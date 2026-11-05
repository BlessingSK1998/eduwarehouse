"""Single place that says which indicators the warehouse pulls."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "eduwarehouse.duckdb"

START_YEAR = 2000

WORLD_BANK_INDICATORS = [
    "SE.ADT.LITR.ZS",       # adult literacy rate
    "SE.PRM.NENR",          # primary net enrolment
    "SE.SEC.ENRR",          # secondary gross enrolment
    "SE.TER.ENRR",          # tertiary gross enrolment
    "SE.XPD.TOTL.GD.ZS",    # govt expenditure on education, % GDP
    "SE.PRM.CMPT.ZS",       # primary completion rate
]

UIS_INDICATORS = [
    "CR.1",        # completion rate, primary
    "CR.2",        # completion rate, lower secondary
    "CR.3",        # completion rate, upper secondary
    "ROFST.1.CP",  # out-of-school RATE (%), primary age. Note OFST.1.CP is a head count.
]

# Eurostat dataset -> fixed dimension filters (everything else is returned)
EUROSTAT_DATASETS = {
    "edat_lfse_03": {"sex": "T", "age": "Y25-34", "isced11": "ED5-8"},  # tertiary attainment 25-34
    "edat_lfse_14": {"sex": "T", "wstatus": "POP"},                      # early leavers 18-24
}
