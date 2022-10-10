drop table if exists dm_court_scrap_config;

create table dm_court_scrap_config (
link varchar(1000),
title varchar(1000),
skip boolean,
alias varchar(50),
server_num varchar(50),
parser_type varchar(50)
);

