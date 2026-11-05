select
    'uis' as source,
    indicator_code as source_code,
    country_iso3,
    year,
    value
from {{ source('raw', 'uis_indicators') }}
where value is not null
