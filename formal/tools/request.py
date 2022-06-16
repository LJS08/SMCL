# coding:utf-8
# 发送请求

import requests


# 请求父类
class Request(object):
    def __init__(self, headers={}):
        # 初始化
        self.session = requests.session()
        self.session.headers = headers

    def get(self, url, params={}):
        # get请求
        try:
            return True, self.session.get(url=url, params=params)
        except Exception as e:
            return False, e

    def post(self, url, data={}):
        # post请求
        try:
            return self.session.post(url=url, data=data)
        except Exception as e:
            return False, e


# 下载MC原版
class DownMC(Request):
    def __init__(self):
        """初始化"""
        super(DownMC, self).__init__({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763"})
        self.versionList = None

    def get_version_list(self):
        """获取版本列表"""
        versions = self.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")  # 调用api
        if versions[0]:  # 正常情况
            versions = versions[1].json()
            # 获取最新版本
            self.latest = versions["latest"]
            # 获取所有版本
            versions = versions["versions"]
            self.versionList = []
            for version in versions:
                self.versionList.append(version["id"])
            del version
            return True, versions  # 回调
        else:  # 出现错误
            return versions  # 回调

    def download_version(self, version: str, filename: str = None):
        """下载原版mc"""
        # 检测版本是否存在
        if version not in self.versionList:
            return False, f"没有名为{version}的版本"
        # 版本名
        if not filename:
            filename = version
        # 下载版本
        data = self.get(f"https://bmclapi2.bangbang93.com/version/{version}/client")
        if data[0]:
            data = data[1].content
            with open(filename + ".jar", "wb") as file:
                file.write(data)
            del data
            del version
            return True, filename + ".jar"
        else:
            return data
