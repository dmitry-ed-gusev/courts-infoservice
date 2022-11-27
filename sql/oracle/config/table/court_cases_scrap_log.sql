drop table courts_info.config_court_cases_scrap_log;

create table courts_info.config_court_cases_scrap_log (
court varchar2(200 char),
check_date date,
status varchar2(20 char),
load_dttm date
);
