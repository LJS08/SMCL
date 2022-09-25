import os
import time
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import tkinter.messagebox

import requests

import core

# coding:utf-8
# Make a dirs if there is no.

config_path = os.path.abspath("config.txt")


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


f = Files()
f.make_mc_dir(".")


def path(file: str):
    return file


def read_config():
    global config_path
    with open(config_path, "r") as openfile:
        file = openfile.readline().split(",")
        return [file[0], file[1], file[2], file[3]]


def write_config(infos):
    global config_path
    if infos:
        with open(config_path, "w") as writefile:
            writefile.write(infos[0] + "," + os.path.abspath(infos[1]) + "," + infos[2] + "," + infos[3])


def main_page():
    global basic_info

    def launch():
        start_time = time.time()
        print("We are launching for you!")
        core.core_bootstrap_main(True, basic_info[1], version.get(), "BMCLAPI")
        os.popen(core.core_start_IN(basic_info[0], basic_info[1], version.get(), basic_info[2], "0", "0", "Lite", False,
                                    "20", "20", "128M", basic_info[3])[1])
        success_time = time.time()
        print("Launch success in " + str(success_time - start_time) + "seconds")

    def copyr():
        tk.messagebox.showinfo("SMCL", "SMCL Beta1.0.0 created by LJS80 and Sharll.\nCopyright SMDC Develop Bar 2022.")

    # init
    window = tk.Tk()
    bgimage1 = tk.PhotoImage(file="./imgs/backdrop.png")
    bg = tk.Label(window, image=bgimage1)
    window.iconphoto(False, tk.PhotoImage(file="./imgs/icon.png"))
    window.geometry("640x360")
    window.title("SMCL Lite")
    window.resizable(0, 0)
    # title
    titles_Frame = tk.Frame(window, width=640, height=60, bg="#FFFFFF")
    title = tk.Button(window, text="SMCL", bg="#FFFFFF", font=("Bahnschrift", 22), command=copyr, bd=0)
    # copyr = tk.Label(window, text="SMCL Beta1.0.0 created by LJS80 and Sharll. Copyright SMDC Develop Bar 2022.")

    # window.overrideredirect(True)
    # buttons
    img1 = tk.PhotoImage(file=path(r"./imgs/launch.png"))
    btn_launch = tk.Button(window, text="Launch", image=img1, bg="#FFFFFF",
                           activebackground="#CADFF2", bd=0, height=56, width=120,
                           font=("simhei", 16), command=launch, compound="top")

    img2 = tk.PhotoImage(file=path(r"./imgs/Download.png"))
    btn_download = tk.Button(window, text="Download", image=img2, bg="#FFFFFF",
                             activebackground="#CADFF2", bd=0, height=56, width=120,
                             font=("simhei", 14,), command=download_page, compound="top")

    img3 = tk.PhotoImage(file=path(r"./imgs/Settings.png"))
    btn_setting = tk.Button(window, text="Settings", image=img3, bg="#FFFFFF",
                            activebackground="#CADFF2", bd=0, height=56, width=120,
                            font=("simhei", 14,), command=setting_page, compound="top")

    version = ttk.Combobox(window)
    version["values"] = os.listdir(basic_info[1] + "\\versions")
    version.insert(0, os.listdir(basic_info[1] + "\\versions")[0])

    # backdrop
    bg.pack()
    # title
    titles_Frame.place(x=0, y=0)
    title.place(x=520, y=0)
    # copyr.place(x=0, y=340)
    # buttons
    btn_launch.place(x=0, y=0)
    btn_download.place(x=130, y=0)
    btn_setting.place(x=260, y=0)
    version.place(x=0, y=60, width=120)
    # run
    window.mainloop()


def download_page():
    def download():
        core.core_bootstrap_main(True, basic_info[1], versions.get(versions.curselection()), "BMCLAPI")
        print("Ok")

    window = tk.Tk()
    window.geometry("640x360")
    window.title("SMCL Lite")
    window.resizable(0, 0)

    versions = tk.Listbox(window, selectmode=tk.SINGLE)
    btn_ok = tk.Button(window, text="下载", command=download)

    for i in requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()["versions"]:
        versions.insert("end", i['id'])

    versions.place(x=0, y=0, height=360)
    btn_ok.place(x=185, y=200)

    window.mainloop()


def setting_page():
    def write():
        global basic_info
        write_config([java.get(), dotmc.get(), name.get(), memory.get()])
        basic_info = read_config()
        window.destroy()

    def choosefile():
        jpath = tk.filedialog.askopenfilenames(filetypes=[('java/javaw程序', '.exe')])
        if jpath:
            java.delete(0, "end")
            java.insert(0, '"' + jpath[0] + '"')

    def choosefolder():
        dpath = tk.filedialog.askdirectory()
        if dpath:
            dotmc.delete(0, "end")
            dotmc.insert(0, dpath)

    window = tk.Tk()
    window.geometry("640x360")
    window.title("SMCL Lite")
    window.resizable(0, 0)

    infos = read_config()

    # java路径模块
    tk.Label(window, text="java路径").place(x=0, y=5)
    java = tk.Entry(window, show=None)
    java.place(x=90, y=5, width=400)
    java.insert(0, infos[0])
    btn_choosejava = tk.Button(window, command=choosefile, text="View...")
    btn_choosejava.place(x=475, y=0)

    # minecraft路径模块
    tk.Label(window, text=".minecraft路径").place(x=0, y=30)
    dotmc = tk.Entry(window, show=None)
    dotmc.place(x=90, y=30, width=400)
    dotmc.insert(0, infos[1])
    btn_choosejava = tk.Button(window, command=choosefolder, text="View...")
    btn_choosejava.place(x=475, y=25)

    # 玩家名模块
    tk.Label(window, text="玩家名").place(x=0, y=55)
    name = tk.Entry(window, show=None)
    name.place(x=90, y=55, width=200)
    name.insert(0, infos[2])

    # 内存分配模块
    tk.Label(window, text="内存分配").place(x=0, y=80)
    memory = tk.Entry(window, show=None)
    memory.place(x=90, y=80)
    memory.insert(0, infos[3])

    btn_ok = tk.Button(window, text="OK", command=write)

    btn_ok.place(x=300, y=180, width=40)

    window.mainloop()


if not os.path.exists("config.txt"):
    write_config(["java", ".minecraft", "player", "2048M"])
    tk.messagebox.showwarning("警告",
                              "请务必确定你的SMCL是从正规渠道下载的\n否则极其有可能被安装了病毒\n请前往www.hello-smcl.cn下载.")
basic_info = read_config()

main_page()
