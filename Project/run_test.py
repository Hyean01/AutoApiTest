"""
Editor:Hyean
E-mail:1067065568@qq.com
"""

import unittest
import os
from lib.HTMLTestRunnerNew import HTMLTestRunner
from com import contant
# 创建测试套件
suite = unittest.TestSuite()

# 把用例加载到测试套件中
loader = unittest.TestLoader()
suite.addTest(loader.discover(contant.case_dir))

# 创建一个测试程序启动器
# 使用导入的HTMLTestRunnerNew去创建一个程序启动器，这样可以输出自定义的测试报告
report_path = os.path.join(contant.report_dir, "report.html")
with open(report_path, "wb") as f:
    runner = HTMLTestRunner(stream=f,
                            verbosity=2,
                            title='unittest report',
                            description='练习单元测试报告',
                            tester='hyean')

    # 用启动器运行测试套件
    runner.run(suite)
