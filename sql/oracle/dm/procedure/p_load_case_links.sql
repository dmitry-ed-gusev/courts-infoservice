create or replace procedure courts_info.dm_p_load_case_links
as
begin

    delete from courts_info.dm_case_links;

    insert into courts_info.dm_case_links (case_link, court_alias, court_name, case_num, case_uid, link_case_num, link_court_name, link_level, is_primary)
    select clhub.case_link,
	    cchub.court_alias,
	    cfg.title as court_name,
	    cchub.case_num,
	    clhs.case_uid,
	    cll.link_case_num,
	    clls.link_court_name,
	    clls.link_level,
	    clls.is_primary
    from courts_info.dv_case_link_h clhub
	    join courts_info.dv_case_link_hs clhs
		    on clhub.case_link_id = clhs.case_link_id
			    and clhs.end_dttm is null
	    join courts_info.dv_case_link_l cll
		    on clhub.case_link_id = cll.case_link_id
	    join courts_info.dv_court_cases_h cchub
		    on cll.court_case_id = cchub.court_case_id
	    join courts_info.dv_case_link_ls clls
		    on cll.case_link_l_id = clls.case_link_l_id
			    and clls.end_dttm is null
	    join config_court_scrap_config cfg
		    on cchub.court_alias = cfg.alias;

    delete from courts_info.stage_lnd_case_links;
end;
