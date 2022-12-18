drop table courts_info.stage_lnd_court_cases;

create table courts_info.stage_lnd_court_cases (
court varchar2(200 char),
court_alias varchar2(50 char),
check_date varchar2(50 char),
section_name varchar2(1000 char),
order_num varchar2(10 char),
case_num varchar2(500 char),
hearing_time varchar2(50 char),
hearing_place varchar2(255 char),
case_info varchar2(10000 char),
stage varchar2(1000 char),
judge varchar2(255 char),
hearing_result varchar2(1000 char),
decision_link varchar2(1000 char),
case_link varchar2(1000 char)
);

create index idx_lnd_court_alias_date on courts_info.stage_lnd_court_cases (court_alias, check_date);


