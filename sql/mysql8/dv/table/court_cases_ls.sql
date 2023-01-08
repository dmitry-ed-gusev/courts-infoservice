create table if not exists dv_court_cases_ls (
court_case_l_id int not null,
begin_dttm datetime not null,
end_dttm datetime,
court varchar(200),
section_name varchar(1000),
hearing_time varchar(50),
hearing_place varchar(255),
case_info varchar(10000),
stage varchar(1000),
judge varchar(255),
hearing_result varchar(1000),
decision_link varchar(500),
case_link varchar(500),
row_hash varchar(100) not null,
load_dttm datetime not null default now(),
PRIMARY KEY (court_case_l_id, begin_dttm)
)
ROW_FORMAT=COMPRESSED;
