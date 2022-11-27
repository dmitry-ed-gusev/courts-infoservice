drop table if exists dm_court_case_stats_old;

create table dm_court_case_stats_old (
total_rows int,
last_load_dttm varchar(50),
min_dt varchar(50),
max_dt varchar(50)
);