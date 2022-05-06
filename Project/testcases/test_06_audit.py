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
class AuditTest(unittest.TestCase):
    conf = ConfigParser()
    conf.read(filenames=conf_path, encoding="utf8")
    data_path = os.path.join(data_dir, conf.get("excel", "name"))
    excel = ReadExcel(file_name=data_path, sheet_name="project_audit")
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
        logger.info("********************开始执行审核项目接口测试用例********************")
        """注册一个管理员权限的用户，一个普通会员的用户"""
        register_url = cls.conf.get("env", "test_url") + "/member/register"
        register_headers = eval(cls.conf.get("headers", "header"))
        register_ad_data = {"mobile_phone": cls.random_phone(), "pwd": "123456789", "type": 0, "reg_name": "hyean_ad"}
        register_com_data = {"mobile_phone": cls.random_phone(), "pwd": "123456789", "type": 1, "reg_name": "hyean_com"}
        logger.info("开始执行注册用例\n管理员权限用户的用例参数为:{}\n普通用户的用例参数为{}"
                    .format(register_ad_data, register_com_data))
        register_ad_result = cls.http.send(url=register_url, headers=register_headers, method="post",
                                           data=register_ad_data)
        register_com_result = cls.http.send(url=register_url, headers=register_headers, method="post",
                                            data=register_com_data)
        logger.info("注册用例执行成功\n管理员权限用户注册结果：{}\n普通用户注册结果：{}"
                    .format(register_ad_result.json(), register_com_result.json()))
        """记录返回结果中的用户id,phone设为类属性"""
        cls.ad_member_id = jsonpath.jsonpath(register_ad_result.json(), "$..id")[0]
        cls.ad_mobile_phone = jsonpath.jsonpath(register_ad_result.json(), "$..mobile_phone")[0]
        cls.com_member_id = jsonpath.jsonpath(register_com_result.json(), "$..id")[0]
        cls.com_mobile_phone = jsonpath.jsonpath(register_com_result.json(), "$..mobile_phone")[0]

        """执行登录，获取用户登录后的token"""
        login_url = cls.conf.get("env", "test_url") + "/member/login"
        login_headers = eval(cls.conf.get("headers", "header"))
        ad_login_data = {"mobile_phone": cls.ad_mobile_phone, "pwd": "123456789"}
        com_login_data = {"mobile_phone": cls.com_mobile_phone, "pwd": "123456789"}
        logger.info("开始执行管理员权限用户登录，用例参数为{}".format(ad_login_data))
        ad_login_result = cls.http.send(url=login_url, headers=login_headers, method="post", data=ad_login_data)
        logger.info("管理员权限用户登录成功，用户登录结果返回：{}".format(ad_login_result.json()))
        logger.info("开始执行普通会员权限用户登录，用例参数为{}".format(com_login_data))
        com_login_result = cls.http.send(url=login_url, headers=login_headers, method="post", data=com_login_data)
        logger.info("普通会员用户登录成功，用户登录结果返回：{}".format(com_login_result.json()))

        """记录登录接口返回的token_type,token进行拼接"""
        # 管理员权限用户登录的token
        ad_token_type = jsonpath.jsonpath(ad_login_result.json(), "$..token_type")[0]
        ad_token = jsonpath.jsonpath(ad_login_result.json(), "$..token")[0]
        cls.ad_token_new = ad_token_type + " " + ad_token
        logger.info("管理员权限登录的用户，用于鉴权的token值为 {}".format(cls.ad_token_new))
        # 普通用户登录的token
        com_token_type = jsonpath.jsonpath(com_login_result.json(), "$..token_type")[0]
        com_token = jsonpath.jsonpath(com_login_result.json(), "$..token")[0]
        cls.com_token_new = com_token_type + " " + com_token
        logger.info("普通会员权限登录的用户，用于鉴权的token值为 {}".format(cls.com_token_new))

    def setUp(self) -> None:
        """每条用例执行之前，先执行增加项目的操作，保证有项目可以进行审核"""
        add_url = self.conf.get("env", "test_url") + "/loan/add"
        add_headers = eval(self.conf.get("headers", "header"))
        add_headers["Authorization"] = self.ad_token_new
        add_headers["Content-Type"] = "application/json"
        add_data = {
            "member_id": self.ad_member_id,
            "title": "test-001",
            "amount": 200000.00,
            "loan_rate": 10,
            "loan_term": 12,
            "loan_date_type": 1,
            "bidding_days": 5
        }
        add_result = self.http.send(url=add_url, headers=add_headers, method="POST", data=add_data)
        # 保存添加成功后的项目id
        print(add_result.json())
        loan_id = jsonpath.jsonpath(add_result.json(), "$..id")[0]
        setattr(AuditTest, "loan_id", str(loan_id))
        logger.info("新创建的需要审核的项目id为 {}".format(loan_id))

    @data(*cases)
    def test_audit(self, case):
        # 请求数据
        case_url = self.conf.get("env", "test_url") + case["url"]
        case_headers = eval(self.conf.get("headers", "header"))
        case_headers["Content-Type"] = "application/json"
        if "#loan_id_no_premisson#" in case["data"]:
            case_headers["Authorization"] = self.com_token_new
            case["data"] = case["data"].replace("#loan_id_no_premisson#", self.loan_id)
        else:
            case_headers["Authorization"] = self.ad_token_new
        if "#loan_id#" in case["data"]:
            case["data"] = case["data"].replace("#loan_id#", self.loan_id)
        if "#loan_id_pass#" in case["data"]:
            case["data"] = case["data"].replace("#loan_id_pass#",
                                                self.conf.get("test_data", "loan_id_audited"))
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
