create or replace procedure courts_info.dv_p_load_court_cases_ls
as
begin
    insert /*+ NO_INDEX(stage_stg_court_cases) NO_INDEX(dv_court_cases_h) NO_INDEX(dv_court_cases_l) NO_INDEX(dv_court_cases_ls)
	 USE_HASH(stg hub)  USE_HASH(stg lhub)  USE_HASH(lhub lsat)  USE_HASH(stg lsat)*/
        into courts_info.dv_court_cases_ls (court_case_l_id, begin_dttm, court, section_name, hearing_time,
        hearing_place, case_info, stage, judge, hearing_result, decision_link, case_link, row_hash)
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
    from courts_info.stage_stg_court_cases stg
        join courts_info.dv_court_cases_h hub
            on coalesce(stg.case_num,'N/A') = hub.case_num
                and stg.court_alias = hub.court_alias
        join courts_info.dv_court_cases_l lhub
            on lhub.court_case_id = hub.court_case_id
                and lhub.check_date = stg.check_date
                and lhub.order_num = stg.order_num
        left join courts_info.dv_court_cases_ls lsat
            on lsat.court_case_l_id = lhub.court_case_l_id
                and lsat.end_dttm is null
                and lsat.row_hash = stg.row_hash
    where lsat.court_case_l_id is null;

    -- set end_dttm for records that have new version
    merge into courts_info.dv_court_cases_ls
        using (
            select court_case_l_id, begin_dttm, end_dttm, new_end_dttm
            from (
	            select court_case_l_id, begin_dttm, end_dttm,
		            lead(begin_dttm) over (partition by court_case_l_id order by begin_dttm) as new_end_dttm
	            from courts_info.dv_court_cases_ls
            ) ds
            where new_end_dttm is not null
                and end_dttm is null
        ) src
	        on (dv_court_cases_ls.court_case_l_id = src.court_case_l_id
	            and dv_court_cases_ls.begin_dttm = src.begin_dttm)
	when matched then
        update set end_dttm = src.new_end_dttm;

    -- close deleted records
    merge into courts_info.dv_court_cases_ls
    using (
	    select ccls.court_case_l_id, ccls.begin_dttm
	    from courts_info.dv_court_cases_l ccl
		    join courts_info.dv_court_cases_ls ccls
			    on ccl.court_case_l_id = ccls.court_case_l_id
				    and ccls.end_dttm is null
		    join courts_info.dv_court_cases_h cch
			    on ccl.court_case_id = cch.court_case_id
		    left join (
			    select lhub.court_case_l_id, stg.load_dttm as begin_dttm, stg.row_hash
    			    from courts_info.stage_stg_court_cases stg
        			    join courts_info.dv_court_cases_h hub
            			    on coalesce(stg.case_num,'N/A') = hub.case_num
                			    and stg.court_alias = hub.court_alias
        			    join courts_info.dv_court_cases_l lhub
            			    on lhub.court_case_id = hub.court_case_id
                			    and lhub.check_date = stg.check_date
                			    and lhub.order_num = stg.order_num
         		    ) stg
         			    on stg.court_case_l_id = ccls.court_case_l_id
	    where (cch.court_alias, ccl.check_date) in (
		    select distinct court_alias, check_date from courts_info.stage_stg_court_cases
		    )
		    and stg.court_case_l_id is null
		    ) src
		    on (dv_court_cases_ls.court_case_l_id = src.court_case_l_id
			    and dv_court_cases_ls.begin_dttm = src.begin_dttm)
    when matched then
	    update set end_dttm = sysdate;

end;
