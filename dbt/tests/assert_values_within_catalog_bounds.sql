-- Fails if any observation is negative or above the indicator's plausible maximum.
select f.indicator_key, f.country_iso3, f.year, f.value, i.max_plausible_value
from {{ ref('fct_indicator_observation') }} f
join {{ ref('dim_indicator') }} i using (indicator_key)
where f.value < 0 or f.value > i.max_plausible_value
