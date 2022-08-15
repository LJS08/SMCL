# coding:utf-8
# Make a dirs if there is no.

import os


class Files(object):
    def __init__(self):
        pass

    def make_dir(self, dir):
        if not os.path.isdir(dir):
            os.mkdir(dir)

    def make_long_dir(self, dir: str):
        dir = dir.split("/")
        path = dir[0]
        self.make_dir(path)
        for d in dir[1:]:
            path += "/" + d
            self.make_dir(path)
        del dir
        del path

    def make_mc_dir(self, path):
        path = os.path.abspath(path)
        paths = {".minecraft": {"assets": {"indexes": {}, "log_configs": {}},
                                "bin": {"native": {}},
                                "debug": {},
                                "libraries": {},
                                "logs": {},
                                "resourcepacks": {},
                                "saves": {},
                                "screenshots": {},
                                "stats": {},
                                "texturepacks": {},
                                "texturepacks-mp-cache": {},
                                "versions": {}}}
        self._make_mc_dir(path, paths)
        self.path = path + "/.minecraft"
        del paths
        del path

    def _make_mc_dir(self, path, d):
        for i in d.keys():
            self.make_dir(path + "/" + i)
            self._make_mc_dir(path + "/" + i, d[i])


f = Files()
f.make_mc_dir(".")