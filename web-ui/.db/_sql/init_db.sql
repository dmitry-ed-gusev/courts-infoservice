create table dm_court_cases (
    id             integer not null primary key autoincrement unique,
    court          varchar(200),
    court_alias    varchar(50),
    check_date     date,
    section_name   varchar(1000),
    order_num      int,
    case_num       varchar(255),
    hearing_time   varchar(50),
    hearing_place  varchar(255),
    case_info      varchar(10000),
    stage          varchar(1000),
    judge          varchar(255),
    hearing_result varchar(1000),
    decision_link  varchar(1000),
    case_link      varchar(1000),
    row_hash       varchar(100),
    load_dttm      datetime
);

create table dm_v_court_stats(
    court_alias varchar(50) not null unique,
    title       varchar(1000),
    total_rows  int,
    min_dt      date,
    max_dt      date
);
