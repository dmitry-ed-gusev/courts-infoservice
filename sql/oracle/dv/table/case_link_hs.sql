drop table courts_info.dv_case_link_hs;

create table courts_info.dv_case_link_hs (
case_link_id int not null,
begin_dttm date not null,
end_dttm date,
court_alias varchar2(50 char),
case_uid varchar2(50 char),
row_hash varchar2(50 char) not null,
load_dttm date default sysdate,
PRIMARY KEY (case_link_id, begin_dttm)
);
