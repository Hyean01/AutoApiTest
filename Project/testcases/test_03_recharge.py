"""
Editor:Hyean
E-mail:1067065568@qq.com
"""
import unittest
import os
import random
import jsonpath
from com.readexcel import ReadExcel
from com.contant import data_dir, conf_dir
from configparser import ConfigParser
from lib.ddt import ddt, data
from com.handlerequest import HandleRequest
from com.mylog import logger


conf_path = os.path.join(conf_dir, "conf.ini")
conf = ConfigParser()
conf.read(conf_path, encoding="utf8")
data_path = os.path.join(data_dir, conf.get("excel", "name"))
@ddt
class RechargeTest(unittest.TestCase):
    excel = ReadExcel(data_path, "recharge")
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
        logger.info("********************开始执行充值接口测试用例********************")
        """用例开始之前先执行注册接口，获取一个注册成功的账号，然后执行登录结果，获取鉴权所需的token"""
        # 执行注册接口
        register_data = {"mobile_phone": cls.random_phone(), "pwd": "123456789", "type": 0, "reg_name": "hyean"}
        register_url = conf.get("env", "test_url") + "/member/register"
        register_headers = eval(conf.get("headers", "header"))
        logger.info("开始执行注册用例，用例参数为:{}".format(register_data))
        register_result = cls.http.send(url=register_url, headers=register_headers, method="post", data=register_data)
        logger.info("注册用例执行成功，注册结果返回{}".format(register_result.json()))
        """记录返回结果中的用户id,phone设为类属性"""
        member_id = jsonpath.jsonpath(register_result.json(), "$..id")[0]
        phone = jsonpath.jsonpath(register_result.json(), "$..mobile_phone")[0]
        setattr(RechargeTest, "member_id", member_id)
        # print(member_id, type(member_id))
        # setattr(RechargeTest, "mobile_phone", register_result.json()["mobile_phone"])
        # 执行登录接口
        login_data = {"mobile_phone": phone, "pwd": "123456789"}
        login_url = conf.get("env", "test_url") + "/member/login"
        login_headers = eval(conf.get("headers", "header"))
        logger.info("开始执行登录用例，用例参数为:{}".format(login_data))
        login_result = cls.http.send(url=login_url, headers=login_headers, method="post", data=login_data)
        logger.info("登录用例执行成功，登录结果返回{}".format(login_result.json()))

        """记录登录接口返回的token_type,token进行拼接"""
        token_type = jsonpath.jsonpath(login_result.json(), "$..token_type")[0]
        token = jsonpath.jsonpath(login_result.json(), "$..token")[0]
        # 拼接成鉴权要用的token
        token_new = token_type + " " + token
        # 设置为类属性
        setattr(RechargeTest, "token", token_new)
        logger.info("登录执行成功，可用于鉴权的token值为 {}".format(token_new))

    @data(*cases)
    def test_recharge(self, case):
        # 准备数据
        url = conf.get("env", "test_url") + case["url"]
        headers = eval(conf.get("headers", "header"))
        headers["Content-Type"] = "application/json"
        # 鉴权用的token
        headers["Authorization"] = self.token
        # 参数替换
        if "#member_id#" in case["data"]:
            case["data"] = case["data"].replace("#member_id#", str(self.member_id))
        try:
            case_data = eval(case["data"])
            case_expected = eval(case["expected"])
        except SyntaxError as e:
            self.excel.write_data(row=case["case_id"] + 1, column=conf.getint("excel", "column"), value="参数格式化错误")
            logger.info("用例[{}]-->数据格式化错误,excel读取到的入参为{}".format(case["title"], case["data"]))
            logger.error(e)
            raise e
        else:
            # 发送请求a
            logger.info("开始执行用例[{}]，用例参数为:{}".format(case["title"], case_data))
            result = self.http.send(url=url, headers=headers, method=case["method"], data=case_data)
            # 断言
            try:
                self.assertEqual(case_expected["code"], result.json()["code"])
                self.assertEqual(case_expected["msg"], result.json()["msg"])
            except AssertionError as e:
                self.excel.write_data(row=case["case_id"] + 1, column=conf.getint("excel", "column"), value="未通过")
                print("用例[{}]——>预期结果是:{}，\n实际结果是:{}".format(case["title"], case_expected, result.json()))
                logger.info("用例[{}]执行失败".format(case["title"]))
                logger.info("预期结果——>{}".format(case_expected))
                logger.info("实际结果——>{}".format(result.json()))
                raise e
            else:
                self.excel.write_data(row=case["case_id"] + 1, column=conf.getint("excel", "column"), value="通过")
                logger.info("用例[{}]执行成功".format(case["title"]))
                logger.info("实际运行结果是{}".format(result.json()))
