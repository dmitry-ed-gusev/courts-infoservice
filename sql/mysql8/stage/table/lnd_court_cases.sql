drop table if exists stage_lnd_court_cases;

create table stage_lnd_court_cases (
court varchar(200),
court_alias varchar(50),
check_date varchar(50),
section_name varchar(1000),
order_num varchar(10),
case_num varchar(500),
hearing_time varchar(50),
hearing_place varchar(255),
case_info varchar(10000),
stage varchar(1000),
judge varchar(255),
hearing_result varchar(1000),
decision_link varchar(1000),
case_link varchar(1000)
);

alter table stage_lnd_court_cases add index idx_court_alias_date (court_alias, check_date);
