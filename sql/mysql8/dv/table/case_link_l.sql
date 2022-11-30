drop table if exists dv_case_link_l;

create table if not exists dv_case_link_l (
case_link_l_id int not null,
case_link_id int not null,
court_case_id int not null,
link_case_num varchar(255) not null,
load_dttm datetime default now(),
PRIMARY KEY (case_link_l_id),
UNIQUE KEY (case_link_id, court_case_id, link_case_num)
);
