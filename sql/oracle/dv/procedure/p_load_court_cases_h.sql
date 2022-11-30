create or replace procedure courts_info.dv_p_load_court_cases_h
as
max_id int;
begin
    select coalesce(max(court_case_id),0)
    into max_id
    from courts_info.dv_court_cases_h;

    insert into courts_info.dv_court_cases_h (court_case_id, case_num, court_alias)
    select row_number() over (order by 1) + max_id as court_case_id,
        coalesce(stg.case_num, 'N/A'),
        stg.court_alias
    from courts_info.stage_stg_court_cases stg
    where not exists (
        select 1
        from courts_info.dv_court_cases_h hub
        where stg.court_alias = hub.court_alias
            and coalesce(stg.case_num, 'N/A') = hub.case_num
    )
    group by coalesce(stg.case_num, 'N/A'),
        stg.court_alias;
end;
