"""
Editor:Hyean
E-mail:1067065568@qq.com
"""
import os

# 获取当前文件的绝对路径
dir = os.path.abspath(__file__)
# 获取项目目录路径
BASEDIR = os.path.dirname(os.path.dirname(dir))
# 获取配置文件的路径
conf_dir = os.path.join(BASEDIR, "conf")
# 获取Excel文件的路径
data_dir = os.path.join(BASEDIR, "data")
# 获取日志文件的路径
log_dir = os.path.join(BASEDIR, "log")
# 获取测试用例的路径
case_dir = os.path.join(BASEDIR, "testcases")
# 获取测试报告的路径
report_dir = os.path.join(BASEDIR, "report")