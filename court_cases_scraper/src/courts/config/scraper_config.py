#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Courts Scraper/Parser config. In case cache dir [.courts_scraper] exists in the current 
    dir - use it, otherwise cache dir will be placed/used in the user home dir.

    Created:  Gusev Dmitrii, 13.10.2022
    Modified:
"""
import threading
import os
import json
from pathlib import Path
from dataclasses import asdict
from dataclasses import dataclass
from courts.utils.utilities import singleton
from courts.defaults import MSG_MODULE_ISNT_RUNNABLE

# common constants/defaults
CACHE_DIR_NAME: str = ".courts_scraper"  # cache dir name


def threadsafe_function(fn):
    """Decorator making sure that the decorated function is thread safe."""
    lock = threading.Lock()

    def new(*args, **kwargs):
        lock.acquire()
        try:
            r = fn(*args, **kwargs)
        # except Exception as e:
        #     raise e
        finally:
            lock.release()
        return r

    return new

# if cache is in curr dir (exists and is dir) - use it, otherwise - use the user
# home directory (mostly suitable for development, in most cases user home dir will be used)
def get_cache_dir(base_name: str) -> str:
    if not base_name:
        raise ValueError("Empty base name!")

    if Path(base_name).exists() and Path(base_name).is_dir():
        return base_name
    else:  # cache dir not exists or is not a dir
        return str(Path.home()) + '/' + base_name


@singleton
@dataclass(frozen=True)
class Config():
    # -- basic directories settings
    cache_dir: str = get_cache_dir(CACHE_DIR_NAME)
    log_dir: str = cache_dir + "/logs"  # log directory
    work_dir: str = str(os.getcwd())  # current working dir
    user_dir: str = str(Path.home())  # user directory

    encoding: str = "utf-8"  # general encoding

    # post-init method - create necessary sub-dir(s)
    #   - logging dir
    def __post_init__(self):
        os.makedirs(str(self.log_dir), exist_ok=True)

    def __repr__(self):
        return "Config: " + json.dumps(asdict(self), indent=4)


@singleton
class CookiesArbitrary:
    """class to preserve current cookie between worker sessions"""
    __cookies: str = ""
    __user_agent: str = ""

    @property
    @threadsafe_function
    def cookies(self) -> str:
        return self.__cookies

    @cookies.setter
    @threadsafe_function
    def cookies(self, value: str):
        self.__cookies = value

    @property
    @threadsafe_function
    def user_agent(self) -> str:
        return self.__user_agent

    @cookies.setter
    @threadsafe_function
    def user_agent(self, value: str):
        self.__user_agent = value


MAX_RETRIES = 20
RANGE_BACKWARD = 14
RANGE_FORWARD = 45
WORKERS_COUNT_1 = 4
WORKERS_COUNT_2 = 5
WORKERS_COUNT_3 = 1
WORKERS_COUNT_4 = 3
WORKERS_COUNT_5 = 5
WORKERS_COUNT_6 = 3
WORKERS_COUNT_7 = 2
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
                   ]

STAGE_MAPPING_8 = [{"name": "court", "mapping": "court"},
                   {"name": "court_alias", "mapping": "court_alias"},
                   {"name": "check_date", "mapping": "check_date"},
                   {"name": "case_num", "mapping": "case_num"},
                   {"name": "stage", "mapping": "stage"},
                   {"name": "hearing_time", "mapping": "hearing_time"},
                   {"name": "hearing_place", "mapping": "hearing_place"},
                   {"name": "case_info", "mapping": "case_info"},
                   {"name": "case_link", "mapping": "case_link"},
                   {"name": "judge", "mapping": "judge"},
                   ]

if __name__ == "__main__":
    print(MSG_MODULE_ISNT_RUNNABLE)
