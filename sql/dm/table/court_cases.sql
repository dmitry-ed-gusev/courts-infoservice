drop table if exists dm_court_cases;

create table dm_court_cases (
id int not null AUTO_INCREMENT,
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
load_dttm datetime,
PRIMARY KEY (id)
);

/*
PARTITION BY RANGE ( MONTH(CHECK_DATE) ) (
    PARTITION p0 VALUES LESS THAN (1),
    PARTITION p1 VALUES LESS THAN (2),
    PARTITION p2 VALUES LESS THAN (3),
    PARTITION p3 VALUES LESS THAN (4),
    PARTITION p4 VALUES LESS THAN (5),
    PARTITION p5 VALUES LESS THAN (6),
    PARTITION p6 VALUES LESS THAN (7),
    PARTITION p7 VALUES LESS THAN (8),
    PARTITION p8 VALUES LESS THAN (9),
    PARTITION p9 VALUES LESS THAN (10),
    PARTITION p10 VALUES LESS THAN (11),
    PARTITION p11 VALUES LESS THAN MAXVALUE);
*/

alter table dm_court_cases add index idx_case_num (case_num);

alter table dm_court_cases add index idx_court_alias (court_alias);
