drop table if exists config_website_subscriptions;

create table config_website_subscriptions (
username varchar(300),
case_num varchar(255),
court varchar(255),
add_dttm timestamp
);

