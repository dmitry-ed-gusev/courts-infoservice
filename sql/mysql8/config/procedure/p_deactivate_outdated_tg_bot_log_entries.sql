drop procedure if exists config_p_deactivate_outdated_tg_bot_log_entries;

create procedure config_p_deactivate_outdated_tg_bot_log_entries ()
begin

    update config_telegram_bot_notification_log nlog
    set inactive_flag = true
    where nlog.inactive_flag = false
        and not exists (
	        select 1
	        from dm_v_court_cases dm
	        where dm.case_num = nlog.case_num
                and dm.court_alias = nlog.court_alias
                and dm.check_date = nlog.check_date
                and dm.order_num = nlog.order_num
                and dm.row_hash = nlog.row_hash
    );

end;