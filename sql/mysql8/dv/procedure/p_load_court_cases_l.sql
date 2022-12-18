drop procedure if exists dv_p_load_court_cases_l;

create procedure dv_p_load_court_cases_l ()
begin
    declare max_id int;
    set max_id = (select coalesce(max(court_case_l_id),0) from dv_court_cases_l);

    insert into dv_court_cases_l (court_case_l_id, court_case_id, check_date, order_num)
    select row_number() over () + max_id as court_case_l_id,
        hub.court_case_id,
        stg.check_date,
        stg.order_num
    from stage_stg_court_cases stg
        join dv_court_cases_h hub
            on coalesce(stg.case_num,'N/A') = hub.case_num
                and stg.court_alias = hub.court_alias
    where not exists (
        select 1
        from dv_court_cases_l lhub
        where lhub.court_case_id = hub.court_case_id
            and lhub.check_date = stg.check_date
            and lhub.order_num = stg.order_num
    )
    group by hub.court_case_id,
        stg.check_date,
        stg.order_num;
end;
