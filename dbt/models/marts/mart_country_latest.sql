-- Most recent available value per country x indicator.
select
    f.country_iso3,
    c.country_name,
    c.region,
    c.income_level,
    f.indicator_key,
    i.indicator_name,
    i.unit,
    i.theme,
    f.year as latest_year,
    f.value as latest_value,
    year(current_date) - f.year as years_since_observation
from {{ ref('fct_indicator_observation') }} f
join {{ ref('dim_country') }} c using (country_iso3)
join {{ ref('dim_indicator') }} i using (indicator_key)
qualify row_number() over (partition by f.country_iso3, f.indicator_key order by f.year desc) = 1
