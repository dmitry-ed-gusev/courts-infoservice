drop procedure if exists dm_p_fill_court_case_stats;

create procedure dm_p_fill_court_case_stats ()
begin

    delete from dm_court_case_stats_old;

    insert into dm_court_case_stats_old (total_rows, last_load_dttm, min_dt, max_dt)
        select count(*) as total_rows,
            date_format(max(load_dttm),'%d.%m.%Y %H:%i') as last_load_dttm,
            date_format(min(check_date),'%d.%m.%Y') as min_dt,
            date_format(max(check_date),'%d.%m.%Y') as max_dt
        from dm_court_cases_old;

    commit;

    delete from dm_court_case_stat_details_old;

    insert into dm_court_case_stat_details_old (court_alias, title, total_rows, min_dt, max_dt)
    select dm.court_alias, cfg.title, count(*) as total_rows, min(dm.check_date) as min_dt, max(dm.check_date) as max_dt
    from dm_court_cases_old dm
	    join config_court_scrap_config cfg
		    on dm.court_alias = cfg.alias
    group by dm.court_alias, cfg.title;

    commit;
end;
