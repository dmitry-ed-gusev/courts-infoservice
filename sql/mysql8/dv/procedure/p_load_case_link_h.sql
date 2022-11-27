drop procedure if exists dv_p_load_case_link_h;

create procedure dv_p_load_case_link_h ()
begin
    declare max_id int;
    set max_id = (select coalesce(max(case_link_id),0) from dv_case_link_h);

    insert into dv_case_link_h (case_link_id, case_link)
    select row_number() over () + max_id as court_case_id,
        dm.case_link
    from dm_court_cases dm
    where dm.case_link is not null
        and not exists (
            select 1
            from dv_case_link_h hub
            where hub.case_link = dm.case_link
        )
    group by dm.case_link;
end;
