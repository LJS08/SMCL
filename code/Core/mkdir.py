import os


def make_dir(path_):
    if not os.path.isdir(path_):
        os.mkdir(path_)


def make_long_dir(path_: str):
    path_ = path_.split("/")
    path__ = path_[0]
    make_dir(path__)
    for d in path_[1:]:
        path__ += "/" + d
        make_dir(path__)
    del path_
    del path__


class Files(object):
    def __init__(self):
        self.path = None

    def make_mc_dir(self, fpath):
        fpath = os.path.abspath(fpath)
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
        self._make_mc_dir(fpath, paths)
        self.path = fpath + "/.minecraft"
        del paths
        del fpath

    def _make_mc_dir(self, path_, d):
        for i in d.keys():
            make_dir(path_ + "/" + i)
            self._make_mc_dir(path_ + "/" + i, d[i])


