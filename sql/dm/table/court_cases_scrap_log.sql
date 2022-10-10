drop table if exists dm_court_cases_scrap_log;

create table dm_court_cases_scrap_log (
court varchar(200),
check_date date,
load_dttm datetime
);
