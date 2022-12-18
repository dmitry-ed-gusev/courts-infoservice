drop procedure if exists dv_p_load_case_link_l;

create procedure dv_p_load_case_link_l ()
begin
    declare max_id int;
    set max_id = (select coalesce(max(case_link_l_id),0) from dv_case_link_l);

    insert into dv_case_link_l (case_link_l_id, case_link_id, court_case_id, link_case_num)
    select row_number() over () + max_id as court_case_l_id,
        hubcl.case_link_id,
        hub.court_case_id,
        coalesce(stg.link_case_num,'N/A') as link_case_num
    from stage_stg_case_links stg
        join dv_court_cases_h hub
            on stg.case_num = hub.case_num
                and stg.court_alias = hub.court_alias
        join dv_case_link_h hubcl
            on stg.case_link = hubcl.case_link
    where not exists (
            select 1
            from dv_case_link_l lhub
            where lhub.court_case_id = hub.court_case_id
                and lhub.link_case_num = coalesce(stg.link_case_num,'N/A')
        )
    group by hubcl.case_link_id,
        hub.court_case_id,
        coalesce(stg.link_case_num,'N/A');
end;
