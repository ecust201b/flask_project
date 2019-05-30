# -*- coding: utf-8 -*-
import logging


class log(object):
    def __init__(self, logPath, level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        handler = logging.FileHandler(logPath)
        handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s '
                                      '- %(process)d - %(thread)d - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, string):
        self.logger.info(string)

    def debug(self, string):
        self.logger.debug(string)

    def warning(self, string):
        self.logger.warning(string)

    def error(self, string):
        self.logger.error(string)




