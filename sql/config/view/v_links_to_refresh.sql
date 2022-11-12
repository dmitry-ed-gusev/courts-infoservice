drop view if exists config_v_links_to_refresh_1;

drop view if exists config_v_links_to_refresh_2;

drop view if exists config_v_links_to_refresh_3;

drop view if exists config_v_links_to_refresh_4;

drop view if exists config_v_links_to_refresh_5;

drop view if exists config_v_links_to_refresh_6;

drop view if exists config_v_links_to_refresh_8;

drop view if exists config_v_links_to_refresh_9;

drop view if exists config_v_links_to_refresh;

create view config_v_links_to_refresh_1
as
SELECT distinct dm.case_link, dm.case_num, cf.parser_type, cf.link
FROM dm_court_cases dm
	join config_court_scrap_config cf
		on dm.court_alias = cf.alias
	left join dm_case_links cl
		on dm.case_link = cl.case_link
where cl.case_link is null
	and dm.case_link is not null
	and parser_type = '1'
limit 10000;

create view config_v_links_to_refresh_2
as
SELECT distinct dm.case_link, dm.case_num, cf.parser_type, cf.link
FROM dm_court_cases dm
	join config_court_scrap_config cf
		on dm.court_alias = cf.alias
	left join dm_case_links cl
		on dm.case_link = cl.case_link
where cl.case_link is null
	and dm.case_link is not null
	and parser_type = '2'
limit 10000;

create view config_v_links_to_refresh_3
as
SELECT distinct dm.case_link, dm.case_num, cf.parser_type, cf.link
FROM dm_court_cases dm
	join config_court_scrap_config cf
		on dm.court_alias = cf.alias
	left join dm_case_links cl
		on dm.case_link = cl.case_link
where cl.case_link is null
	and dm.case_link is not null
	and parser_type = '3'
limit 500;

create view config_v_links_to_refresh_4
as
SELECT distinct dm.case_link, dm.case_num, cf.parser_type, cf.link
FROM dm_court_cases dm
	join config_court_scrap_config cf
		on dm.court_alias = cf.alias
	left join dm_case_links cl
		on dm.case_link = cl.case_link
where cl.case_link is null
	and dm.case_link is not null
	and parser_type = '4'
limit 1000;

create view config_v_links_to_refresh_5
as
SELECT distinct dm.case_link, dm.case_num, cf.parser_type, cf.link
FROM dm_court_cases dm
	join config_court_scrap_config cf
		on dm.court_alias = cf.alias
	left join dm_case_links cl
		on dm.case_link = cl.case_link
where cl.case_link is null
	and dm.case_link is not null
	and parser_type = '5'
limit 2500;

create view config_v_links_to_refresh_6
as
SELECT distinct dm.case_link, dm.case_num, cf.parser_type, cf.link
FROM dm_court_cases dm
	join config_court_scrap_config cf
		on dm.court_alias = cf.alias
	left join dm_case_links cl
		on dm.case_link = cl.case_link
where cl.case_link is null
	and dm.case_link is not null
	and parser_type = '6'
limit 1000;

create view config_v_links_to_refresh_8
as
SELECT distinct dm.case_link, dm.case_num, cf.parser_type, cf.link
FROM dm_court_cases dm
	join config_court_scrap_config cf
		on dm.court_alias = cf.alias
	left join dm_case_links cl
		on dm.case_link = cl.case_link
where cl.case_link is null
	and dm.case_link is not null
	and parser_type = '8'
limit 1000;

create view config_v_links_to_refresh_9
as
SELECT distinct dm.case_link, dm.case_num, cf.parser_type, cf.link
FROM dm_court_cases dm
	join config_court_scrap_config cf
		on dm.court_alias = cf.alias
	left join dm_case_links cl
		on dm.case_link = cl.case_link
where cl.case_link is null
	and dm.case_link is not null
	and parser_type = '9'
limit 1000;

create view config_v_links_to_refresh
as
select case_link, case_num, parser_type, link
from config_v_links_to_refresh_1
union all
select case_link, case_num, parser_type, link
from config_v_links_to_refresh_2
union all
select case_link, case_num, parser_type, link
from config_v_links_to_refresh_3
union all
select case_link, case_num, parser_type, link
from config_v_links_to_refresh_4
union all
select case_link, case_num, parser_type, link
from config_v_links_to_refresh_5
union all
select case_link, case_num, parser_type, link
from config_v_links_to_refresh_6
union all
select case_link, case_num, parser_type, link
from config_v_links_to_refresh_8
union all
select case_link, case_num, parser_type, link
from config_v_links_to_refresh_9;
