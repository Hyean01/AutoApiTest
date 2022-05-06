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
class InvestTest(unittest.TestCase):
    conf = ConfigParser()
    conf.read(filenames=conf_path, encoding="utf8")
    data_path = os.path.join(data_dir, conf.get("excel", "name"))
    excel = ReadExcel(file_name=data_path, sheet_name="invest")
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
        logger.info("********************开始执行投资接口测试用例********************")
        """注册一个管理员权限的用户,方便之后项目审核"""
        register_url = cls.conf.get("env", "test_url") + "/member/register"
        register_headers = eval(cls.conf.get("headers", "header"))
        register_data = {"mobile_phone": cls.random_phone(), "pwd": "123456789", "type": 0, "reg_name": "hyean_ad"}
        logger.info("开始执行注册用例\n管理员权限用户的用例参数为:{}".format(register_data))
        register_result = cls.http.send(url=register_url, headers=register_headers, method="post", data=register_data)
        logger.info("注册用例执行成功，管理员权限用户注册结果：{}".format(register_result.json()))
        """记录返回结果中的用户id,phone设为类属性"""
        cls.member_id = str(jsonpath.jsonpath(register_result.json(), "$..id")[0])
        cls.mobile_phone = str(jsonpath.jsonpath(register_result.json(), "$..mobile_phone")[0])

        """执行登录，获取用户登录后的token"""
        login_url = cls.conf.get("env", "test_url") + "/member/login"
        login_headers = eval(cls.conf.get("headers", "header"))
        login_data = {"mobile_phone": cls.mobile_phone, "pwd": "123456789"}
        logger.info("开始执行管理员权限用户登录，用例参数为{}".format(login_data))
        login_result = cls.http.send(url=login_url, headers=login_headers, method="post", data=login_data)
        logger.info("管理员权限用户登录成功，用户登录结果返回：{}".format(login_result.json()))

        """记录登录接口返回的token_type,token进行拼接"""
        # 管理员权限用户登录的token
        token_type = jsonpath.jsonpath(login_result.json(), "$..token_type")[0]
        token = jsonpath.jsonpath(login_result.json(), "$..token")[0]
        cls.token_new = token_type + " " + token
        logger.info("管理员权限登录的用户，用于鉴权的token值为 {}".format(cls.token_new))

        """执行增加项目的操作，保证有项目可以进行投资"""
        add_url = cls.conf.get("env", "test_url") + "/loan/add"
        add_headers = eval(cls.conf.get("headers", "header"))
        add_headers["Authorization"] = cls.token_new
        add_headers["Content-Type"] = "application/json"
        add_data = {
            "member_id": cls.member_id,
            "title": "test-001",
            "amount": 200000.00,
            "loan_rate": 10,
            "loan_term": 12,
            "loan_date_type": 1,
            "bidding_days": 5
        }
        add_result = cls.http.send(url=add_url, headers=add_headers, method="POST", data=add_data)
        # 保存添加成功后的项目id
        cls.loan_id = str(jsonpath.jsonpath(add_result.json(), "$..id")[0])
        logger.info("新创建的需要审核的项目id为 {}".format(cls.loan_id))
        # 创建一个不需要审核的项目
        add_result2 = cls.http.send(url=add_url, headers=add_headers, method="POST", data=add_data)
        cls.loan_id_auditing = str(jsonpath.jsonpath(add_result2.json(), "$..id")[0])
        logger.info("新创建的不需要审核的项目id为 {}".format(cls.loan_id_auditing))

        """执行审核项目的操作，保证有项目可以进行投资"""
        audit_url = cls.conf.get("env", "test_url") + "/loan/audit"
        audit_headers = eval(cls.conf.get("headers", "header"))
        audit_headers["Authorization"] = cls.token_new
        audit_headers["Content-Type"] = "application/json"
        audit_data = {"loan_id": cls.loan_id, "approved_or_not": True}
        audit_result = cls.http.send(url=audit_url, headers=audit_headers, method="PATCH", data=audit_data)
        logger.info("项目审核的headers={}".format(audit_headers))
        logger.info("项目审核的data={}".format(audit_data))
        logger.info("项目 {}审核结果为：{}".format(cls.loan_id, audit_result.json()))
        # try:
        #     cls.assertEqual(audit_expected["msg"], jsonpath.jsonpath(audit_result.json(), "$..msg")[0])
        # except AssertionError as e:
        #     logger.info("项目审核出现错误, 审核结果返回：{}".format(audit_result.json()))
        #     logger.error(e)
        #     raise e
        # else:
        #     logger.info("项目审核通过，可以进行投资")

    @data(*cases)
    def test_invest(self, case):
        # 请求数据
        case_url = self.conf.get("env", "test_url") + case["url"]
        case_headers = eval(self.conf.get("headers", "header"))
        case_headers["Content-Type"] = "application/json"
        case_headers["Authorization"] = self.token_new
        if "#member_id#" in case["data"]:
            case["data"] = case["data"].replace("#member_id#", self.member_id)
        if "#loan_id#" in case["data"]:
            case["data"] = case["data"].replace("#loan_id#", self.loan_id)
        if "#loan_id_auditing#" in case["data"]:
            case["data"] = case["data"].replace("#loan_id_auditing#", self.loan_id_auditing)
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

