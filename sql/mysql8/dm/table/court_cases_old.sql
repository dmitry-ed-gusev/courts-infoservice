drop table if exists dm_court_cases_old;

create table dm_court_cases_old (
id int not null AUTO_INCREMENT,
court varchar(200) not null,
court_alias varchar(50) not null,
check_date date not null,
section_name varchar(1000),
order_num int,
case_num varchar(255),
hearing_time varchar(50),
hearing_place varchar(255),
case_info varchar(10000),
stage varchar(1000),
judge varchar(255),
hearing_result varchar(1000),
decision_link varchar(500),
case_link varchar(500),
row_hash varchar(100) not null,
load_dttm datetime not null,
PRIMARY KEY (id)
);

alter table dm_court_cases_old add index idx_case_num (case_num);

alter table dm_court_cases_old add index idx_court_alias (court_alias);

alter table dm_court_cases_old add index idx_case_link (case_link);
