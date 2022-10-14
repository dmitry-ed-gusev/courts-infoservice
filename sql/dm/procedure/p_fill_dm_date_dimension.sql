drop procedure if exists p_fill_dm_date_dimension;

create procedure p_fill_dm_date_dimension(in startdate date,in stopdate date)
begin
    declare currentdate date;
    set currentdate = startdate;
    while currentdate < stopdate do
        insert into dm_data_dimension values (
                        year(currentdate)*10000+month(currentdate)*100 + day(currentdate),
                        currentdate,
                        year(currentdate),
                        month(currentdate),
                        day(currentdate),
                        quarter(currentdate),
                        weekofyear(currentdate),
                        date_format(currentdate,'%W'),
                        date_format(currentdate,'%M'),
                        'f',
                        case dayofweek(currentdate) when 1 then 't' when 7 then 't' else 'f' end,
                        null);
        set currentdate = adddate(currentdate,interval 1 day);
    end while;
end;

delete from dm_data_dimension;
call p_fill_dm_date_dimension(date'2000-01-01', date'2050-01-01');
