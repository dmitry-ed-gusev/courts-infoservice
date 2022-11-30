drop table courts_info.config_telegram_bot_notification_log;

create table courts_info.config_telegram_bot_notification_log (
account_id varchar2(300),
case_num varchar2(255),
check_date date,
court_alias varchar2(50),
order_num int,
row_hash varchar2(50),
send_dttm date,
inactive_flag varchar2(5) default ON NULL '0' not null
);

