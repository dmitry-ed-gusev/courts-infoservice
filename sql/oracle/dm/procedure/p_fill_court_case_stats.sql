create or replace procedure courts_info.dm_p_fill_court_case_stats
as
begin

    delete from courts_info.dm_court_case_stats;

    insert into courts_info.dm_court_case_stats (total_rows, last_load_dttm, min_dt, max_dt)
    select count(*) as total_rows,
        to_char(max(load_dttm),'dd.mm.yyyy hh24:mi') as last_load_dttm,
        to_char(min(check_date),'dd.mm.yyyy') as min_dt,
        to_char(max(check_date),'dd.mm.yyyy') as max_dt
    from courts_info.dm_court_cases;
end;
