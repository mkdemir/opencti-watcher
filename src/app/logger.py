import logging
import os
from src.config import Config
from datetime import datetime
import sys
from logging.handlers import RotatingFileHandler
import glob


class Logger:
    """
    Used for logging
    """

    def __init__(self, log_type):
        """
        Constructor function
        :param log_type: type of log(database or webcrawler vs.)
        """
        self.log_type = log_type
        self.log_dir = Config.LOG_DIR
        date = datetime.today().strftime('%Y-%m-%d')
        self.log_path = self.log_dir + 'opencti' + "-" + date + '.log'
        self.log_format = Config.LOG_FORMAT
        # self.close_log()
        self.logger = self.get_log_config()
        self.remove_log()

    def log(self, level, msg):
        """
        Log info/warning/error message in log file.
        :param level: level of the log(info, warning, error)
        :param msg: message
        """
        if self.logger is not None:
            if level == logging.INFO:
                self.logger.info("{}".format(msg))
            elif level == logging.WARNING:
                self.logger.warning("{}".format(msg))
            else:
                self.logger.error("{}".format(msg))

    def get_log_config(self):
        """
        Configuration for logging.
        """
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # create logger
        logger = logging.getLogger(self.log_type)
        # create handler
        file_path = os.path.abspath(self.log_path)
        handler = logging.FileHandler(file_path, encoding="UTF-8")
        # handler = RotatingFileHandler(file_path, maxBytes=5*1024*1024, backupCount=10, encoding="UTF-8") #FIXME - Burayı aç
        # create formatter
        formatter = logging.Formatter(self.log_format)
        # set Formatter
        handler.setFormatter(formatter)
        # add handler
        logger.addHandler(handler)
        # set level
        logger.setLevel(logging.INFO)

        return logger

    # def close_log(self):
    #     """
    #     Remove all logger.
    #     """
    #     try:
    #         logger = logging.getLogger(self.log_type)
    #         while logger.hasHandlers():
    #             logger.removeHandler(logger.handlers[0])
    #     except Exception as e:
    #         self.logger.log(logging.ERROR, e)

    def remove_log(self):
        """
        Remove old log
        """
        try:
            log_files = glob.glob('../logs/*.log')
            log_files_list = [(f, os.path.getctime(f)) for f in log_files]
            log_files_list = sorted(log_files_list, key=lambda x: x[1])
            for i in range(len(log_files_list) - 2):
                os.remove(log_files_list[i][0])
        except Exception as e:
            self.log(logging.INFO, e)
