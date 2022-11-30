drop table courts_info.dv_case_link_l;

create table courts_info.dv_case_link_l (
case_link_l_id int not null,
case_link_id int not null,
court_case_id int not null,
link_case_num varchar2(255 char) not null,
load_dttm date default sysdate not null,
PRIMARY KEY (case_link_l_id)
);

create unique index idx_dv_case_link_l_u on courts_info.dv_case_link_l (case_link_id, court_case_id, link_case_num);
