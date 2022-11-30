drop table courts_info.dv_case_link_ls;

create table courts_info.dv_case_link_ls (
case_link_l_id int not null,
begin_dttm date not null,
end_dttm date,
link_court_name varchar2(500 char),
link_level varchar2(5 char),
is_primary varchar2(5 char),
row_hash varchar2(50 char) not null,
load_dttm date default sysdate not null,
PRIMARY KEY (case_link_l_id, begin_dttm)
);
