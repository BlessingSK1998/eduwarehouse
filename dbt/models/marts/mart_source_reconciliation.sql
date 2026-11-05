-- World Bank and UIS both publish primary completion. Where both report the same
-- country-year, how far apart are they?
with wb as (
    select country_iso3, year, value from {{ ref('fct_indicator_observation') }}
    where indicator_key = 'completion_primary_wb'
),
uis as (
    select country_iso3, year, value from {{ ref('fct_indicator_observation') }}
    where indicator_key = 'completion_primary_uis'
)

select
    country_iso3,
    year,
    wb.value as worldbank_value,
    uis.value as uis_value,
    round(abs(wb.value - uis.value), 2) as abs_diff
from wb
join uis using (country_iso3, year)
