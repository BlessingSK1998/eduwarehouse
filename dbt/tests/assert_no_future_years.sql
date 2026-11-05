select * from {{ ref('fct_indicator_observation') }}
where year > year(current_date)
