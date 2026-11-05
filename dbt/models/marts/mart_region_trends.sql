-- Simple (unweighted) regional averages; a region-year needs 3+ countries to be reported.
select
    c.region,
    f.indicator_key,
    f.year,
    round(avg(f.value), 2) as avg_value,
    count(*) as n_countries
from {{ ref('fct_indicator_observation') }} f
join {{ ref('dim_country') }} c using (country_iso3)
where c.region is not null
group by 1, 2, 3
having count(*) >= 3
