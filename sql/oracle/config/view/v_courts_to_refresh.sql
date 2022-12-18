create or replace view courts_info.config_v_courts_to_refresh
as
select cfg.link, cfg.title, cfg.alias, cfg.server_num, cfg.parser_type, ddim.db_date as check_date
from courts_info.config_court_scrap_config cfg
    cross join courts_info.dm_date_dimension ddim
    left join (
    		select court, check_date, max(load_dttm) as load_dttm
    		from courts_info.config_court_cases_scrap_log
    		group by court, check_date
    ) log
        on cfg.alias = log.court
        	and ddim.db_date = log.check_date
    where skip = '0'
        and (log.court is null
        	 or (trunc(sysdate) = trunc(log.load_dttm)
        			and to_char(current_date, 'hh24:mi') >= cfg.refresh_time
        			and to_char(log.load_dttm, 'hh24:mi') < cfg.refresh_time
        		)
        	  or sysdate - 1 > log.load_dttm
        	);
