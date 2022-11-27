drop table if exists config_court_scrap_config;

create table config_court_scrap_config (
link varchar(1000) not null,
title varchar(1000) not null,
skip boolean not null,
alias varchar(50) not null,
server_num varchar(50),
parser_type varchar(50) not null,
refresh_time varchar(10) not null
);

