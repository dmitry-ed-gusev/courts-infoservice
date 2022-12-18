drop table courts_info.config_court_scrap_config;

create table courts_info.config_court_scrap_config (
link varchar2(1000) not null,
title varchar2(1000) not null,
skip varchar2(5) not null,
alias varchar2(50) not null,
server_num varchar2(50),
parser_type varchar2(50) not null,
refresh_time varchar2(10) not null,
PRIMARY KEY (alias)
);

