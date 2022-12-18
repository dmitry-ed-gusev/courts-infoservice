create or replace procedure courts_info.dv_p_load_case_link_l
as
max_id int;
begin
    select coalesce(max(case_link_l_id),0)
    into max_id
    from courts_info.dv_case_link_l;

    insert into courts_info.dv_case_link_l (case_link_l_id, case_link_id, court_case_id, link_case_num)
    select row_number() over (order by 1) + max_id as court_case_l_id,
        hubcl.case_link_id,
        hub.court_case_id,
        coalesce(stg.link_case_num,'N/A') as link_case_num
    from courts_info.stage_stg_case_links stg
        join courts_info.dv_court_cases_h hub
            on stg.case_num = hub.case_num
                and stg.court_alias = hub.court_alias
        join courts_info.dv_case_link_h hubcl
            on stg.case_link = hubcl.case_link
    where not exists (
            select 1
            from courts_info.dv_case_link_l lhub
            where lhub.court_case_id = hub.court_case_id
                and lhub.link_case_num = coalesce(stg.link_case_num,'N/A')
        )
    group by hubcl.case_link_id,
        hub.court_case_id,
        coalesce(stg.link_case_num,'N/A');
end;
