"""
Editor:Hyean
E-mail:1067065568@qq.com
"""
import openpyxl


class CaseData(object):
    # 用于存放用例对象的类
    pass


class ReadExcel(object):
    def __init__(self, file_name, sheet_name):
        self.file_name = file_name
        self.sheet_name = sheet_name

    def open(self):
        self.wb = openpyxl.load_workbook(filename=self.file_name)
        self.sh = self.wb[self.sheet_name]

    def save(self):
        self.wb.save(filename=self.file_name)
        self.wb.close()

    def read_data(self):
        self.open()
        # 按行获取所有行数据
        rows = list(self.sh.rows)
        # 获取表头行数据
        title = []
        for r in rows[0]:
            title.append(r.value)
        # 创建一个空列表，用于存放所有的用例数据
        cases = []
        # 获取剩下行的数据，
        for row in rows[1:]:
            # 再遍历读取的行的每一个格子，然后获取格子的值存放到一个列表中
            # 创建一个空列表，用于存放该行的数据
            data = []
            for r in row:
                data.append(r.value)
                # 表头和该行数据进行打包后就是一条用例数据，再转化为字典形式
                case = dict(zip(title, data))
                # 转化后的用例数据添加到用例集合中
            cases.append(case)
        self.save()
        return cases

    def read_data_obj(self):
        self.open()
        # 获取所有行的数据
        rows = list(self.sh.rows)
        title = []
        for r in rows[0]:
            title.append(r.value)
        # 遍历剩下行的数据
        cases_obj = []
        for row in rows[1:]:
            data = []
            for r in row:
                data.append(r.value)
            case = list(zip(title, data))
            case_obj = CaseData()
            for k, v in case:
                setattr(case_obj, k, v)
            cases_obj.append(case_obj)
            self.save()
        return cases_obj

    def write_data(self, row, column, value):
        self.open()
        self.sh.cell(row=row, column=column, value=value)
        self.wb.save(self.file_name)
        self.wb.close()


if __name__ == '__main__':
    excel = ReadExcel(r"E:\Py24\Project\data\future_api_data.xlsx", "register")
    data = excel.read_data()
    print(data)
