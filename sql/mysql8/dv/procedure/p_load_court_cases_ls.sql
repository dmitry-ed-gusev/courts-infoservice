drop procedure if exists dv_p_load_court_cases_ls;

create procedure dv_p_load_court_cases_ls ()
begin
    insert into dv_court_cases_ls (court_case_l_id, begin_dttm, court, section_name, hearing_time, hearing_place,
        case_info, stage, judge, hearing_result, decision_link, case_link, row_hash)
    select lhub.court_case_l_id,
        stg.load_dttm as begin_dttm,
        stg.court,
        stg.section_name,
        stg.hearing_time,
        stg.hearing_place,
        stg.case_info,
        stg.stage,
        stg.judge,
        stg.hearing_result,
        stg.decision_link,
        stg.case_link,
        stg.row_hash
    from stage_stg_court_cases stg
        join dv_court_cases_h hub
            on coalesce(stg.case_num,'N/A') = hub.case_num
                and stg.court_alias = hub.court_alias
        join dv_court_cases_l lhub
            on lhub.court_case_id = hub.court_case_id
                and lhub.check_date = stg.check_date
                and lhub.order_num = stg.order_num
        left join dv_court_cases_ls lsat
            on lsat.court_case_l_id = lhub.court_case_l_id
                and lsat.end_dttm is null
                and lsat.row_hash = stg.row_hash
    where lsat.court_case_l_id is null;

    commit;

    create temporary table temp_dv_court_cases_ls_dates
    as
    select court_case_l_id,
		begin_dttm,
		end_dttm, new_end_dttm
    from (
	    select court_case_l_id,
		    begin_dttm,
		    end_dttm,
		    max(begin_dttm) over (partition by court_case_l_id order by begin_dttm rows between 1 following and 1 following) as new_end_dttm
	    from dv_court_cases_ls
    ) ds
    where new_end_dttm is not null
        and end_dttm is null;

    update dv_court_cases_ls tgt
        join temp_dv_court_cases_ls_dates src
	        on tgt.court_case_l_id = src.court_case_l_id
	            and tgt.begin_dttm = src.begin_dttm
    set tgt.end_dttm = src.new_end_dttm;

    commit;

    -- close deleted records
    create temporary table temp_loaded_court_cases
    as
    select distinct court_alias, check_date
    from stage_stg_court_cases stg;

    create temporary table temp_exist_data
    as
    select distinct lhub.court_case_l_id
    from stage_stg_court_cases stg
        join dv_court_cases_h hub
            on coalesce(stg.case_num,'N/A') = hub.case_num
                and stg.court_alias = hub.court_alias
        join dv_court_cases_l lhub
            on lhub.court_case_id = hub.court_case_id
                and lhub.check_date = stg.check_date
                and lhub.order_num = stg.order_num;

    create temporary table temp_link_to_close
    as
    select ccls.court_case_l_id, ccls.begin_dttm
    from dv_court_cases_l ccl IGNORE INDEX (PRIMARY, court_case_id)
	    join dv_court_cases_ls ccls IGNORE INDEX (PRIMARY)
		    on ccl.court_case_l_id = ccls.court_case_l_id
	    join dv_court_cases_h cch IGNORE INDEX (PRIMARY, idx_case_alias)
	    	on ccl.court_case_id = cch.court_case_id
	    join temp_loaded_court_cases tlcc
		    on ccl.check_date = tlcc.check_date
		    	and cch.court_alias = tlcc.court_alias
	    left join temp_exist_data ted
		    on ccl.court_case_l_id = ted.court_case_l_id
    where ted.court_case_l_id is null
	    and ccls.end_dttm is null;

    update dv_court_cases_ls tgt
	    join temp_link_to_close src
		    on tgt.court_case_l_id = src.court_case_l_id
			    and tgt.begin_dttm = src.begin_dttm
    set tgt.end_dttm = now();

    commit;
end;
