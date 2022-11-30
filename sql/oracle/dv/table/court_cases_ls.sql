drop table courts_info.dv_court_cases_ls;

create table courts_info.dv_court_cases_ls (
court_case_l_id int not null,
begin_dttm date not null,
end_dttm date,
court varchar2(200 char),
section_name varchar2(1000 char),
hearing_time varchar2(50 char),
hearing_place varchar2(255 char),
case_info varchar2(10000 char),
stage varchar2(1000 char),
judge varchar2(255 char),
hearing_result varchar2(1000 char),
decision_link varchar2(500 char),
case_link varchar2(500 char),
row_hash varchar2(100 char) not null,
load_dttm date default sysdate not null,
PRIMARY KEY (court_case_l_id, begin_dttm)
);
