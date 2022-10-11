drop view if exists config_v_courts_to_refresh;

create view config_v_courts_to_refresh
as
with last_load_dttm as (
    select court, max(load_dttm) as load_dttm
    from config_court_cases_scrap_log
    group by court
)
select cfg.link, cfg.title, cfg.alias, cfg.server_num, cfg.parser_type
from config_court_scrap_config cfg
    left join last_load_dttm log
        on cfg.alias = log.court
    where not skip
        and (log.court is null or
        		(current_date > cast(log.load_dttm as date)
        			and current_time >= cast(cfg.refresh_time as time)
        		)
        	);