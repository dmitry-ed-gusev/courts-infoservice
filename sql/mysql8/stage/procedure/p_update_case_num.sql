drop procedure if exists stage_p_update_case_num;

create procedure stage_p_update_case_num()
begin
    update stage_stg_court_cases stg
    set case_num = (select dm.case_num from dm_court_cases dm where dm.case_link = stg.case_link and dm.case_num is not null limit 1)
    where case_num is null and court_alias not in ('stav_mir');
end;
