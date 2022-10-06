import sys
from threading import RLock


single_lock = RLock()


def Singleton(cls):
    instance = {}

    def _singleton_wrapper(*args, **kargs):
        with single_lock:
            if cls not in instance:
                instance[cls] = cls(*args, **kargs)
        return instance[cls]

    return _singleton_wrapper


@Singleton
class Const:
    # 自定义异常处理
    class ConstValueError(PermissionError):
        pass

    class ConstCaseError(PermissionError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstValueError("不能修改常量 {0} 的值 ".format(name))

        if not name.isupper():
            raise self.ConstCaseError("常量名称 {0} 必须大写".format(name))

        self.__dict__[name] = value


sys.modules[__name__] = Const()

# Thanks https://zhuanlan.zhihu.com/p/353201473
# emm 真的是魔法方法啊。。。 https://zhuanlan.zhihu.com/p/101004827?from_voters_page=true
