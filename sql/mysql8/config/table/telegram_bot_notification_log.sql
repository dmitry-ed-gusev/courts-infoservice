drop table if exists config_telegram_bot_notification_log;

create table config_telegram_bot_notification_log (
account_id varchar(300),
case_num varchar(500),
check_date date,
court_alias varchar(50) not null,
order_num int,
row_hash varchar(100) not null,
send_dttm timestamp,
inactive_flag boolean not null default false
);

alter table config_telegram_bot_notification_log add index idx_account_id (account_id);
