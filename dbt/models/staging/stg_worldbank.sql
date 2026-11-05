select
    'worldbank' as source,
    indicator_code as source_code,
    country_iso3,
    year,
    value
from {{ source('raw', 'wb_indicators') }}
where value is not null
  and country_iso3 is not null
