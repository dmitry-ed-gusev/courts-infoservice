create or replace view courts_info.config_v_links_to_refresh
as
with last_link_alias as (
	select court_alias, case_link, case_num, check_date,
		row_number() over (partition by case_link order by check_date desc) as order_dt
	from courts_info.dm_v_court_cases
	where case_link is not null
), dmv_links as (
	select distinct case_link, court_alias
	from courts_info.dm_v_case_links
)
select dmvcc.court_alias, dmvcc.case_link, cfg.parser_type, cfg.link, dmvcc.case_num
from last_link_alias dmvcc
	join config_court_scrap_config cfg
		on dmvcc.court_alias = cfg.alias
	left join dmv_links dmvcl
		on dmvcc.case_link = dmvcl.case_link
			and dmvcc.court_alias = dmvcl.court_alias
	left join courts_info.stage_stg_case_links lnd
		on dmvcc.case_link = lnd.case_link
			and dmvcc.court_alias = lnd.court_alias
where dmvcc.order_dt = 1
	and dmvcl.case_link is null
	and lnd.case_link is null;
