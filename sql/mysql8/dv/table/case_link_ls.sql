drop table if exists dv_case_link_ls;

create table if not exists dv_case_link_ls (
case_link_l_id int not null,
begin_dttm datetime not null,
end_dttm datetime,
link_court_name varchar(500),
link_level varchar(5),
is_primary boolean,
row_hash varchar(50) not null,
load_dttm datetime default now(),
PRIMARY KEY (case_link_l_id, begin_dttm)
);
