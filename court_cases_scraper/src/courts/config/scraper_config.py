"""scrapper config"""

MAX_RETRIES = 20
RANGE_BACKWARD = 14
RANGE_FORWARD = 60
WORKERS_COUNT_1 = 15
WORKERS_COUNT_2 = 10
WORKERS_COUNT_3 = 5
WORKERS_COUNT_4 = 5
WORKERS_COUNT_5 = 5
WORKERS_COUNT_6 = 5
WORKERS_COUNT_7 = 5
WORKERS_COUNT_8 = 1

COMMIT_INTERVAL = 1000

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"

STAGE_TABLE = "stage_stg_court_cases"
STAGE_MAPPING_1 = [{"name": "court", "mapping": "court"},
                   {"name": "court_alias", "mapping": "court_alias"},
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "section_name", "mapping": "section_name"},
                   {"name": "order_num", "mapping": "col0"},
                   {"name": "case_num", "mapping": "col1"},
                   {"name": "hearing_time", "mapping": "col2"},
                   {"name": "hearing_place", "mapping": "col3"},
                   {"name": "case_info", "mapping": "col4"},
                   {"name": "judge", "mapping": "col5"},
                   {"name": "hearing_result", "mapping": "col6"},
                   {"name": "decision_link", "mapping": "col7_link"},
                   {"name": "case_link", "mapping": "col1_link"},
                   {"name": "load_dttm", "constant": "now()"}
                   ]

STAGE_MAPPING_2 = [{"name": "court", "mapping": "court"},
                   {"name": "court_alias", "mapping": "court_alias"},
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "section_name", "mapping": "col7"},
                   {"name": "order_num", "mapping": "order_num"},
                   {"name": "case_num", "mapping": "col0"},
                   {"name": "hearing_time", "mapping": "hearing_time"},
                   {"name": "hearing_place", "mapping": "col4"},
                   {"name": "stage", "mapping": "col5"},
                   {"name": "case_info", "mapping": "col1"},
                   {"name": "judge", "mapping": "col6"},
                   {"name": "hearing_result", "mapping": "col2"},
                   {"name": "case_link", "mapping": "col0_link"},
                   {"name": "load_dttm", "constant": "now()"}
                   ]

STAGE_MAPPING_3 = [{"name": "court", "mapping": "court"},
                   {"name": "court_alias", "mapping": "court_alias"},
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "section_name", "mapping": "section_name"},
                   {"name": "order_num", "mapping": "col0"},
                   {"name": "case_num", "mapping": "col1"},
                   {"name": "hearing_time", "mapping": "col2"},
                   {"name": "hearing_place", "mapping": "col4"},
                   {"name": "case_info", "mapping": "col5"},
                   {"name": "stage", "mapping": "col3"},
                   {"name": "judge", "mapping": "col6"},
                   {"name": "hearing_result", "mapping": "col7"},
                   {"name": "decision_link", "mapping": "col8_link"},
                   {"name": "case_link", "mapping": "col1_link"},
                   {"name": "load_dttm", "constant": "now()"}
                   ]

STAGE_MAPPING_4 = [{"name": "court", "mapping": "court"},
                   {"name": "court_alias", "mapping": "court_alias"},
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "section_name", "mapping": "section_name"},
                   {"name": "order_num", "mapping": "order_num"},
                   {"name": "case_num", "mapping": "case_num"},
                   {"name": "case_info", "mapping": "case_info"},
                   {"name": "stage", "mapping": "status"},
                   {"name": "case_link", "mapping": "case_link"},
                   {"name": "load_dttm", "constant": "now()"}
                   ]

STAGE_MAPPING_5 = [{"name": "court", "mapping": "court"},
                   {"name": "court_alias", "mapping": "court_alias"},
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "section_name", "mapping": "col6"},
                   {"name": "order_num", "mapping": "order_num"},
                   {"name": "case_num", "mapping": "col0"},
                   {"name": "hearing_time", "mapping": "hearing_time"},
                   {"name": "hearing_place", "mapping": "col3"},
                   {"name": "stage", "mapping": "col4"},
                   {"name": "case_info", "mapping": "col1"},
                   {"name": "judge", "mapping": "col5"},
                   {"name": "case_link", "mapping": "col0_link"},
                   {"name": "load_dttm", "constant": "now()"}
                   ]

STAGE_MAPPING_6 = [{"name": "court", "mapping": "court"},
                   {"name": "court_alias", "mapping": "court_alias"},
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "section_name", "mapping": "section_name"},
                   {"name": "order_num", "mapping": "col0"},
                   {"name": "case_num", "mapping": "col1"},
                   {"name": "hearing_time", "mapping": "col2"},
                   {"name": "hearing_place", "mapping": "col3"},
                   {"name": "case_info", "mapping": "col4"},
                   {"name": "judge", "mapping": "col5"},
                   {"name": "hearing_result", "mapping": "col6"},
                   {"name": "decision_link", "mapping": "col7_link"},
                   {"name": "case_link", "mapping": "col1_link"},
                   {"name": "load_dttm", "constant": "now()"}
                   ]

STAGE_MAPPING_7 = [{"name": "court", "mapping": "court"},
                   {"name": "court_alias", "mapping": "court_alias"},
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "section_name", "mapping": "section_name"},
                   {"name": "order_num", "mapping": "order_num"},
                   {"name": "case_num", "mapping": "col3"},
                   {"name": "hearing_time", "mapping": "col8"},
                   {"name": "hearing_place", "mapping": "col9"},
                   {"name": "case_info", "mapping": "case_info"},
                   {"name": "judge", "mapping": "judge"},
                   {"name": "load_dttm", "constant": "now()"}
                   ]

STAGE_MAPPING_8 = [{"name": "court", "mapping": "court"},
                   {"name": "court_alias", "mapping": "court_alias"},
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "case_num", "mapping": "case_num"},
                   {"name": "hearing_time", "mapping": "hearing_time"},
                   {"name": "hearing_place", "mapping": "hearing_place"},
                   {"name": "case_info", "mapping": "case_info"},
                   {"name": "case_link", "mapping": "case_link"},
                   {"name": "judge", "mapping": "judge"},
                   {"name": "load_dttm", "constant": "now()"}
                   ]
