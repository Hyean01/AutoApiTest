"""
Editor:Hyean
E-mail:1067065568@qq.com
"""
import unittest
import os
import random
import pymysql
from com.contant import data_dir, conf_dir
from com.readexcel import ReadExcel
from lib.ddt import ddt, data
from configparser import ConfigParser
from com.handlerequest import HandleRequest
from com.mylog import logger


# 创建读取配置文件的对象，设置为类属性
conf_path = os.path.join(conf_dir, "conf.ini")
conf = ConfigParser()
conf.read(filenames=conf_path, encoding="utf8")
data_path = os.path.join(data_dir, conf.get("excel", "name"))

con = pymysql.Connect(host=conf.get("db", "host"),
                      port=conf.getint("db", "port"),
                      user=conf.get("db", "username"),
                      password=conf.get("db", "password"),
                      charset="utf8")
cur = con.cursor()


@ddt
class RegisterTest(unittest.TestCase):
    # 准备数据
    excel = ReadExcel(file_name=data_path, sheet_name="register")
    cases = excel.read_data()
    http = HandleRequest()

    @classmethod
    def setUpClass(cls) -> None:
        logger.info("********************开始执行注册接口测试用例********************")

    # 创建一个静态方法用于生成随机手机号
    @staticmethod
    def random_phone():
        phone = "185"
        # sql = "SELECT * FROM futureloan.member WHERE mobile_phone = #phone#"
        for i in range(8):
            phone += str(random.randint(0, 9))
        return phone
            # sql = sql.replace("#phone#", phone)
        # #if cur.execute(sql) == '0':
        #     return phone
        # else:
        #     return self.random_phone()

    @data(*cases)
    def test_register(self, case):
        # 参数替换
        if "#phone#" in case["data"]:
            case["data"] = case["data"].replace("#phone#", self.random_phone())
        case_data = eval(case["data"])
        case_expected = eval(case["expected"])
        url = conf.get(section="env", option="test_url") + case["url"]
        headers = eval(conf.get(section="headers", option="header"))
        headers["Content-Type"] = "application/json"
        # 判断excel中该条用例是否有要执行的sql语句
        if case["sql"] is not None:
            case["sql"] = case["sql"].replace("#phone#", case_data["mobile_phone"])
        # 发送请求
        logger.info("用例[{}]开始执行，用例参数为：{}".format(case["title"], case_data))
        result = self.http.send(url=url, headers=headers, method=case["method"], data=case_data)
        # 断言
        try:
            self.assertEqual(case_expected["code"], result.json()["code"])
            self.assertEqual(case_expected["msg"], result.json()["msg"])
            # 注册成功后，进行数据库校验，看数据库是否有插入一条新数据
            if case_expected["msg"] == "OK":
                try:
                    logger.info("数据库校验：{}".format(case["sql"]))
                    self.assertEqual(1, cur.execute(case["sql"]))
                except AssertionError as e:
                    print("数据库校验失败")
                    logger.info("数据库校验失败，注册成功但未在数据库插入数据：{}——>{}".format(cur.execute(case["sql"]), cur.fetchall()))
                    logger.error(e)
                    raise e
                else:
                    # print("数据库校验成功{}---->{}".format(case["sql"], cur.fetchall()))
                    logger.info("数据库校验成功 [{}]---->{}".format(case["sql"], cur.fetchall()))
        except AssertionError as e:
            self.excel.write_data(row=case["case_id"] + 1, column=conf.getint("excel", "column"), value="未通过")
            print("用例[{}]——>预期结果是:{}，\n实际结果是:{}".format(case["title"], case_expected, result.json()))
            logger.info("用例[{}]执行失败".format(case["title"]))
            logger.info("预期结果——>{}".format(case_expected))
            logger.info("实际结果——>{}".format(result.json()))
            logger.error(e)
            raise e
        else:
            self.excel.write_data(row=case["case_id"] + 1, column=conf.getint("excel", "column"), value="通过")
            logger.info("用例[{}]执行成功".format(case["title"]))
            logger.info("实际结果——>{}".format(result.json()))

    def tearDown(self) -> None:
        """每条用例执行完成后，要提交一次数据库事务，不然下次执行就会报错"""
        con.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """全部用例执行完成后，关闭游标和数据库连接"""
        cur.close()
        con.close()
