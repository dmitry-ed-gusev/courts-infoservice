create or replace procedure courts_info.dv_p_load_case_link_h
as
max_id int;
begin
    select coalesce(max(case_link_id),0)
    into max_id
    from courts_info.dv_case_link_h;

    insert into courts_info.dv_case_link_h (case_link_id, case_link)
    select row_number() over (order by 1) + max_id as court_case_id,
        dm.case_link
    from courts_info.dm_court_cases dm
    where dm.case_link is not null
        and not exists (
            select 1
            from courts_info.dv_case_link_h hub
            where hub.case_link = dm.case_link
        )
    group by dm.case_link;
end;
