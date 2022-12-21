drop view if exists config_v_courts_to_refresh;

create view config_v_courts_to_refresh
as
select cfg.link, cfg.title, cfg.alias, cfg.server_num, cfg.parser_type, ddim.db_date as check_date
from config_court_scrap_config cfg
    cross join dm_data_dimension ddim
    	--on ddim.db_date between adddate(current_date,interval -1 month) and adddate(current_date,interval 3 month)
    left join (
    		select court, check_date, max(load_dttm) as load_dttm
    		from config_court_cases_scrap_log
    		group by court, check_date
    ) log
        on cfg.alias = log.court
        	and ddim.db_date = log.check_date
    where not skip
        and (log.court is null
        	  or adddate(now(), interval -20 hour) > log.load_dttm
        	);
