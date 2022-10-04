drop procedure if exists dm.p_load_court_cases;

create procedure dm.p_load_court_cases ()
begin
    -- delete records that don't exist in stage
    -- find parsed periods
    with updated_data as (
        select distinct court, check_date, str_to_date(check_date, '%d.%m.%Y') as check_date_dt
        from stage.stg_court_cases
    -- find new records
    ), new_data as (
	    select court,
		    str_to_date(src.check_date, '%d.%m.%Y') as check_date,
            src.case_num,
            cast(trim(both '.' from src.order_num) as DECIMAL) as order_num
        from stage.stg_court_cases src
    -- check all existing records from parsed period if they are still exist in source
    ), data_for_delete as (
        select tgt.court, tgt.check_date, tgt.order_num, tgt.case_num
        from dm.court_cases tgt
	        join updated_data
		        on tgt.court = updated_data.court
		        and tgt.check_date = updated_data.check_date_dt
	        left join new_data
		        on tgt.court = new_data.court
		        and tgt.check_date = new_data.check_date
		        and tgt.order_num = new_data.order_num
		        and tgt.case_num = new_data.case_num
        where new_data.court is null
    )
    -- delete records that are no longer exist in source
    delete from dm.court_cases
    where (court, check_date, order_num, case_num) in (
        select court, check_date, order_num, case_num from data_for_delete
    );


    -- delete records that have updated information in stage
    with data_to_delete as (
	    SELECT tgt.court, tgt.case_num, tgt.check_date
	    FROM dm.court_cases tgt
		    join stage.stg_court_cases src
		    on src.court = tgt.court
        	    and str_to_date(src.check_date, '%d.%m.%Y') = tgt.check_date
        	    and src.case_num = tgt.case_num
        	    and cast(trim(both '.' from src.order_num) as DECIMAL) = tgt.order_num
                and src.row_hash <> tgt.row_hash
    )
	delete from dm.court_cases
	where (court, case_num, check_date) in (
	    select court, case_num, check_date from data_to_delete
    );

    -- insert new records from stage
    insert into dm.court_cases (court, check_date, section_name, order_num, case_num, hearing_time,
        hearing_place, case_info, stage, judge, hearing_result, decision_link, case_link, row_hash, load_dttm)
    select src.court,
            str_to_date(src.check_date, '%d.%m.%Y') as check_date,
            src.section_name,
            cast(trim(both '.' from src.order_num) as DECIMAL) as order_num_dec,
            src.case_num, src.hearing_time, src.hearing_place, src.case_info,
            src.stage, src.judge,
            src.hearing_result, src.decision_link,
            src.case_link, src.row_hash, src.load_dttm
    from stage.stg_court_cases src
        left join dm.court_cases tgt
            on src.court = tgt.court
            and str_to_date(src.check_date, '%d.%m.%Y') = tgt.check_date
            and cast(trim(both '.' from src.order_num) as DECIMAL) = tgt.order_num
            and src.case_num = tgt.case_num
    where tgt.row_hash is null;

end;

