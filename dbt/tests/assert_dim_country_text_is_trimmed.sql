-- Regression test: the World Bank API pads some region names with trailing spaces,
-- which silently splits a region into two groups in any GROUP BY.
select country_iso3, region, income_level
from {{ ref('dim_country') }}
where region != trim(region) or income_level != trim(income_level) or country_name != trim(country_name)
