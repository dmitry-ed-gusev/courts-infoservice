insert into courts_info.dm_date_dimension
select cast(to_char(db_date, 'yyyymmdd') as int) as id,
	db_date,
	extract(year from db_date) as year,
	extract(month from db_date) as month,
	extract(day from db_date) as day,
	cast(to_char(db_date, 'Q') as int) as quarter,
	cast(to_char(db_date, 'W') as int) as week,
	to_char(db_date, 'Day') as day_name,
	to_char(db_date, 'Month') as month_name,
	'f' as holiday_flag,
	case when cast(to_char(db_date, 'D') as int) in (6,7) then 't' else 'f' end as weekend_flag,
	null
from (
	select date'2010-01-01' + level as db_date
	from dual
	connect by level < (date'2040-01-01' - date'2010-01-01')
) x;