create view courts_info.dm_v_court_stats
as
select total_rows, last_load_dttm, min_dt, max_dt
from courts_info.dm_court_case_stats;
