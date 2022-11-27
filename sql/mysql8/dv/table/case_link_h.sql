drop table if exists dv_case_link_h;

create table if not exists dv_case_link_h (
case_link_id int not null,
case_link varchar(500) not null,
load_dttm datetime default now(),
PRIMARY KEY (case_link_id)
);

alter table dv_case_link_h add index idx_case_link (case_link);
