drop view if exists dm_v_court_stats;

create view dm_v_court_stats
as
SELECT total_rows, last_load_dttm, min_dt, max_dt
FROM dm_court_case_stats;
