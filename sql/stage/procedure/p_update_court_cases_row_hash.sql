drop procedure if exists stage.p_update_court_cases_row_hash;

create procedure stage.p_update_court_cases_row_hash()
begin
    update stage.stg_court_cases
    set row_hash = md5(concat_ws('#', section_name, hearing_time,
        hearing_place, case_info, judge, hearing_result, decision_link, case_link));
end;
