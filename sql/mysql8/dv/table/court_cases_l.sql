create table if not exists dv_court_cases_l (
court_case_l_id int not null,
court_case_id int not null,
check_date date not null,
order_num int not null,
load_dttm datetime default now(),
PRIMARY KEY (court_case_l_id),
UNIQUE KEY (court_case_id, check_date, order_num)
);
