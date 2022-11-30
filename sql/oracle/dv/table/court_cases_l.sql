drop table courts_info.dv_court_cases_l;

create table courts_info.dv_court_cases_l (
court_case_l_id int not null,
court_case_id int not null,
check_date date not null,
order_num int not null,
load_dttm date default sysdate not null,
PRIMARY KEY (court_case_l_id)
);

create unique index idx_dv_court_cases_l_u  on courts_info.dv_court_cases_l (court_case_id, check_date, order_num)
