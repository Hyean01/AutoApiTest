"""
Editor:Hyean
E-mail:1067065568@qq.com
"""
import requests


# 传入不同请求方法，调用对应的方法名发送request请求
class HandleRequest(object):
    def send(self, url, method, data, headers=None):
        if method.upper() == "POST":
            return requests.post(url=url, headers=headers, json=data)
        elif method.upper() == "GET":
            return requests.get(url=url, headers=headers, params=data)
        elif method.upper() == "PATCH":
            return requests.patch(url=url, headers=headers, json=data)


class HandleSessionRequest(object):
    """使用session鉴权的，可以直接用session对象发送request请求"""
    def __init__(self):
        self.se = requests.session()

    def send(self, url, headers, method, data):
        if method.upper() == "POST":
            return self.se.post(url=url, headers=headers, json=data)
        elif method.upper() == "GET":
            return self.se.get(url=url, headers=headers, params=data)
        elif method.upper() == "PATCH":
            return self.se.patch(url=url, headers=headers, data=data)