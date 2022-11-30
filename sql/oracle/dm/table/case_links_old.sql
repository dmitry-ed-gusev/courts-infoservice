drop table courts_info.dm_case_links_old;

create table courts_info.dm_case_links_old (
case_link varchar2(500 char) not null,
court_alias varchar2(50 char) not null,
court_name varchar2(500 char) not null,
case_num varchar2(255 char) not null,
case_uid varchar2(100 char),
link_case_num varchar2(255 char),
link_court_name varchar2(500 char),
link_level varchar2(5 char),
is_primary varchar2(5 char) not null,
load_dttm date default sysdate not null
);

create index idx_2_case_link on courts_info.dm_case_links_old (case_link);

create index idx_2_case_num on courts_info.dm_case_links_old (case_num);

create index idx_2_case_uid on courts_info.dm_case_links_old (case_uid);

create index idx_2_link_case_num on courts_info.dm_case_links_old (link_case_num);
