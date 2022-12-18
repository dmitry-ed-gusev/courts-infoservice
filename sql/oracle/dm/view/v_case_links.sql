create or replace view courts_info.dm_v_case_links
as
select case_link,
    court_alias,
    court_name,
    case_num,
    case_uid,
    link_case_num,
    link_court_name,
    link_level,
    is_primary,
    load_dttm
from courts_info.dm_case_links;
