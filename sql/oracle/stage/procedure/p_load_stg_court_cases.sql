create or replace procedure courts_info.stage_p_load_stg_court_cases
as
begin
    delete from courts_info.stage_stg_court_cases;

    insert into courts_info.stage_stg_court_cases (court, court_alias, check_date, section_name, order_num, case_num,
            hearing_time, hearing_place, case_info, stage, judge, hearing_result, decision_link,
            case_link, row_hash)
    SELECT court,
        court_alias,
        to_date(check_date, 'dd.mm.yyyy') as check_date,
        section_name,
        coalesce(to_number(replace(order_num,'.','')),row_number() over (partition by court_alias, check_date, section_name order by hearing_time, hearing_place)) as order_num,
        case_num,
        hearing_time,
        hearing_place,
        case_info,
        stage,
        judge,
        hearing_result,
        decision_link,
        case_link,
        standard_hash(section_name||'#'||hearing_time||'#'||hearing_place||'#'||case_info||'#'||stage||'#'||judge||'#'||hearing_result||'#'||decision_link||'#'||case_link, 'MD5') as row_hash
    from courts_info.stage_lnd_court_cases;

end;