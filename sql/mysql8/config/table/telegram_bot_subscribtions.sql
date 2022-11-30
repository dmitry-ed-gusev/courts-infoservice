drop table if exists config_telegram_bot_subscriptions;

create table config_telegram_bot_subscriptions (
account_id varchar(300),
case_num varchar(255),
court varchar(255),
add_dttm timestamp
);

