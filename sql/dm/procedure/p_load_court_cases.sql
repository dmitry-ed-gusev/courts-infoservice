drop procedure if exists dm_p_load_court_cases;

create procedure dm_p_load_court_cases (
    in in_court_alias varchar(50),
    in in_check_date varchar(20)
    )
begin
    --delete data from dm
    delete from dm_court_cases
    where court_alias = in_court_alias and check_date = str_to_date(in_check_date, '%d.%m.%Y');

    -- insert new records from stage
    insert into dm_court_cases (court, court_alias, check_date, section_name, order_num, case_num, hearing_time,
        hearing_place, case_info, stage, judge, hearing_result, decision_link, case_link, row_hash, load_dttm)
    select src.court,
            src.court_alias,
            str_to_date(src.check_date, '%d.%m.%Y') as check_date,
            src.section_name,
            cast(trim(both '.' from src.order_num) as decimal) as order_num_dec,
            src.case_num, src.hearing_time, src.hearing_place, src.case_info,
            src.stage, src.judge,
            src.hearing_result, src.decision_link,
            src.case_link, src.row_hash, src.load_dttm
    from stage_stg_court_cases src
    where src.court_alias = in_court_alias and src.check_date = in_check_date;

    delete from stage_stg_court_cases
    where court_alias = in_court_alias and check_date = in_check_date;

end;
