drop table if exists dm_court_cases;

create table dm_court_cases (
court varchar(200),
court_alias varchar(50),
check_date date,
section_name varchar(1000),
order_num int,
case_num varchar(255),
hearing_time varchar(50),
hearing_place varchar(255),
case_info varchar(10000),
stage varchar(1000),
judge varchar(255),
hearing_result varchar(1000),
decision_link varchar(1000),
case_link varchar(1000),
row_hash varchar(100),
load_dttm datetime
);

alter table dm_court_cases add index idx_case_num (case_num);
