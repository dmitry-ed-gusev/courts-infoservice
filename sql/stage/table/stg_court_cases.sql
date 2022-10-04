drop table if exists stage.stg_court_cases;

create table stage.stg_court_cases (
court varchar(200),
check_date varchar(50),
section_name varchar(1000),
order_num varchar(10),
case_num varchar(255),
hearing_time varchar(50),
hearing_place varchar(255),
case_info varchar(15000),
stage varchar(1000),
judge varchar(255),
hearing_result varchar(1000),
decision_link varchar(1000),
case_link varchar(1000),
row_hash varchar(100),
load_dttm datetime
);

