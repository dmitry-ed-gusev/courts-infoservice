drop view if exists config_v_links_to_refresh;

create view config_v_links_to_refresh
as
SELECT distinct dm.case_link, dm.case_num, cf.parser_type, cf.link
FROM dm_court_cases dm
	join config_court_scrap_config cf
		on dm.court_alias = cf.alias
	left join dm_case_links cl
		on dm.case_link = cl.case_link
where cl.case_link is null
	and dm.case_link is not null;
