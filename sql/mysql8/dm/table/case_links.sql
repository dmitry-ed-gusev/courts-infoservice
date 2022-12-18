drop table if exists dm_case_links;

create table dm_case_links (
id int not null AUTO_INCREMENT,
case_link varchar(500) not null,
court_alias varchar(50) not null,
court_name varchar(500) not null,
case_num varchar(255) not null,
case_uid varchar(100),
link_case_num varchar(255),
link_court_name varchar(500),
link_level varchar(5),
is_primary boolean not null,
load_dttm datetime not null,
PRIMARY KEY (id)
)
ROW_FORMAT = COMPRESSED;

alter table dm_case_links add index idx_case_link (case_link);

alter table dm_case_links add index idx_case_num (case_num);

alter table dm_case_links add index idx_case_uid (case_uid);

alter table dm_case_links add index idx_link_case_num (link_case_num);
