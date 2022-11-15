drop procedure if exists dm_p_load_court_cases;

create procedure dm_p_load_court_cases ()
begin
    --delete data from dm
    delete from dm_court_cases;

    insert into dm_court_cases (court, court_alias, check_date, section_name, order_num, case_num, hearing_time, hearing_place, case_info, stage, judge, hearing_result, decision_link, case_link, row_hash, load_dttm)
    select lsat.court, hub.court_alias, link.check_date, lsat.section_name, link.order_num, hub.case_num, lsat.hearing_time,
	    lsat.hearing_place, lsat.case_info, lsat.stage, lsat.judge, lsat.hearing_result, lsat.decision_link, lsat.case_link, lsat.row_hash, lsat.load_dttm
    from dv_court_cases_l link
	    join dv_court_cases_h hub
		    on hub.court_case_id = link.court_case_id
	    join dv_court_cases_ls lsat
		    on link.court_case_l_id = lsat.court_case_l_id
			    and lsat.end_dttm is null;

end;
