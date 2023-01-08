drop table if exists config_telegram_bot_account_link;

create table config_telegram_bot_account_link (
username varchar(200) not null,
account_id varchar(300) not null
);
