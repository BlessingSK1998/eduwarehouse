-- One row per country x indicator x year, across all three sources.
with unioned as (
    select * from {{ ref('stg_worldbank') }}
    union all
    select * from {{ ref('stg_uis') }}
    union all
    select * from {{ ref('stg_eurostat') }}
)

select
    i.indicator_key,
    u.country_iso3,
    u.year,
    u.value,
    u.source
from unioned u
join {{ ref('dim_indicator') }} i
  on i.source = u.source and i.source_code = u.source_code
join {{ ref('dim_country') }} c
  on c.country_iso3 = u.country_iso3
