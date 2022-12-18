drop table courts_info.dm_court_cases_old;

create table courts_info.dm_court_cases_old (
id int GENERATED BY DEFAULT ON NULL AS IDENTITY,
court varchar2(200 char) not null,
court_alias varchar2(50 char) not null,
check_date date not null,
section_name varchar2(1000 char),
order_num int,
case_num varchar2(500 char),
hearing_time varchar2(50 char),
hearing_place varchar2(255 char),
case_info varchar2(10000 char),
stage varchar2(1000 char),
judge varchar2(255 char),
hearing_result varchar2(1000 char),
decision_link varchar2(500 char),
case_link varchar2(500 char),
row_hash varchar2(100 char) not null,
load_dttm date not null
);

create index idx_dm_court_cases_old_case_num on courts_info.dm_court_cases_old (case_num);

create index idx_dm_court_cases_old_court_alias on courts_info.dm_court_cases_old (court_alias);

create index idx_dm_court_cases_old_case_link on courts_info.dm_court_cases_old (case_link);