drop table if exists config_court_scrap_config;

create table config_court_scrap_config (
link varchar(1000),
title varchar(1000),
skip boolean,
alias varchar(50),
server_num varchar(50),
parser_type varchar(50),
refresh_time varchar(10)
);

