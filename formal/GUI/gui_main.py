# coding:utf-8

from GUI.GUI import GUI
from GUI.pages.index import index as _index

gui = GUI()


@gui.page("index", "主页", "854x480")
def index(root):
    return _index(root)
