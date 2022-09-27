drop procedure if exists dm.p_load_court_cases;

create procedure dm.p_load_court_cases ()
begin
    delete from dm.court_cases
    where (court, check_date) in (
        select court, str_to_date(check_date, '%d.%m.%Y') as check_date
        from stage.stg_court_cases);

    insert into dm.court_cases (court, check_date, section_name, order_num, case_num, hearing_time,
        hearing_place, case_info, judge, hearing_result, decision_link, case_link, load_dttm)
        select court,
            str_to_date(check_date, '%d.%m.%Y') as check_date,
            section_name,
            cast(trim(both '.' from order_num) as DECIMAL) as order_num_dec,
            case_num, hearing_time, hearing_place, case_info, judge, hearing_result, decision_link,
            case_link, load_dttm
        from stage.stg_court_cases;
end;

