#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HTTP client for the scraping.

    Useful resources:
        - (download file) https://stackoverflow.com/questions/7243750/download-file-from-web-in-python-3
        - (pypi - urllib3) https://pypi.org/project/urllib3/
        - (urllib3 - docs) https://urllib3.readthedocs.io/en/stable/
        - (docs from python) https://docs.python.org/3/howto/urllib2.html
        - (fake User Agent) https://github.com/hellysmile/fake-useragent
        - (HTTP status codes) https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

    Created:  Dmitrii Gusev, 13.10.2022
    Modified:
"""

import logging
import shutil
import requests
from pathlib import Path
from requests import Response
from requests.adapters import HTTPAdapter, Retry
from fake_useragent import UserAgent
from typing import Dict, Tuple, List, AnyStr, Any

from pyutilities.utils.utilities import threadsafe_function
from pyutilities.exception import PyUtilitiesException
from pyutilities.defaults import MSG_MODULE_ISNT_RUNNABLE

# init module logger
log = logging.getLogger(__name__)
log.debug(f"Logging for module {__name__} is configured.")

HTTP_DEFAULT_TIMEOUT = 20  # default HTTP requests timeout (seconds)
HTTP_DEFAULT_BACKOFF = 1  # default back off factor (it is better to not touch this value!)
HTTP_DEFAUT_RETRIES = 4  # default retries num for HTTP requests (+1 for the original request!)


class TimeoutHTTPAdapter(HTTPAdapter):
    """Timeout adapter based on the HTTPAdapter."""

    def __init__(self, *args, **kwargs):
        log.debug("Initializing TimeoutHTTPAdapter.")
        self.timeout = HTTP_DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class WebClient():
    """Simple WebClient class (class based on the [requests] module).
        If user_agent specified - use it, if not - generate it randomly.
    """

    # class (not instance!) variable - when we create multiple instances of this class - we need
    # to update the user agents data only once (for all instances)
    __user_agent_info_updated: bool = False

    # class-level variable for storing the fake User Agent info
    # todo: use fake User Agent without cache - see docs -> UserAgent(cache=False)
    __ua: UserAgent = UserAgent()

    @threadsafe_function
    def __update_user_agent_info(self):
        if not WebClient.__user_agent_info_updated:
            log.info("Fake User Agent -> cached info updating...")
            WebClient.__ua.update()
            WebClient.__user_agent_info_updated = True

    def __init__(self, headers: Dict[str, str] = None, cookies: Dict[str, str] = None, auth=None,
                 user_agent: str = "", allow_redirects: bool = True, redirects_count: int = 0,
                 timeout: int = HTTP_DEFAULT_TIMEOUT, retries: int = HTTP_DEFAUT_RETRIES,
                 update_user_agents_info: bool = False) -> None:
        log.debug("Initializing WebClient() instance.")

        if update_user_agents_info:
            self.__update_user_agent_info()

        # init internal state - session + some other parameters
        self.__session = requests.Session()
        self.__allow_redirects = allow_redirects

        # setup requests hooks - raise HTTPError for error HTTP status codes 4xx, 5xx, except
        # the statuses specified in status_forcelist parameter of the Retry strategy
        def assert_status_hook(response, *args, **kwargs): response.raise_for_status()
        self.__session.hooks["response"] = [assert_status_hook]

        # setup retries strategy for the session - see mounting it below
        retry_strategy = Retry(  # create retry strategy
            total=retries,  # total # of retries, see HTTP codes that will be retried -> status_forcelist
            backoff_factor=HTTP_DEFAULT_BACKOFF,  # backoff: 1 -> [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256] sec

            # for these HTTP error status codes will be applied the Retry startegy, in case the retry limit
            # will be reached without success - TooMaxRetries(?) issue will be raised, otherwise the
            # success status/response (1xx, 2xx, 3xx) will be returned.
            status_forcelist=[429, 500, 502, 503, 504],  # statuses for retry

            # use 'allowed_methods' instead of 'method_whitelist' (deprecated and will be removed in v2.0)
            allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "TRACE", "PATCH"],
        )

        # create TimeoutHTTPAdapter (based on HTTPAdapter) and mount it to prefixes
        adapter = TimeoutHTTPAdapter(timeout=timeout, max_retries=retry_strategy)
        self.__session.mount("https://", adapter)  # mount to HTTPS (timeout+retries)
        self.__session.mount("http://", adapter)  # mount to HTTP (timeout+retries)

        if headers and len(headers) > 0:  # add headers
            self.__session.headers.update(headers)
            log.debug("Headers are not empty, adding to the HTTP session.")
        if cookies and len(cookies) > 0:  # add cookies
            self.__session.cookies.update(cookies)
            log.debug("Cookies are not empty, adding to the HTTP session.")
        if redirects_count > 0:  # add redirects count
            self.__session.max_redirects = redirects_count
        if not user_agent:  # set User Agent header
            user_agent = WebClient.__ua.random
        self.__session.headers.update({"user-agent": user_agent})  # header may be "User-Agent"
        if auth:  # add authorization to session
            self.__session.auth = auth

        log.debug("WebClient() instance initialized OK. Configuration:\n"
                  f"Headers: {self.__session.headers}\n"
                  f"Cookies: {self.__session.cookies}\n")

    def get(self, url: str, params: Dict[str, str] = None) -> Response:
        """Perform HTTP GET request with retry (if necessary).
        :param params: request parameters -> will be added to the URL
        """
        log.debug(f"WebClient.get(): {url}. Params: {params}.")
        return self.__session.get(url, params=params, allow_redirects=self.__allow_redirects)

    def post(self, url: str, data: Dict[str, str] = None, params: Dict[str, str] = None) -> Response:
        """Perform HTTP POST request with retry (if necessary).
        :param data: request data -> will be added to the request body (HTTP POST)
        :param params: request parameters -> will be added to the URL
        """
        log.debug(f"WebClient.post(): {url}. Params: {params}. Data: {data}.")
        return self.__session.post(url, data=data, params=params, allow_redirects=self.__allow_redirects)

    def put(self, url: str, data: Dict[str, str] = None, params: Dict[str, str] = None) -> Response:
        """Perform HTTP PUT request with retry (if necessary).
        :param data: request data -> will be added to the request body (like HTTP POST)
        :param params: request parameters -> will be added to the URL
        """
        log.debug(f"WebClient.put(): {url}. Params: {params}. Data: {data}.")
        return self.__session.put(url, data=data, params=params, allow_redirects=self.__allow_redirects)

    def delete(self, url: str, data: Dict[str, str] = None, params: Dict[str, str] = None) -> Response:
        """Perform HTTP DELETE request with retry (if necessary).
        :param data: request data -> will be added to the request body (like HTTP POST)
        :param params: request parameters -> will be added to the URL
        """
        log.debug(f"WebClient.delete(): {url}. Params: {params}. Data: {data}.")
        return self.__session.delete(url, data=data, params=params, allow_redirects=self.__allow_redirects)

    def head(self, url: str, data: Dict[str, str] = None, params: Dict[str, str] = None) -> Response:
        """Perform HTTP HEAD request with retry (if necessary).
        :param data: request data -> will be added to the request body (like HTTP POST)
        :param params: request parameters -> will be added to the URL
        """
        log.debug(f"WebClient.head(): {url}. Params: {params}. Data: {data}.")
        return self.__session.head(url, data=data, params=params, allow_redirects=self.__allow_redirects)

    def options(self, url: str, data: Dict[str, str] = None, params: Dict[str, str] = None) -> Response:
        """Perform HTTP OPTIONS request with retry (if necessary).
        :param data: request data -> will be added to the request body (like HTTP POST)
        :param params: request parameters -> will be added to the URL
        """
        log.debug(f"WebClient.options(): {url}. Params: {params}. Data: {data}.")
        return self.__session.options(url, data=data, params=params, allow_redirects=self.__allow_redirects)

    # def get_text_2_files(self, urls: Dict[str, str], dir: str, allow_redicrects: bool,
    #                      fail_on_error: bool) -> None:
    #     log.debug(f'get_text_2_files(): saving multiple urls to dir: {dir}.')

    #     if not urls:
    #         raise ScraperException('Provided empty URLs dictionary!')

    #     if not dir:
    #         raise ScraperException('Provided empty dir for saving urls!')

    #     os.makedirs(dir, exist_ok=True)  # if all is OK - create dir for the ship data

    #     # check existence of files with additional info and request if missing
    #     for key in urls:
    #         file = dir + "/" + key + ".html"
    #         if not Path(file).exists():  # if file doesn't exist - request it
    #             # HTTP GET request + save to file
    #             self.get_text_2_file(urls[key], file, allow_redicrects, fail_on_error)


# def http_get_request(url: str, request_params: dict, retry_count: int = 0) -> str:
#     """Perform one HTTP GET request with the specified parameters.
#         Module is based on the urllib library.
#     :param url: url to request
#     :param request_params: reuqest parameters (will be added to the request URL - for the GET request)
#     :param retry_count: number of retries. 0 -> no retries (one request), less than 0 -> no requests at all,
#                         greater than 0 -> (retry_count + 1) - such number of requests (one original 
#                         request + # of retries)
#     :return: HTML output with data (text/str)
#     """

#     if not url or len(url.strip()) == 0:  # fail-fast - empty URL
#         raise ValueError("Provided empty URL, can't perform the request!")

#     # prepare/encode the request data
#     req = request.Request(url)  # this will make the method "GET" (without data)
#     context = ssl.SSLContext()  # new SSLContext -> to bypass security certificate check

#     # perform the request itself (with necessary # of retries)
#     tries_counter: int = 0
#     response_ok: bool = False
#     my_response = None
#     while tries_counter <= retry_count and not response_ok:  # perform specified number of requests
#         log.debug(f"HTTP GET: URL: {url}, data: {request_params}, try #{tries_counter}/{retry_count}.")
#         try:
#             my_response = request.urlopen(req, context=context, timeout=TIMEOUT_URLLIB_URLOPEN)
#             response_ok = True  # after successfully done request we should stop requests
#         except (TimeoutError, error.URLError) as e:
#             log.error(f"We got error -> URL: {url}, data: {request_params}, "
#                       f"try: #{tries_counter}/{retry_count}, "
#                       f"error: {e}.")
#         tries_counter += 1  # increment tries counter

#     if my_response:
#         return my_response.read().decode(config.encoding)  # read response and perform decode

#     return ""  # return empty string if got an empty answer


# def http_post_request(url: str, request_params: dict, retry_count: int = 0) -> str:
#     """Perform one HTTP POST request with the specified parameters.
#         Module is based on the urllib library.
#     :param url: url to request
#     :param request_params: reuqest parameters (will be added to the body of the POST request)
#     :param retry_count: number of retries. 0 -> no retries (one request), less than 0 -> no requests at all,
#                         greater than 0 -> (retry_count + 1) - such number of requests (one original 
#                         request + # of retries)
#     :return: HTML output with data (text/str)
#     """

#     if not url or len(url.strip()) == 0:  # fail-fast - empty URL
#         raise ValueError("Provided empty URL, can't perform the request!")

#     # prepare/encode the request data
#     data = parse.urlencode(request_params).encode(config.encoding)  # perform encoding of request params
#     req = request.Request(url, data=data)  # this will make the method "POST" request (with data load)
#     context = ssl.SSLContext()  # new SSLContext -> to bypass security certificate check

#     # perform the request itself (with necessary # of retries)
#     tries_counter: int = 0
#     response_ok: bool = False
#     my_response = None
#     while tries_counter <= retry_count and not response_ok:  # perform specified number of requests
#         log.debug(f"HTTP POST: URL: {url}, data: {request_params}, try #{tries_counter}/{retry_count}.")
#         try:
#             my_response = request.urlopen(req, context=context, timeout=TIMEOUT_URLLIB_URLOPEN)
#             response_ok = True  # after successfully done request we should stop requests
#         except (TimeoutError, error.URLError) as e:
#             log.error(f"We got error -> URL: {url}, data: {request_params}, "
#                       f"try: #{tries_counter}/{retry_count}, "
#                       f"error: {e}.")
#         tries_counter += 1  # increment tries counter

#     if my_response:
#         return my_response.read().decode(config.encoding)  # read response and perform decode

#     return ""  # return empty string if got an empty answer


# def perform_file_download_over_http(url: str, target_dir: str, target_file: str = None) -> str:
#     """Downloads file via HTTP protocol.
#     :param url: URL for file download, shouldn't be empty.
#     :param target_dir: local dir to save file, if empty - save to the current dir
#     :param target_file: local file name to save, if empty - file name will be derived from URL
#     :return: path to locally saved file, that was downloaded
#     """
#     log.debug(
#         f"perform_file_download_over_http(): downloading link: {url}, target dir: {target_dir}, "
#         f"target_file: {target_file}."
#     )

#     if not url or len(url.strip()) == 0:  # fail-fast check for provided url
#         raise ValueError("Provided empty URL!")

#     # check target dir name - if not empty we will create all missing dirs in the path
#     if target_dir is not None and len(target_dir.strip()) > 0:
#         Path(target_dir).mkdir(parents=True, exist_ok=True)  # create necessary parent dirs in path
#         log.debug(f"Created all missing dirs in path: {target_dir}")
#     else:
#         log.debug("Provided empty target dir - file will be saved in the current directory.")

#     # pick a target file name
#     local_file_name: str = ''
#     if target_file is None or len(target_file.strip()) == 0:
#         local_file_name = Path(url).name
#     else:
#         local_file_name = target_file
#     log.debug(f"Target file name: {local_file_name}")

#     # construct the full local target path
#     local_path: str = target_dir + "/" + local_file_name
#     log.debug(f"Generated local full path: {local_path}")

#     # download the file from the provided `url` and save it locally under certain `file_name`:
#     with request.urlopen(url) as my_response, open(local_path, "wb") as out_file:
#         shutil.copyfileobj(my_response, out_file)
#     log.info(f"Downloaded file: {url} and put here: {local_path}")

#     return local_path


def process_url(url: str, postfix: str = '', format_values: Tuple[str] = None) -> str:
    log.debug(f'Processing URL [{url}] with postfix [{postfix}] and format values [{format_values}].')

    if not url:
        raise ScraperException('Provided empty URL for processing!')

    processed_url: str = url
    if postfix:  # if postfix - add it to the URL string
        if not processed_url.endswith('/'):
            processed_url += '/'
        processed_url += postfix

    if format_values:  # if there are values - format URL string with them
        processed_url = processed_url.format(*format_values)

    return processed_url


def process_urls(urls: Dict[str, str], postfix: str = '', format_values: Tuple[str] = None) -> Dict[str, str]:
    log.debug('Processing urls dictionary.')

    if not urls:
        raise ScraperException('Provided empty URLs dictionary for processing!')

    processed: Dict[str, str] = dict()
    for key in urls:
        processed[key] = process_url(urls[key], postfix, format_values)

    return processed


if __name__ == "__main__":
    print(MSG_MODULE_ISNT_RUNNABLE)