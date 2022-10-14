drop view if exists dm_v_court_stats;

create view dm_v_court_stats
as
SELECT dm.court_alias, cfg.title, count(*) as total_rows, min(dm.check_date) as min_dt, max(dm.check_date) as max_dt
FROM dm_court_cases dm
join config_court_scrap_config cfg
	on dm.court_alias = cfg.alias
group by dm.court_alias, cfg.title;
