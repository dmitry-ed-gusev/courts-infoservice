drop view dm.v_courts_to_refresh;

create view dm.v_courts_to_refresh
as
with max_load_date as (
    select court, max(load_dttm) as load_dttm from dm.court_cases_scrap_log group by court
)
select cfg.link, cfg.title, cfg.alias, cfg.server_num, cfg.parser_type
from dm.court_scrap_config cfg
    left join max_load_date log
        on cfg.alias = log.court
    where not skip
        and (log.court is null or date_add(now(), interval -23 hour) > log.load_dttm);