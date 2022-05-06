"""
Editor:Hyean
E-mail:1067065568@qq.com
"""
import unittest
import os
from com.readexcel import ReadExcel
from com.contant import data_dir, conf_dir
from lib.ddt import ddt, data
from configparser import ConfigParser
from com.mylog import logger
from com.handlerequest import HandleRequest

# Excel用例数据的路径
file_path = os.path.join(data_dir, "future_api_data.xlsx")
# 配置文件的路径
conf_path = os.path.join(conf_dir, "conf.ini")
# 使用ddt数据驱动，把读取出来的用例数据转化为一条条用例，传到用例方法中
@ddt
class LoginTest(unittest.TestCase):
    # 读取Excel用例数据
    excel = ReadExcel(file_name=file_path, sheet_name="login")
    cases = excel.read_data()
    conf = ConfigParser()
    conf.read(filenames=conf_path, encoding="utf8")
    http = HandleRequest()

    @classmethod
    def setUpClass(cls) -> None:
        logger.info("********************开始执行登录接口测试用例********************")

    @data(*cases)
    def test_login(self, case):
        # 准备用例数据
        url = self.conf.get(section="env", option="test_url") + case["url"]
        case_data = eval(case["data"])
        case_expected = eval(case["expected"])
        case_id = case["case_id"]
        headers = eval(self.conf.get(section="headers", option="header"))
        headers["Content-Type"] = "application/json"
        # 发送请求
        logger.info("开始执行用例[{}]，用例参数为:{}".format(case["title"], case_data))
        result = self.http.send(url=url, method=case["method"], headers=headers, data=case_data)
        # 断言结果
        # print(result, result.json())
        try:
            self.assertEqual(case_expected["code"], result.json()["code"])
            self.assertEqual(case_expected["msg"], result.json()["msg"])
        except AssertionError as e:
            self.excel.write_data(row=case_id+1, column=self.conf.getint(section="excel", option="column"), value="未通过")
            print("用例[{}]——>预期结果是:{}，\n实际结果是:{}".format(case["title"], case_expected, result.json()))
            logger.info("用例[{}]执行失败".format(case["title"]))
            logger.info("预期结果——>{}".format(case_expected))
            logger.info("实际结果——>{}".format(result.json()))
            raise e
        else:
            self.excel.write_data(row=case_id+1, column=self.conf.getint(section="excel", option="column"), value="通过")
            logger.info("用例[{}]执行成功".format(case["title"]))
            logger.info("实际运行结果是{}".format(result.json()))
