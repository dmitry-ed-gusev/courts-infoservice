SQL_SCRIPTS_DIR = "../../../../sql"
INIT_FILES = [
    "stage/table/stg_court_cases.sql",
    "stage/procedure/p_update_court_cases_row_hash.sql",
    "dm/table/court_cases.sql",
    "dm/table/court_cases_scrap_log.sql",
    "dm/table/court_scrap_config.sql",
    "dm/table/telegram_bot_subscribtions.sql",
    "dm/view/v_courts_to_refresh.sql",
    "dm/procedure/p_load_court_cases.sql",
    "dm/data/court_scrap_config.sql",
]

TEST_DB_QUERY = "select count(*) from dm_court_cases"
