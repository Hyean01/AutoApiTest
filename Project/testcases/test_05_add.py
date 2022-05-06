"""
Editor:Hyean
E-mail:1067065568@qq.com
"""
import unittest
import os
import random
import jsonpath
from configparser import ConfigParser
from com.contant import conf_dir, data_dir
from com.readexcel import ReadExcel
from lib.ddt import ddt, data
from com.mylog import logger
from com.handlerequest import HandleRequest

conf_path = os.path.join(conf_dir, "conf.ini")
@ddt
class AddTest(unittest.TestCase):
    conf = ConfigParser()
    conf.read(filenames=conf_path, encoding="utf8")
    data_path = os.path.join(data_dir, conf.get("excel", "name"))
    excel = ReadExcel(file_name=data_path, sheet_name="project_add")
    cases = excel.read_data()
    http = HandleRequest()

    @staticmethod
    def random_phone():
        """定义一个静态方法，生成注册所需要的随机手机号"""
        phone = "185"
        for i in range(8):
            phone += str(random.randint(0, 9))
        return phone

    @classmethod
    def setUpClass(cls) -> None:
        logger.info("********************开始执行新增项目接口测试用例********************")
        """注册一个用户"""
        register_url = cls.conf.get("env", "test_url") + "/member/register"
        register_headers = eval(cls.conf.get("headers", "header"))
        register_data = {"mobile_phone": cls.random_phone(), "pwd": "123456789", "type": 0, "reg_name": "hyean_ad"}
        logger.info("开始执行注册用例，用例参数为{}".format(register_data))
        register_result = cls.http.send(url=register_url, headers=register_headers, method="post", data=register_data)
        logger.info("注册用例执行成功，用户注册结果返回：{}".format(register_result.json()))
        """记录返回结果中的用户id,phone设为类属性"""
        cls.member_id = jsonpath.jsonpath(register_result.json(), "$..id")[0]
        cls.mobile_phone = jsonpath.jsonpath(register_result.json(), "$..mobile_phone")[0]

        """执行登录，获取用户登录后的token"""
        login_url = cls.conf.get("env", "test_url") + "/member/login"
        login_headers = eval(cls.conf.get("headers", "header"))
        login_data = {"mobile_phone": cls.mobile_phone, "pwd": "123456789"}
        logger.info("开始执行登录用例，用例参数为{}".format(login_data))
        login_result = cls.http.send(url=login_url, headers=login_headers, method="post", data=login_data)
        logger.info("登录用例执行成功，用户登录结果返回：{}".format(login_result.json()))

        """记录登录接口返回的token_type,token进行拼接"""
        token_type = jsonpath.jsonpath(login_result.json(), "$..token_type")[0]
        token = jsonpath.jsonpath(login_result.json(), "$..token")[0]
        # 拼接成鉴权要用的token
        cls.token_new = token_type + " " + token
        logger.info("登录执行成功，可用于鉴权的token值为 {}".format(cls.token_new))

    @data(*cases)
    def test_add(self, case):
        # 准备数据
        case_url = self.conf.get("env", "test_url") + case["url"]
        case_headers = eval(self.conf.get("headers", "header"))
        case_headers["Authorization"] = self.token_new
        case_headers["Content-Type"] = "application/json"
        if "#member_id#" in case["data"]:
            case["data"] = case["data"].replace("#member_id#", str(self.member_id))
        case_data = eval(case["data"])
        case_expected = eval(case["expected"])
        # 发送请求
        logger.info("开始执行用例[{}]，用例参数为:{}".format(case["title"], case_data))
        result = self.http.send(url=case_url, headers=case_headers, method=case["method"], data=case_data)
        # 断言
        try:
            self.assertEqual(case_expected["code"], result.json()["code"])
            self.assertEqual(case_expected["msg"], result.json()["msg"])
        except AssertionError as e:
            self.excel.write_data(row=case["case_id"] + 1, column=self.conf.getint("excel", "column"), value="未通过")
            print("用例[{}]——>预期结果是:{}，\n实际结果是:{}".format(case["title"], case_expected, result.json()))
            logger.info("用例[{}]执行失败".format(case["title"]))
            logger.info("预期结果——>{}".format(case_expected))
            logger.info("实际结果——>{}".format(result.json()))
            raise e
        else:
            self.excel.write_data(row=case["case_id"] + 1, column=self.conf.getint("excel", "column"), value="通过")
            logger.info("用例[{}]执行成功".format(case["title"]))
            logger.info("实际运行结果是{}".format(result.json()))
