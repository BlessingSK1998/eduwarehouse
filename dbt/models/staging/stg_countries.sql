select
    country_iso3,
    iso2 as country_iso2,
    country_name,
    nullif(region, '') as region,
    nullif(income_level, '') as income_level,
    region = 'Aggregates' as is_aggregate
from {{ source('raw', 'wb_countries') }}
