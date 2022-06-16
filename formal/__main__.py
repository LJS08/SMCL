# coding:utf-8
# Main

from tools import request
from GUI.gui_main import gui

download = request.DownMC()
gui.show("index")
