drop table if exists dm_court_case_stats;

create table dm_court_case_stats (
total_rows int,
last_load_dttm varchar(50),
min_dt varchar(50),
max_dt varchar(50)
);