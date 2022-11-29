create table if not exists dv_court_cases_h (
court_case_id int not null,
case_num varchar(500) not null default 'N/A',
court_alias varchar(50) not null,
load_dttm datetime default now(),
PRIMARY KEY (court_case_id)
);

alter table dv_court_cases_h add index idx_case_alias (case_num, court_alias);
