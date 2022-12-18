drop procedure if exists dm_p_load_case_links;

create procedure dm_p_load_case_links ()
begin

    truncate table dm_case_links;

    commit;

    insert into dm_case_links (case_link, court_alias, court_name, case_num, case_uid, link_case_num, link_court_name, link_level, is_primary, load_dttm)
    select clhub.case_link,
	    cchub.court_alias,
	    cfg.title as court_name,
	    cchub.case_num,
	    clhs.case_uid,
	    cll.link_case_num,
	    clls.link_court_name,
	    clls.link_level,
	    clls.is_primary,
	    clls.load_dttm
    from dv_case_link_h clhub
	    join dv_case_link_hs clhs
		    on clhub.case_link_id = clhs.case_link_id
			    and clhs.end_dttm is null
	    join dv_case_link_l cll
		    on clhub.case_link_id = cll.case_link_id
	    join dv_court_cases_h cchub
		    on cll.court_case_id = cchub.court_case_id
	    join dv_case_link_ls clls
		    on cll.case_link_l_id = clls.case_link_l_id
			    and clls.end_dttm is null
	    join config_court_scrap_config cfg
		    on cchub.court_alias = cfg.alias;

    commit;
end;
