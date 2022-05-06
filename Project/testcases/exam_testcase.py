"""
Editor:Hyean
E-mail:1067065568@qq.com
"""

import unittest
import os
import requests
from lib.ddt import ddt, data
from com.readexcel import ReadExcel
from com import contant
from com.mylog import logger

'''
测试用例类：自己定义的类只要是继承于unittest.TestCase，就是一个测试用例类
测试用例：测试用例类中，以test开头的方法就是一条测试用例
测试用例是否执行通过的评判标准：断言是否异常

测试用例书写步骤：
1. 准备用例数据（用例的参数、预期结果、数据库执行的SQL）
2. 执行功能函数，获取实际结果
3. 比对预期结果和实际结果，进行断言
'''
file_path = os.path.join(contant.data_dir, "cases.xlsx")
@ddt
class LoginTestCases(unittest.TestCase):
    # 创建读取excel的对象，调用封装好的方法读取excel数据，作为要传入的测试用例数据
    excel = ReadExcel(file_path, "login") 
    cases = excel.read_data()

    @data(*cases)
    def test_login(self, case):
        # 1. 准备用例数据，预期结果
        logger.info("开始执行第{}条用例:{}，测试数据为：{},预期结果为{}"
                    .format(case["case_id"], case["title"], case["data"], case["expect"]))
        case_data = eval(case["data"])
        case_expected = eval(case["expect"])
        case_id = case["case_id"]
        # 2. 调用功能函数，获取实际执行结果
        result = requests.post(url="", json=case_data, headers={})
        # 3. 断言
        try:
            self.assertEqual(case_expected, result)
        except AssertionError as e:
            # 用例执行未通过
            self.excel.write_data(row=case_id+1, column=5, value='未通过')
            logger.info("用例{}:{} 执行未通过".format(case_id, case["title"]))
            logger.error(e)
            raise e
        else:
            # 用例执行通过
            self.excel.write_data(row=case_id+1, column=5, value="通过")
            logger.info("用例{}:{} 执行通过".format(case_id, case["title"]))


@ddt
class RegisterCases(unittest.TestCase):
    excel = ReadExcel(file_path, "register")
    cases = excel.read_data()

    @data(*cases)
    def test_register(self, case):
        # 准备用例数据，预期结果
        logger.info("开始执行第{}条用例:{}，测试数据为：{},预期结果为{}"
                    .format(case["case_id"], case["title"], case["data"], case["expect"]))
        case_data = eval(case["data"])
        case_expected = eval(case["expect"])
        case_id = case["case_id"]
        # 调用功能函数，获取实际结果
        case_result = register(*case_data)
        # 断言预期结果和实际结果
        try:
            self.assertEqual(case_expected, case_result)
        except AssertionError as e:
            self.excel.write_data(row=case_id+1, column=5, value="未通过")
            logger.info("用例{}:{} 执行未通过".format(case_id+1, case["title"]))
            logger.error(e)
            raise e
        else:
            self.excel.write_data(row=case_id+1, column=5, value="通过")
            logger.info("用例{}:{} 执行通过".format(case_id + 1, case["title"]))


# 如果直接运行这个文件，就是使用unittest.main函数执行文件测试用例
if __name__ == '__main__':
    unittest.main()
