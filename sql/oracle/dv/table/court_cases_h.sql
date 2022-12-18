drop table courts_info.dv_court_cases_h;

create table courts_info.dv_court_cases_h (
court_case_id int not null,
case_num varchar2(500 char) default 'N/A' not null,
court_alias varchar2(50 char) not null,
load_dttm date default sysdate not null,
PRIMARY KEY (court_case_id)
);

create unique index idx_case_alias on courts_info.dv_court_cases_h (case_num, court_alias);
