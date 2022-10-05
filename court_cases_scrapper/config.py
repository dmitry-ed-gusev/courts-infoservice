"""scrapper config"""

MYSQL_CONNECT = {
    "host": "localhost",
    "port": 3306,
    "user": "usr_etl",
    "passwd": "password"
}

OUTPUT_DIR = "../output"
RANGE_BACKWARD = 7
RANGE_FORWARD = 60
WORKERS_COUNT_1 = 15
WORKERS_COUNT_2 = 4

COMMIT_INTERVAL = 1000

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"

STAGE_TABLE = "stage.stg_court_cases"
STAGE_MAPPING_1 = [{"name": "court", "mapping": "court"},
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
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "section_name", "mapping": "col7"},
                   {"name": "order_num", "mapping": "order_num"},
                   {"name": "case_num", "mapping": "col0"},
                   {"name": "hearing_time", "mapping": "hearing_time"},
                   {"name": "hearing_place", "mapping": "col4"},
                   {"name": "case_info", "mapping": "col1"},
                   {"name": "judge", "mapping": "col6"},
                   {"name": "hearing_result", "mapping": "col2"},
                   {"name": "case_link", "mapping": "col0_link"},
                   {"name": "stage", "mapping": "col5"},
                   {"name": "load_dttm", "constant": "now()"}
                   ]
