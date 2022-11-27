drop table if exists stage_lnd_case_links;

create table stage_lnd_case_links (
case_link varchar(500) not null,
court_alias varchar(50) not null,
case_num varchar(255) not null,
case_uid varchar(100),
link_case_num varchar(255),
link_court_name varchar(500),
link_level varchar(5),
is_primary boolean default false,
load_dttm datetime not null default now()
);
