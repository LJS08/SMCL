import tkinter as tk
import tkinter.messagebox
import Download
import Core.core_start as Launch
import logging
import os
import wx
import PIL.Image

saying_page_open = 0
advanced_settings_yn = False

class advanced_settings(wx.Frame):
    def __init__(self):
        super().__init__(None, title="SMCL Lite", size=(600, 400), pos=(100, 100))
        panel = wx.Panel(parent=self)
        tc1 = wx.TextCtrl(panel)
        tc2 = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        tc2_pass_b = wx.Button(parent=panel, label="显示uuid", )
        self.Bind(wx.EVT_BUTTON, self.on_click, tc2_pass_b)
        tc3 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        Conf_ST = wx.StaticText(panel, label="选择配置的存储方式")
        Conf_SQL = wx.CheckBox(panel, id=1, label="使用数据库进行存放", style=wx.RB_GROUP)
        Conf_text = wx.CheckBox(panel, id=2, label="使用文本文档进行存放")
        Conf_text.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_Conf_sel, id=1, id2=2)

        statictext = wx.StaticText(parent=panel, label="SMCL-Lite by LJS80(wxPython)", pos=(10, 10))
        username = wx.StaticText(parent=panel, label="用户名:")
        uuid = wx.StaticText(parent=panel, label="uuid:")
        变量名_反馈与建议 = wx.StaticText(parent=panel, label="反馈与建议")

        hbox1 = wx.BoxSizer()
        hbox1.Add(tc2_pass_b, flag=wx.EXPAND | wx.RIGHT, border=5)

        hbox2 = wx.BoxSizer()
        hbox2.Add(Conf_ST, flag=wx.LEFT | wx.RIGHT, border=5)
        hbox2.Add(Conf_SQL)
        hbox2.Add(Conf_text)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(username, flag=wx.EXPAND | wx.LEFT, border=10)
        vbox.Add(tc1, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(uuid, flag=wx.EXPAND | wx.LEFT, border=10)
        vbox.Add(tc2, flag=wx.EXPAND | wx.ALL, border=10)

        vbox.Add(hbox1, flag=wx.ALL, border=10)
        vbox.Add(hbox2, flag=wx.ALL, border=10)

        vbox.Add(变量名_反馈与建议, flag=wx.EXPAND | wx.LEFT, border=10)
        vbox.Add(tc3, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(statictext, flag=wx.EXPAND | wx.LEFT, border=10)

        panel.SetSizer(vbox)

        tc1.SetValue("Player")

    def on_click(self, event):
        tc1 = self.TextCtrl(panel)
        tc2 = self.TextCtrl(panel, style=wx.TE_PASSWORD)
        tc2_pass_b = self.Button(parent=panel, label="隐藏uuid", )
        self.Bind(wx.EVT_BUTTON, self.on_click, b_h)
        tc3 = self.TextCtrl(panel, style=wx.TE_MULTILINE)

        statictext = self.StaticText(parent=panel, label="SMCL-Lite by LJS80(wxPython)", pos=(10, 10))
        username = self.StaticText(parent=panel, label="用户名:")
        uuid = self.StaticText(parent=panel, label="uuid:")
        变量名_反馈与建议 = self.StaticText(parent=panel, label="反馈与建议")

        vbox = self.BoxSizer(wx.VERTICAL)

        vbox.Add(username, flag=wx.EXPAND | wx.LEFT, border=10)
        vbox.Add(tc1, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(uuid, flag=wx.EXPAND | wx.LEFT, border=10)
        vbox.Add(tc2, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(b, flag=wx.EXPAND | wx.RIGHT, border=10)
        vbox.Add(变量名_反馈与建议, flag=wx.EXPAND | wx.LEFT, border=10)
        vbox.Add(tc3, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(statictext, flag=wx.EXPAND | wx.LEFT, border=10)

        self.panel.SetSizer(vbox)

    def on_checkbox_Conf_sel(self, event):
        pass


def path(file: str):
    return file


def read_config():
    with open("./config.txt", "r") as file:
        file = file.readline().split(",")
        return [file[0], file[1], file[2], file[3]]


def write_config(infos):
    if infos:
        with open("./config.txt", "w") as file:
            file.write(infos[0] + "," + infos[1] + "," + infos[2] + "," + infos[3])


class main_page(object):
    def __init__(self):
        # init
        window = tk.Tk()
        image = tk.PhotoImage(file=path("./imgs/backdrop.png"))
        bg = tk.Label(window, image=image)
        window.iconphoto(False, tk.PhotoImage(file="./imgs/icon.png"))
        window.geometry("800x450")
        window.title("SMCL Lite")
        window.resizable(0, 0)
        # window.attributes("-alpha", 0.8)       # 透明色设置
        # title
        titles_Frame = tk.Frame(window, width=800, height=60, bg="#FFFFFF")
        title = tk.Label(titles_Frame, text="SMCL", bg="#FFFFFF", font=("Bahnschrift", 30))
        title2 = tk.Label(titles_Frame, text="Hello, World!", bg="#FFFFFF", font=("Bahnschrift", 12))
        # window.overrideredirect(True)
        # buttons
        img1 = tk.PhotoImage(file=path(r"./imgs/launch.png"))
        btn_launch = tk.Button(window, text="Launch", image=img1, bg="#FFFFFF", activebackground="#CADFF2", bd=0, height=56, width=120, font=("simhei", 16), command=launch_page, compound="top")

        img2 = tk.PhotoImage(file=path(r"./imgs/Download.png"))
        btn_download = tk.Button(window, text="Download", image=img2, bg="#FFFFFF", activebackground="#CADFF2", bd=0, height=56, width=120, font=("simhei", 14,), command=download_page, compound="top")

        img3 = tk.PhotoImage(file=path(r"./imgs/Settings.png"))
        btn_setting = tk.Button(window, text="Settings", image=img3, bg="#FFFFFF", activebackground="#CADFF2", bd=0, height=56, width=120, font=("simhei", 14,), command=setting_page, compound="top")
        img4 = tk.PhotoImage(file=path(r"./imgs/Saying.png"))
        btn_saying = tk.Button(window, text="About", image=img4, bg="#FFFFFF", activebackground="#CADFF2", bd=0, height=56, width=120, font=("simhei", 14,), command=saying_page, compound="top")

        # backdrop
        bg.pack()
        # title
        titles_Frame.place(x=0, y=0)
        title.place(x=650, y=5)
        title2.place(x=550, y=30)
        # buttons
        btn_launch.place(x=0, y=0)
        btn_download.place(x=130, y=0)
        btn_setting.place(x=260, y=0)
        btn_saying.place(x=390, y=0)
        # run
        window.mainloop()


def launch_page():
    global basic_info

    def launch():
        Launch.core_start_IN(basic_info[0], basic_info[1], version.get(), basic_info[2], "0", "0", "Lite", False, "20", "20", "128M", basic_info[3])

    window = tk.Tk()
    window.geometry("800x450")
    window.title("SMCL Lite")
    window.resizable(0, 0)
    tk.Label(window, text="启动什么版本").pack()
    version = tk.Entry(window, show=None)
    version.pack()
    version.insert(0, "1.16.5")
    btn_launch = tk.Button(window, text="启动", command=launch)
    btn_launch.pack()
    window.mainloop()


def download_page():
    def download():
        print("download" + downloader.get_version_list()[1][versions.curselection()[0]]["id"])
        downloader.download_version(downloader.get_version_list()[1][versions.curselection()[0]]["id"])
        print("Ok")

    window = tk.Tk()
    window.geometry("800x450")
    window.title("SMCL Lite")
    window.resizable(0, 0)
    downloader = Download.DownMC()
    downloader.get_version_list()

    versions = tk.Listbox(window, selectmode=tk.SINGLE)
    btn_ok = tk.Button(window, text="下载", command=download)

    for i in downloader.get_version_list()[1]:
        versions.insert("end", i["id"])

    versions.pack()
    btn_ok.place(x=185, y=200)

    window.mainloop()


def saying_page():
    global advanced_settings_yn
    if advanced_settings_yn:
        tk.messagebox.showinfo("SMCL Lite", "SMCL Lite 1.0 by Sharll\nSMCL Lite 1.0 Advanced Settings 1.0 by LJS80\nSMDC Develop Bar, 2022\n")
    else:
        tk.messagebox.showinfo("SMCL Lite", "SMCL Lite 1.0 by Sharll\nSMDC Develop Bar, 2022\n")
    global saying_page_open
    saying_page_open += 1
    if saying_page_open >= 10:
        advanced_settings_yn = True


def advanced_settings_boot():
    app = wx.App()
    frm = advanced_settings()
    frm.Show()
    app.MainLoop()


def setting_page():
    def write():
        global basic_info
        write_config([java.get(), dotmc.get(), name.get(), memory.get()])
        basic_info = read_config()

    def choosefile():
        jpath = tk.filedialog.askopenfilenames(filetypes=[('java/javaw程序', '.exe')])
        if jpath:
            java.delete(0, "end")
            java.insert(0, '"'+jpath[0]+'"')

    def choosefolder():
        dpath = tk.filedialog.askdirectory()
        if dpath:
            dotmc.delete(0, "end")
            dotmc.insert(0, dpath)

    window = tk.Tk()
    window.geometry("800x450")
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

    btn_ok.place(x=390, y=400, width=20)
    global advanced_settings_yn
    if advanced_settings_yn:
        btn_advanced_settings = tk.Button(window, text="Advanced_Settings", command=advanced_settings_boot)
        btn_advanced_settings.place(x=420, y=400, width=150)
    window.mainloop()


if not os.path.exists("./config.txt"):
    write_config(["java", "./.minecraft", "player", "2048M"])
basic_info = read_config()

main_page()
