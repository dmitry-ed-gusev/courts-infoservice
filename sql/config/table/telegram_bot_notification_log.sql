drop table if exists config_telegram_bot_notification_log;

create table config_telegram_bot_notification_log (
account_id varchar(300),
case_num varchar(255),
check_date date,
court_alias varchar(50),
order_num int,
row_hash varchar(50),
send_dttm timestamp,
inactive_flag boolean not null default false
);

