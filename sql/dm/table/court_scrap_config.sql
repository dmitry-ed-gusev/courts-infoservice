drop table if exists dm.court_scrap_config;

create table dm.court_scrap_config (
link varchar(1000),
title varchar(1000),
skip boolean,
alias varchar(50),
server_num varchar(50),
parser_type varchar(50)
);

