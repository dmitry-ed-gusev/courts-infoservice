drop procedure if exists dm_p_load_court_cases;

create procedure dm_p_load_court_cases ()
begin
    -- delete records that don't exist in stage
    -- find parsed periods

    create temporary table temp_updated_data
    as
    select distinct court_alias, check_date, str_to_date(check_date, '%d.%m.%Y') as check_date_dt
    from stg_court_cases;

    -- find new records
    create temporary table temp_new_data as
    select court_alias,
    	str_to_date(src.check_date, '%d.%m.%Y') as check_date,
        src.case_num,
        cast(trim(both '.' from src.order_num) as decimal) as order_num
    from stg_court_cases src;

    -- check all existing records from parsed period if they are still exist in source
    create temporary table temp_data_for_delete
    as
    select tgt.court_alias, tgt.check_date, tgt.order_num, tgt.case_num
    from dm_court_cases tgt
    	join temp_updated_data
	        on tgt.court_alias = temp_updated_data.court_alias
	        and tgt.check_date = temp_updated_data.check_date_dt
	    left join temp_new_data
	        on tgt.court_alias = temp_new_data.court_alias
	            and tgt.check_date = temp_new_data.check_date
		        and tgt.order_num = temp_new_data.order_num
		        and tgt.case_num = temp_new_data.case_num
    where temp_new_data.court_alias is null;

    -- delete records that are no longer exist in source
    delete from dm_court_cases
    where (court_alias, check_date, order_num, case_num) in (
        select court_alias, check_date, order_num, case_num from temp_data_for_delete
    );

	create temporary table tmp_data_to_delete
	as
	select tgt.court_alias, tgt.case_num, tgt.check_date
	    FROM dm_court_cases tgt
		    join stg_court_cases src
		    on src.court_alias = tgt.court_alias
        	    and str_to_date(src.check_date, '%d.%m.%Y') = tgt.check_date
        	    and src.case_num = tgt.case_num
        	    and cast(trim(both '.' from src.order_num) as DECIMAL) = tgt.order_num
                and src.row_hash <> tgt.row_hash;

    -- delete records that have updated information in stage
	delete from dm_court_cases
	where (court_alias, case_num, check_date) in (
	    select court_alias, case_num, check_date from tmp_data_to_delete
    );

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
    from stg_court_cases src
        left join dm_court_cases tgt
            on src.court_alias = tgt.court_alias
            and str_to_date(src.check_date, '%d.%m.%Y') = tgt.check_date
            and cast(trim(both '.' from src.order_num) as decimal) = tgt.order_num
            and src.case_num = tgt.case_num
    where tgt.row_hash is null;

end;
