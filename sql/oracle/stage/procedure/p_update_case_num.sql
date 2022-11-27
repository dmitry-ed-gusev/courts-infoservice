create or replace procedure courts_info.stage_p_update_case_num
as
begin
    update courts_info.stage_stg_court_cases stg
    set case_num = (select dm.case_num from courts_info.dm_court_cases dm where dm.case_link = stg.case_link and dm.case_num is not null and rownum=1)
    where case_num is null;
end;
