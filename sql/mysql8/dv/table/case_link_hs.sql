drop table if exists dv_case_link_hs;

create table if not exists dv_case_link_hs (
case_link_id int not null,
begin_dttm datetime not null,
end_dttm datetime,
court_alias varchar(50),
case_uid varchar(50),
row_hash varchar(50) not null,
load_dttm datetime default now(),
PRIMARY KEY (case_link_id, begin_dttm)
);
