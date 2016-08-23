#!/usr/bin/env python
#-*- coding: utf8 -*-
import logging
import os
from time import strftime

class LoadDataHandler(logging.FileHandler):
    def __init__(self, path, file_name, mode):
        file_name = "%s.log" % (strftime("%Y%m%d%H%M%S"))
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs/%s' % (strftime("%Y%m%d")))
        super(LoadDataHandler, self).__init__("%s/%s" % (path, file_name), mode)
