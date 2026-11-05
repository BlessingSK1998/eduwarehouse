-- Eurostat uses its own geo codes: EL = Greece, UK = United Kingdom.
-- Aggregates (EU27_2020, EA21...) match no country and drop out in the join.
with obs as (
    select
        dataset, year, value,
        case geo when 'EL' then 'GR' when 'UK' then 'GB' else geo end as geo_iso2
    from {{ source('raw', 'eurostat_indicators') }}
    where value is not null
)

select
    'eurostat' as source,
    obs.dataset as source_code,
    c.country_iso3,
    obs.year,
    obs.value
from obs
join {{ ref('stg_countries') }} c
  on c.country_iso2 = obs.geo_iso2
 and not c.is_aggregate
