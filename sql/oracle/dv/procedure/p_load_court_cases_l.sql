create or replace procedure courts_info.dv_p_load_court_cases_l
as
max_id int;
begin
    select coalesce(max(court_case_l_id),0)
    into max_id
    from courts_info.dv_court_cases_l;

    insert into courts_info.dv_court_cases_l (court_case_l_id, court_case_id, check_date, order_num)
    select row_number() over (order by 1) + max_id as court_case_l_id,
        hub.court_case_id,
        stg.check_date,
        stg.order_num
    from courts_info.stage_stg_court_cases stg
        join courts_info.dv_court_cases_h hub
            on coalesce(stg.case_num,'N/A') = hub.case_num
                and stg.court_alias = hub.court_alias
    where not exists (
        select 1
        from courts_info.dv_court_cases_l lhub
        where lhub.court_case_id = hub.court_case_id
            and lhub.check_date = stg.check_date
            and lhub.order_num = stg.order_num
    )
    group by hub.court_case_id,
        stg.check_date,
        stg.order_num;
end;
