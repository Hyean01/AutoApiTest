"""
Editor:Hyean
E-mail:1067065568@qq.com
"""
import logging
import os
import colorlog
from com import contant
from logging.handlers import RotatingFileHandler


class MyLog(object):
    @staticmethod
    def create_log():
        # 创建日志收集器并设置收集的日志等级
        my_log = logging.getLogger()
        my_log.setLevel("DEBUG")
        # 创建日志输出渠道并设置输出等级
        # 输出到控制台
        out_ctrl = logging.StreamHandler()
        out_ctrl.setLevel("DEBUG")
        # 输出到文件
        out_file = logging.FileHandler(filename=os.path.join(contant.log_dir, "log.txt"))
        out_file.setLevel("DEBUG")
        # 设置文件日志的轮转
        out_file = RotatingFileHandler(filename=os.path.join(contant.log_dir, "log.txt"), encoding="utf8",
                                       maxBytes=100*1024*1024, backupCount=7)
        # out_file = logging.handlers.TimedRotatingFileHandler(filename=os.path.join(contant.log_dir, "log.txt"),
        #                                                      encoding="utf8", when="D", interval=1, backupCount=7)
        # 把日志收集器和输出渠道绑定
        my_log.addHandler(out_ctrl)
        my_log.addHandler(out_file)
        # 设置日志输出格式
        log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'black',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
        # Formatter_file = logging.Formatter(('%(asctime)s - [%(filename)s-->line:%(lineno)d] - %(levelname)s: %('
        #                                     'message)s'))
        Formatter_file = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] [line:%(lineno)d]: %(message)s')
        Formatter_ctrl = colorlog.ColoredFormatter('%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
                                                   log_colors=log_colors_config)
        out_file.setFormatter(Formatter_file)
        out_ctrl.setFormatter(Formatter_ctrl)
        return my_log


# 创建一个日志收集器
logger = MyLog.create_log()
