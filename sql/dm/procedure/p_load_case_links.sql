drop procedure if exists dm_p_load_case_links;

create procedure dm_p_load_case_links ()
begin
    insert into dm_case_links
    select case_link, case_num, case_uid, link_case_num, link_court_name, link_level, is_primary, load_dttm
    from stage_stg_case_links;

    delete from stage_stg_case_links;
end;
