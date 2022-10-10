drop table if exists dm_telegram_bot_subscriptions;

create table dm_telegram_bot_subscriptions (
account_id varchar(300),
case_num varchar(255),
last_notification_dttm timestamp
);

