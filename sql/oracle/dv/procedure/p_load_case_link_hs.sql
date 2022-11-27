create or replace procedure courts_info.dv_p_load_case_link_hs
as
begin

    insert into courts_info.dv_case_link_hs (case_link_id, begin_dttm, court_alias, case_uid, row_hash)
    select hub.case_link_id,
        stg.load_dttm as begin_dttm,
        stg.court_alias,
        stg.case_uid,
        stg.row_hash
    from (
        select distinct case_link, court_alias, case_uid,
            standard_hash(court_alias||'#'||case_uid, 'MD5') as row_hash,
            load_dttm
        from courts_info.stage_stg_case_links
        ) stg
        join courts_info.dv_case_link_h hub
            on stg.case_link = hub.case_link
        left join courts_info.dv_case_link_hs hs
            on hub.case_link_id = hs.case_link_id
                and hs.end_dttm is null
                and hs.row_hash = stg.row_hash
    where hs.case_link_id is null;

    merge into courts_info.dv_case_link_hs
    using (
	    select case_link_id, begin_dttm, end_dttm, new_end_dttm
            from (
	            select case_link_id,
		            begin_dttm,
		            end_dttm,
		            lead(begin_dttm) over (partition by case_link_id order by begin_dttm) as new_end_dttm
	            from courts_info.dv_case_link_hs
            ) ds
            where new_end_dttm is not null
                and end_dttm is null
	    ) src
	    on (dv_case_link_hs.case_link_id = src.case_link_id
	        and dv_case_link_hs.begin_dttm = src.begin_dttm)
    when matched then
	    update set end_dttm = src.new_end_dttm;

end;
