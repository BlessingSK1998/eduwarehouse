-- Per-indicator coverage: the first place to look when a source quietly shrinks.
select
    i.indicator_key,
    i.indicator_name,
    i.source,
    count(*) as n_observations,
    count(distinct f.country_iso3) as n_countries,
    min(f.year) as first_year,
    max(f.year) as last_year
from {{ ref('dim_indicator') }} i
left join {{ ref('fct_indicator_observation') }} f using (indicator_key)
group by 1, 2, 3
