drop view if exists config_v_courts_to_retry;

create view config_v_courts_to_retry
as
select cfg.link, cfg.title, cfg.alias, cfg.server_num, cfg.parser_type, x.check_date
from (
	select court, check_date, status, load_dttm, row_number () over (partition by court, check_date order by load_dttm desc) as sort_order
	from config_court_cases_scrap_log
) x
	join config_court_scrap_config cfg
		on x.court = cfg.alias
where x.sort_order = 1
	and x.status <> 'success'
	and adddate(now(), interval -6 hour) > x.load_dttm;
