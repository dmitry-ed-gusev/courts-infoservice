#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Utilities module.

    Created:  Gusev Dmitrii, 13.10.2022
    Modified:
"""

import logging
import threading

from courts.defaults import MSG_MODULE_ISNT_RUNNABLE

log = logging.getLogger(__name__)


def singleton(class_):
    """Simple singleton class decorator. Use it on the class level to make class Singleton."""

    instances = {}  # classes instances storage

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


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


if __name__ == "__main__":
    print(MSG_MODULE_ISNT_RUNNABLE)
