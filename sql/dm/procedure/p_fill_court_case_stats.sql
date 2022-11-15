drop procedure if exists dm_p_fill_court_case_stats;

create procedure dm_p_fill_court_case_stats ()
begin
    insert into dm_court_case_stats (total_rows, last_load_dttm, min_dt, max_dt)
        select count(*) as total_rows,
            date_format(max(load_dttm),'%d.%m.%Y %H:%i') as last_load_dttm,
            date_format(min(check_date),'%d.%m.%Y') as min_dt,
            date_format(max(check_date),'%d.%m.%Y') as max_dt
        from dm_court_cases;
end;
