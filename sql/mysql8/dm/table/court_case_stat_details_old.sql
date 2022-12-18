drop table if exists dm_court_case_stat_details_old;

create table dm_court_case_stat_details_old (
court_alias varchar(50) not null,
title varchar(1000),
total_rows int,
min_dt date,
max_dt date
);
