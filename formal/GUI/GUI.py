# coding:utf-8
# GUI引擎
import tkinter as tk


# GUI页面
class GUI(object):
    def __init__(self):
        """初始化"""
        self.root = tk.Tk()
        self.root.resizable(0, 0)
        self.pages = {}

    def _replace_function(*args, **kwargs):
        return "You can't use page function without main."

    def page(self, id, title, geometry):
        def _page(function):
            self.pages[id] = {"title": title, "geometry": geometry, "fun": function}
            return self._replace_function

        return _page

    def show(self, page):
        config = self.pages[page]
        self.root.geometry(config["geometry"])
        self.root.title("SMCL - " + config["title"])
        ret = config["fun"](self.root)
        return ret
