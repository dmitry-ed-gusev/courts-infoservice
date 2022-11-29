drop view if exists dm_v_court_case_stats_detail;

create view dm_v_court_case_stats_detail
as
select court_alias, title, total_rows, min_dt, max_dt
from dm_court_case_stat_details;
