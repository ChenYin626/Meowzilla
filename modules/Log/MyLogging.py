# -*- coding: utf-8 -*-
"""
@Author         ：Cat
@Date           : 2022年 11月 06日
@Introduction   ：A Lazy Cat
"""
import logging
import os.path

import time


class MyLogging:
    logger = None

    # 初始化日志
    def __init__(self, name="app"):
        self.logPath = 'logs/'
        self.logName = name+".log"
        self.logFile = self.logPath + self.logName
        strf_time = time.strftime("%Y-%m-%d", time.localtime())
        self.logFile = self.logFile.replace(".log", "-" + strf_time + ".log")
        MyLogging.logger = logging.getLogger(name)
        # 创建日志器对象
        # self.logger = logging.getLogger(__name__)

        # 设置logger可输出日志级别范围
        MyLogging.logger.setLevel(logging.DEBUG)

        # 添加控制台handler，用于输出日志到控制台
        self.console_handler = logging.StreamHandler()
        # 添加日志文件handler，用于输出日志到文件中
        self.file_handler = logging.FileHandler(filename=self.logFile, mode="a", encoding='UTF-8')

        # 将handler添加到日志器中
        MyLogging.logger.addHandler(self.console_handler)
        MyLogging.logger.addHandler(self.file_handler)

        # 设置格式并赋予handler
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        self.console_handler.setFormatter(formatter)
        self.file_handler.setFormatter(formatter)

    @staticmethod
    def write_debug_logger(content):
        MyLogging.logger.debug(content)

    @staticmethod
    def write_error_logger(content):
        MyLogging.logger.error(content)

    @staticmethod
    def write_info_logger(content):
        MyLogging.logger.info(content)

    @staticmethod
    def write_warning_logger(content):
        MyLogging.logger.warning(content)

    @staticmethod
    def write_critical_logger(content):
        MyLogging.logger.critical(content)
