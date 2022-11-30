drop view if exists dm_v_court_cases;

create view dm_v_court_cases
as
SELECT id,
court,
court_alias,
check_date,
section_name,
order_num,
case_num,
hearing_time,
hearing_place,
case_info,
stage,
judge,
hearing_result,
decision_link,
case_link,
row_hash,
load_dttm
FROM dm_court_cases;
