drop procedure if exists config_p_deactivate_outdated_tg_bot_log_entries;

create procedure config_p_deactivate_outdated_tg_bot_log_entries ()
begin

    update config_telegram_bot_notification_log nlog
    set inactive_flag = true
    where nlog.inactive_flag = false
        and not exists (
	        select dm.case_num
	        from dm_v_court_cases dm
	        where dm.case_num = nlog.case_num
                and dm.court_alias = nlog.court_alias
                and dm.check_date = nlog.check_date
                and coalesce(dm.order_num, 0) = coalesce(nlog.order_num, 0)
                and nlog.row_hash = dm.row_hash
    );

end;