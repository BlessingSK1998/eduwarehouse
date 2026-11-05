-- Every real Eurostat country code must resolve to an ISO3 country.
-- Aggregates (EU27_2020, EA21, ...) are expected to be unmapped and ignored.
select distinct e.geo
from {{ source('raw', 'eurostat_indicators') }} e
left join {{ ref('stg_countries') }} c
  on c.country_iso2 = case e.geo when 'EL' then 'GR' when 'UK' then 'GB' else e.geo end
where c.country_iso3 is null
  and e.geo not like 'EU%' and e.geo not like 'EA%'
