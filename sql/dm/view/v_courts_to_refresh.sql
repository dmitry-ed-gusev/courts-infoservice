drop view dm_v_courts_to_refresh;

create view dm_v_courts_to_refresh
as
select cfg.link, cfg.title, cfg.alias, cfg.server_num, cfg.parser_type
from dm_court_scrap_config cfg
    left join (select court, max(load_dttm) as load_dttm from dm_court_cases_scrap_log group by court) log
        on cfg.alias = log.court
    where not skip
        and (log.court is null or date_add(now(), interval -23 hour) > log.load_dttm);
