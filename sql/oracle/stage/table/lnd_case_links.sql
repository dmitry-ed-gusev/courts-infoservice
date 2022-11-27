drop table courts_info.stage_lnd_case_links;

create table courts_info.stage_lnd_case_links (
case_link varchar2(500 char) not null,
court_alias varchar2(50 char) not null,
case_num varchar2(255 char) not null,
case_uid varchar2(100 char),
link_case_num varchar2(255 char),
link_court_name varchar2(500 char),
link_level varchar2(5 char),
is_primary varchar2(5 char),
load_dttm date DEFAULT sysdate not null
);