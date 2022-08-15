# coding:utf-8
# 发送请求

import requests
from files import f
from os.path import isfile
from threading import Thread
from multiprocessing import cpu_count


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
        versions = self.get("https://bmclapi2.bangbang93.com/mc/game/version_manifest.json")  # 调用api
        if versions[0]:  # 正常情况
            versions = versions[1].json()
            # 获取最新版本
            self.latest = versions["latest"]
            # 获取所有版本
            versions = versions["versions"]
            self.versionList = {"all": [], "release": [], "snapshot": [], "old_beta": [], "old_alpha": []}
            for version in versions:
                self.versionList["all"].append(version["id"])
                self.versionList[version["type"]].append(version["id"])
            del version
            return True, versions  # 回调
        else:  # 出现错误
            return versions  # 回调

    def download_version(self, version: str, filename: str = None, path="./.minecraft", reinstall_libs=False):
        """下载原版mc"""
        # 检测版本是否存在
        if version not in self.versionList["all"]:
            return False, f"没有名为{version}的版本"
        # 版本名
        if not filename:
            filename = version
        # 下载版本jar与json
        data = self.get(f"https://bmclapi2.bangbang93.com/version/{version}/client")
        json = self.get(f"https://bmclapi2.bangbang93.com/version/{version}/json")
        if data[0] and json[0]:
            f.make_long_dir(f"{path}/versions/{filename}")
            with open(f"{path}/versions/{filename}/{filename}.jar", "wb") as file:
                file.write(data[1].content)
            with open(f"{path}/versions/{filename}/{filename}.json", "w") as file:
                file.write(json[1].text)
            del data
        else:
            return data
        # 下载libraries文件
        files = json[1].json()["libraries"]
        for attr in files:
            attr = attr["downloads"]["artifact"]
            if not ("-macos" in attr["url"] or "-linux" in attr["url"]):
                if reinstall_libs or (not isfile(f"{path}/libraries/{attr['path']}")):
                    data = self.get(attr["url"])
                    if "natives" in attr["url"]:
                        print(attr["url"])
                    f.make_long_dir("/".join(f"{path}/libraries/{attr['path']}".split("/")[:-1]))
                    with open(f"{path}/libraries/{attr['path']}", "wb") as file:
                        file.write(data[1].content)
        # 下载assets索引，并根据索引下载assets
        index = self.get(json[1].json()["assetIndex"]["url"].replace("https://launchermeta.mojang.com",
                                                                     "https://bmclapi2.bangbang93.com").replace(
            "https://launcher.mojang.com", "https://bmclapi2.bangbang93.com"))
        if index[0]:
            with open(f"{path}/assets/indexes/{json[1].json()['assetIndex']['id']}.json", "w") as file:
                file.write(index[1].text)
            assets = list(index[1].json()["objects"].values())

            def _download(asset):
                if not isfile(f"{path}/assets/objects/{asset['hash'][:2]}/{asset['hash']}"):
                    data = self.get("https://bmclapi2.bangbang93.com/assets/" + asset["hash"])[1].text
                    try:
                        f.make_long_dir(f"{path}/assets/objects/{asset['hash'][:2]}")
                    except FileExistsError:
                        pass
                    try:
                        with open(f"{path}/assets/objects/{asset['hash'][:2]}/{asset['hash']}", "w") as file:
                            file.write(data)
                    except:
                        pass

            def download():
                while assets:
                    asset = assets[0]
                    assets.pop(0)
                    _download(asset)


d = DownMC()
