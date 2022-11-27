drop procedure if exists dv_p_load_court_cases_h;

create procedure dv_p_load_court_cases_h ()
begin
    declare max_id int;
    set max_id = (select coalesce(max(court_case_id),0) from dv_court_cases_h);

    insert into dv_court_cases_h (court_case_id, case_num, court_alias)
    select row_number() over () + max_id as court_case_id,
        coalesce(stg.case_num, 'N/A'),
        stg.court_alias
    from stage_stg_court_cases stg
    where not exists (
        select 1
        from dv_court_cases_h hub
        where stg.court_alias = hub.court_alias
            and coalesce(stg.case_num, 'N/A') = hub.case_num
    )
    group by coalesce(stg.case_num, 'N/A'),
        stg.court_alias;
end;
