drop procedure if exists dv_p_load_case_link_hs;

create procedure dv_p_load_case_link_hs ()
begin

    create temporary table temp_case_links_stg_hs
    as
    select distinct case_link, court_alias, case_uid, md5(concat_ws('#', court_alias, case_uid)) as row_hash, load_dttm
    from stage_stg_case_links;

    insert into dv_case_link_hs (case_link_id, begin_dttm, court_alias, case_uid, row_hash)
    select hub.case_link_id,
        stg.load_dttm as begin_dttm,
        stg.court_alias,
        stg.case_uid,
        stg.row_hash
    from temp_case_links_stg_hs stg
        join dv_case_link_h hub
            on stg.case_link = hub.case_link
        left join dv_case_link_hs hs
            on hub.case_link_id = hs.case_link_id
                and hs.end_dttm is null
                and hs.row_hash = stg.row_hash
    where hs.case_link_id is null;

    create temporary table temp_dv_case_link_hs_dates
    as
    select case_link_id,
		begin_dttm,
		end_dttm, new_end_dttm
    from (
	    select case_link_id,
		    begin_dttm,
		    end_dttm,
		    max(begin_dttm) over (partition by case_link_id order by begin_dttm rows between 1 following and 1 following) as new_end_dttm
	    from dv_case_link_hs
    ) ds
    where new_end_dttm is not null
        and end_dttm is null;

    update dv_case_link_hs tgt
        join temp_dv_case_link_hs_dates src
	        on tgt.case_link_id = src.case_link_id
	            and tgt.begin_dttm = src.begin_dttm
    set tgt.end_dttm = src.new_end_dttm;

end;
