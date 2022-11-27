create or replace procedure courts_info.stage_p_load_stg_case_links
as
begin
    delete from courts_info.stage_stg_case_links;

    insert into courts_info.stage_stg_case_links (case_link, court_alias, case_num, case_uid, link_case_num, link_court_name,
                link_level, is_primary)
    select case_link,
        court_alias,
        case_num,
        case_uid,
        link_case_num,
        link_court_name,
        link_level,
        is_primary
    from (
        select case_link, court_alias, case_num, case_uid,
            case when length(link_case_num) = 0 then null else link_case_num end as link_case_num,
            case when length(link_court_name) = 0 then null else link_court_name end as link_court_name,
            link_level,
		    coalesce(is_primary, '0') as is_primary,
            row_number() over (partition by case_link, court_alias, case_num, link_case_num order by link_level desc, is_primary desc) as order_num
        from courts_info.stage_lnd_case_links
    ) x
    where order_num = 1;
end;
