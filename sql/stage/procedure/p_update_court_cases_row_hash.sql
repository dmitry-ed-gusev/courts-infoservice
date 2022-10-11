drop procedure if exists stage_p_update_court_cases_row_hash;

create procedure stage_p_update_court_cases_row_hash()
begin
    update stage_stg_court_cases
    set row_hash = md5(concat_ws('#', section_name, hearing_time,
        hearing_place, case_info, stage, judge, hearing_result, decision_link, case_link));
end;
