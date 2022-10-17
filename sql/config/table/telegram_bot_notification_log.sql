drop table if exists config_telegram_bot_notification_log;

create table config_telegram_bot_notification_log (
account_id varchar(300),
case_num varchar(255),
check_date date,
court_alias varchar(50),
row_hash varchar(50),
order_num int,
send_dttm timestamp
);

