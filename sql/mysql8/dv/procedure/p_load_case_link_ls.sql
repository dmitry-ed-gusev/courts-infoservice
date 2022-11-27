drop procedure if exists dv_p_load_case_link_ls;

create procedure dv_p_load_case_link_ls ()
begin
    insert into dv_case_link_ls (case_link_l_id, begin_dttm, link_court_name, link_level, is_primary, row_hash)
    select lhub.case_link_l_id,
        stg.load_dttm as begin_dttm,
        stg.link_court_name,
        stg.link_level,
        stg.is_primary,
        md5(concat_ws('#', stg.link_court_name, stg.link_level, stg.is_primary)) as row_hash
    from stage_stg_case_links stg
        join dv_court_cases_h hub
            on stg.case_num = hub.case_num
                and stg.court_alias = hub.court_alias
        join dv_case_link_h hubcl
            on stg.case_link = hubcl.case_link
        join dv_case_link_l lhub
            on lhub.case_link_id = hubcl.case_link_id
                and lhub.court_case_id = hub.court_case_id
                and lhub.link_case_num = coalesce(stg.link_case_num,'N/A')
        left join dv_case_link_ls lsat
            on lsat.case_link_l_id = lhub.case_link_l_id
                and lsat.end_dttm is null
                and lsat.row_hash = md5(concat_ws('#', stg.link_court_name, stg.link_level, stg.is_primary))
    where lsat.case_link_l_id is null;

    create temporary table temp_dv_case_link_ls_dates
    as
    select case_link_l_id,
		begin_dttm,
		end_dttm, new_end_dttm
    from (
	    select case_link_l_id,
		    begin_dttm,
		    end_dttm,
		    max(begin_dttm) over (partition by case_link_l_id order by begin_dttm rows between 1 following and 1 following) as new_end_dttm
	    from dv_case_link_ls
    ) ds
    where new_end_dttm is not null
        and end_dttm is null;

    update dv_case_link_ls tgt
        join temp_dv_case_link_ls_dates src
	        on tgt.case_link_l_id = src.case_link_l_id
	            and tgt.begin_dttm = src.begin_dttm
    set tgt.end_dttm = src.new_end_dttm;

    -- close deleted records
    create temporary table temp_loaded_links
    as
    select distinct case_link_id
    from stage_stg_case_links stg
        join dv_case_link_h hubcl
           on stg.case_link = hubcl.case_link;

    create temporary table temp_exist_data
    as
    select distinct lhub.case_link_l_id
    from stage_stg_case_links stg
        join dv_court_cases_h hub
            on stg.case_num = hub.case_num
                and stg.court_alias = hub.court_alias
        join dv_case_link_h hubcl
            on stg.case_link = hubcl.case_link
        join dv_case_link_l lhub
            on lhub.case_link_id = hubcl.case_link_id
                and lhub.court_case_id = hub.court_case_id
                and lhub.link_case_num = coalesce(stg.link_case_num,'N/A')
        join dv_case_link_ls lsat
            on lsat.case_link_l_id = lhub.case_link_l_id
                and lsat.end_dttm is null
                and lsat.row_hash = md5(concat_ws('#', stg.link_court_name, stg.link_level, stg.is_primary));

    create temporary table temp_link_to_close
    as
    select clls.case_link_l_id, clls.begin_dttm
    from dv_case_link_l cll
	    join dv_case_link_ls clls
		    on cll.case_link_l_id = clls.case_link_l_id
	    join temp_loaded_links tll
		    on cll.case_link_id = tll.case_link_id
	    left join temp_exist_data ted
		    on cll.case_link_l_id = ted.case_link_l_id
    where ted.case_link_l_id is null
	    and clls.end_dttm is null;

    update dv_case_link_ls tgt
	    join temp_link_to_close src
		    on tgt.case_link_l_id = src.case_link_l_id
			    and tgt.begin_dttm = src.begin_dttm
    set tgt.end_dttm = now();
end;
