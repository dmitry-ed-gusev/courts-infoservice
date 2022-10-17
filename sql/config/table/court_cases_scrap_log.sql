drop table if exists config_court_cases_scrap_log;

create table config_court_cases_scrap_log (
court varchar(200),
check_date date,
status varchar(20),
load_dttm datetime
);
