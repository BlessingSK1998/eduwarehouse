select
    country_iso3,
    iso2 as country_iso2,
    trim(country_name) as country_name,
    nullif(trim(region), '') as region,            -- the API returns trailing spaces, e.g. 'Sub-Saharan Africa '
    nullif(trim(income_level), '') as income_level,
    trim(region) = 'Aggregates' as is_aggregate
from {{ source('raw', 'wb_countries') }}
