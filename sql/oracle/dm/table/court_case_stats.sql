drop table courts_info.dm_court_case_stats;

create table courts_info.dm_court_case_stats (
total_rows int,
last_load_dttm varchar2(50),
min_dt varchar2(50),
max_dt varchar2(50)
);