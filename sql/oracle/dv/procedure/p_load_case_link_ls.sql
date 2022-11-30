create or replace procedure courts_info.dv_p_load_case_link_ls
as
begin
    insert into courts_info.dv_case_link_ls (case_link_l_id, begin_dttm, link_court_name, link_level, is_primary, row_hash)
    select lhub.case_link_l_id,
        stg.load_dttm as begin_dttm,
        stg.link_court_name,
        stg.link_level,
        stg.is_primary,
        standard_hash(stg.link_court_name||'#'||stg.link_level||'#'||stg.is_primary, 'MD5') as row_hash
    from courts_info.stage_stg_case_links stg
        join courts_info.dv_court_cases_h hub
            on stg.case_num = hub.case_num
                and stg.court_alias = hub.court_alias
        join courts_info.dv_case_link_h hubcl
            on stg.case_link = hubcl.case_link
        join courts_info.dv_case_link_l lhub
            on lhub.case_link_id = hubcl.case_link_id
                and lhub.court_case_id = hub.court_case_id
                and lhub.link_case_num = coalesce(stg.link_case_num,'N/A')
        left join courts_info.dv_case_link_ls lsat
            on lsat.case_link_l_id = lhub.case_link_l_id
                and lsat.end_dttm is null
                and lsat.row_hash = standard_hash(stg.link_court_name||'#'||stg.link_level||'#'||stg.is_primary, 'MD5')
    where lsat.case_link_l_id is null;

    merge into courts_info.dv_case_link_ls
    using (
        select case_link_l_id, begin_dttm, end_dttm, new_end_dttm
        from (
	        select case_link_l_id, begin_dttm, end_dttm,
		        lead(begin_dttm) over (partition by case_link_l_id order by begin_dttm) as new_end_dttm
	        from courts_info.dv_case_link_ls
        ) ds
    where new_end_dttm is not null
        and end_dttm is null) src
        on (dv_case_link_ls.case_link_l_id = src.case_link_l_id
            and dv_case_link_ls.begin_dttm = src.begin_dttm)
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
	    where (cll.case_link_id) in (
		    select distinct case_link_id
            from courts_info.stage_stg_case_links stg
                join courts_info.dv_case_link_h hubcl
                    on stg.case_link = hubcl.case_link
		    )
		    and stg.court_case_l_id is null
		    ) src
		    on (dv_court_cases_ls.court_case_l_id = src.court_case_l_id
			    and dv_court_cases_ls.begin_dttm = src.begin_dttm)
    when matched then
	    update set end_dttm = sysdate;




    select distinct lhub.case_link_l_id
    from courts_info.stage_stg_case_links stg
        join courts_info.dv_court_cases_h hub
            on stg.case_num = hub.case_num
                and stg.court_alias = hub.court_alias
        join courts_info.dv_case_link_h hubcl
            on stg.case_link = hubcl.case_link
        join courts_info.dv_case_link_l lhub
            on lhub.case_link_id = hubcl.case_link_id
                and lhub.court_case_id = hub.court_case_id
                and lhub.link_case_num = coalesce(stg.link_case_num,'N/A')
        join courts_info.dv_case_link_ls lsat
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
