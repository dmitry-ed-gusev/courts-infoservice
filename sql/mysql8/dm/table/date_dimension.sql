drop table if exists dm_date_dimension;

create table dm_data_dimension (
        id                      integer primary key,  -- year*10000+month*100+day
        db_date                 date not null,
        year                    integer not null,
        month                   integer not null, -- 1 to 12
        day                     integer not null, -- 1 to 31
        quarter                 integer not null, -- 1 to 4
        week                    integer not null, -- 1 to 52/53
        day_name                varchar(9) not null, -- 'monday', 'tuesday'...
        month_name              varchar(9) not null, -- 'january', 'february'...
        holiday_flag            char(1) default 'f' check (holiday_flag in ('t', 'f')),
        weekend_flag            char(1) default 'f' check (weekend_flag in ('t', 'f')),
        event                   varchar(50),
        unique td_ymd_idx (year,month,day),
        unique td_dbdate_idx (db_date)
);
