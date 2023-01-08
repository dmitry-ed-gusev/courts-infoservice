drop procedure if exists stage_p_load_stg_court_cases;

create procedure stage_p_load_stg_court_cases()
begin
    truncate table stage_stg_court_cases;

    insert into stage_stg_court_cases (court, court_alias, check_date, section_name, order_num, case_num,
            hearing_time, hearing_place, case_info, stage, judge, hearing_result, decision_link,
            case_link, row_hash)
    SELECT court,
        court_alias,
        str_to_date(check_date, '%d.%m.%Y') as check_date,
        section_name,
        row_number() over (partition by court_alias, case_num, check_date order by section_name, hearing_time, hearing_place) as order_num,
        case_num,
        hearing_time,
        hearing_place,
        case_info,
        stage,
        judge,
        hearing_result,
        decision_link,
        case_link,
        md5(concat_ws('#', section_name, hearing_time, hearing_place, case_info, stage, judge, hearing_result, decision_link, case_link)) as row_hash
    from stage_lnd_court_cases;

    commit;

    analyze table stage_stg_court_cases;
end;
