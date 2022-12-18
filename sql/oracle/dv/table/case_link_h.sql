drop table courts_info.dv_case_link_h;

create table courts_info.dv_case_link_h (
case_link_id int PRIMARY KEY ,
case_link varchar2(500 char) not null,
load_dttm date default sysdate not null
);

create unique index idx_dv_case_link_h_case_link on courts_info.dv_case_link_h (case_link);
