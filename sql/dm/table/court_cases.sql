drop table if exists dm.court_cases;

create table dm.court_cases (
court varchar(200),
check_date date,
section_name varchar(100),
order_num int,
case_num varchar(255),
hearing_time varchar(50),
hearing_place varchar(255),
case_info varchar(10000),
judge varchar(255),
hearing_result varchar(1000),
decision_link varchar(1000),
case_link varchar(1000),
load_dttm datetime
);

