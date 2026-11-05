select
    country_iso3,
    country_iso2,
    country_name,
    region,
    income_level
from {{ ref('stg_countries') }}
where not is_aggregate
