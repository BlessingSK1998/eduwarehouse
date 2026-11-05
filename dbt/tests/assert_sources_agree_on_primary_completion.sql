{{ config(severity='warn') }}
-- Warn (not fail) when World Bank and UIS disagree by more than 5 points.
select * from {{ ref('mart_source_reconciliation') }}
where abs_diff > 5
