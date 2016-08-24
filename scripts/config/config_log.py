#!/usr/bin/python
# -*- coding: utf8 -*-
import logging
import logging.config
import os

# debugging options
import sys
import ipdb
import traceback
from time import strftime

LOGGING_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/logging.conf')
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs/%s' % (strftime("%Y%m%d")))

def info(type, value, tb):
    traceback.print_exception(type, value, tb)
    print
    ipdb.pm()

sys.excepthook = info


# exceptionObj
def displayException(ex):
    template = "An exception of type {0} occured. Arguments:\n{1!r}"
    message = template.format(type(ex).__name__, ex.args)
    logging.exception("Unexpected error: %s", message)
# End debugging options


class GetConfig:
    @staticmethod
    def config_log():
        if not os.path.exists(LOG_DIR):
            logging.info("Dir: '%s' does not exist, going to creat it", LOG_DIR)
            os.makedirs(LOG_DIR)
        logging.config.fileConfig(LOGGING_CONFIG_FILE)
