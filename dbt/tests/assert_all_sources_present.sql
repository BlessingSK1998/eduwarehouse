-- Guards against a silent source outage: every source must contribute observations.
select s.source
from (select 'worldbank' as source union all select 'uis' union all select 'eurostat') s
left join (select source, count(*) n from {{ ref('fct_indicator_observation') }} group by 1) f using (source)
where coalesce(f.n, 0) = 0
