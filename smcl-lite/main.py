import easygui
import os
import Download
import Core.core_start
import wx


class advanced_settings(wx.Frame):
    def __init__(self):
        super().__init__(None, title="SMCL Lite",size=(600, 400), pos=(100,100))
        panel = wx.Panel(parent=self)
        tc1 = wx.TextCtrl(panel)
        tc2 = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        tc2_pass_b = wx.Button(parent=panel, label="显示uuid",)
        self.Bind(wx.EVT_BUTTON,self.on_click,tc2_pass_b)
        tc3 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        Conf_ST = wx.StaticText(panel,label="选择配置的存储方式")
        Conf_SQL = wx.CheckBox(panel, id=1,label="使用数据库进行存放",style=wx.RB_GROUP)
        Conf_text = wx.CheckBox(panel, id=2,label="使用文本文档进行存放")
        Conf_text.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX,self.on_checkbox_Conf_sel,id=1,id2=2)
        
        statictext = wx.StaticText(parent=panel,label="SMCL-Lite by LJS80(wxPython)",pos=(10,10))
        username =  wx.StaticText(parent=panel,label="用户名:")
        uuid = wx.StaticText(parent=panel,label="uuid:")
        变量名_反馈与建议 =  wx.StaticText(parent=panel,label="反馈与建议")

        hbox1 = wx.BoxSizer()
        hbox1.Add(tc2_pass_b,flag=wx.EXPAND|wx.RIGHT,border=5)
        
        hbox2 = wx.BoxSizer()
        hbox2.Add(Conf_ST,flag=wx.LEFT|wx.RIGHT,border=5)
        hbox2.Add(Conf_SQL)
        hbox2.Add(Conf_text)
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(username,flag=wx.EXPAND|wx.LEFT,border=10)
        vbox.Add(tc1,flag=wx.EXPAND|wx.ALL,border=10)
        vbox.Add(uuid,flag=wx.EXPAND|wx.LEFT,border=10)
        vbox.Add(tc2,flag=wx.EXPAND|wx.ALL,border=10)

        vbox.Add(hbox1,flag=wx.ALL,border=10)
        vbox.Add(hbox2,flag=wx.ALL,border=10)
        
        vbox.Add(变量名_反馈与建议,flag=wx.EXPAND|wx.LEFT,border=10)
        vbox.Add(tc3,flag=wx.EXPAND|wx.ALL,border=10)
        vbox.Add(statictext,flag=wx.EXPAND|wx.LEFT,border=10)
        
        panel.SetSizer(vbox)

        tc1.SetValue("Player")
    def on_click(self,event):
        tc1 = self.TextCtrl(panel)
        tc2 = self.TextCtrl(panel, style=wx.TE_PASSWORD)
        tc2_pass_b = self.Button(parent=panel, label="隐藏uuid",)
        self.Bind(wx.EVT_BUTTON,self.on_click,b_h)
        tc3 = self.TextCtrl(panel, style=wx.TE_MULTILINE)
        
        statictext = self.StaticText(parent=panel,label="SMCL-Lite by LJS80(wxPython)",pos=(10,10))
        username =  self.StaticText(parent=panel,label="用户名:")
        uuid = self.StaticText(parent=panel,label="uuid:")
        变量名_反馈与建议 =  self.StaticText(parent=panel,label="反馈与建议")

        vbox = self.BoxSizer(wx.VERTICAL)

        vbox.Add(username,flag=wx.EXPAND|wx.LEFT,border=10)
        vbox.Add(tc1,flag=wx.EXPAND|wx.ALL,border=10)
        vbox.Add(uuid,flag=wx.EXPAND|wx.LEFT,border=10)
        vbox.Add(tc2,flag=wx.EXPAND|wx.ALL,border=10)
        vbox.Add(b,flag=wx.EXPAND|wx.RIGHT,border=10)
        vbox.Add(变量名_反馈与建议,flag=wx.EXPAND|wx.LEFT,border=10)
        vbox.Add(tc3,flag=wx.EXPAND|wx.ALL,border=10)
        vbox.Add(statictext,flag=wx.EXPAND|wx.LEFT,border=10)
        
        self.panel.SetSizer(vbox)

    def on_checkbox_Conf_sel(self,event):
        pass
        
        

        

def read_config():
    with open("./config.txt", "r") as file:
        return file.readline().split(" ")


def write_config(list):
    if list:
        with open("./config.txt", "w") as file:
            file.write(list[0]+" "+list[1]+" "+list[2]+" "+list[3])
    else:
        print("Cancel.")

def main_page():
    window = easygui.buttonbox("", "SMCL Lite", ["下载", "启动", "设置","高级设置", "声明"], )
    if window == "下载":
        download_page()
    elif window == "启动":
        launch_page()
    elif window == "声明":
        saying_page()
    elif window == "设置":
        setting_page()
    elif window == "高级设置":
        app = wx.App()
        frm = advanced_settings()
        frm.Show()
        app.MainLoop()
        main_page()
    else:
        pass


def launch_page():
    window = easygui.choicebox('选择启动的版本', '启动', ["1.8.9","1.16.5"])
    if window:
        Core.core_start.core_start_IN(basic_info[0], basic_info[1], window, basic_info[2], "0", "0", "Lite", "20", "20", "128M", basic_info[3])
    # 返回主页
    main_page()


def download_page():
    downloader = Download.DownMC()
    verlist = []
    for i in downloader.get_version_list()[1]:
        verlist.append(i["id"])
    window = easygui.choicebox("以下是版本列表：", "选择下载的版本", verlist)
    ver=window
    main_page()  # 返回主页
    if window:
        print("Downloading"+ver)
        downloader.download_version(ver)


def saying_page():
    easygui.msgbox("SMCL Lite 1.0 by Sharll\nSMCL Lite 1.0 Advanced Settings by LJS80\nSMDC Develop Bar, 2022\n", "声明")
    main_page()  # 返回主页


def setting_page():
    window = easygui.multenterbox("设置", "", ["java路径", ".minecraft路径", "玩家名", "内存分配"],
                                  read_config())
    write_config(window)
    basic_info = read_config()
    main_page()


if not os.path.exists("./config.txt") :
    write_config(["java","./.minecraft","player","2048M"])
    
basic_info=read_config()
main_page()