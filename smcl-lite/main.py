import easygui, Download, Launch, os


def main_page():
    window = easygui.buttonbox("功能菜单：", "SMCL Lite - Hello,World!", ["下载", "启动", "声明"])
    if window == "下载":
        download_page()
    elif window == "启动":
        launch_page()
    elif window == "声明":
        saying_page()
    else:
        pass


def launch_page():
    window1= easygui.choicebox("选择游戏版本","启动",os.walk())
    if window1:
        window2 = easygui.multenterbox("默认值一般无需改动", '启动',
                                      ['java路径', '.minecraft路径', '启动版本名', '启动版本号', 'jar路径', '玩家名', ''],
                                      ["java", "./.minecraft", "", "", "", "", ""])
    #Launch.core_start_IN("java", )
    main_page()


def download_page():
    downloader = Download.DownMC()
    verlist = []
    for i in downloader.get_version_list()[1]:
        verlist.append(i["id"])
    window = easygui.choicebox("以下是版本列表：", "选择下载的版本", verlist)
    downloader.download_version(window)
    main_page()  # 返回主页


def saying_page():
    easygui.msgbox("SMCL Lite 1.0 by Sharll\nSMDC Develop Bar, 2022", "声明")
    main_page()


main_page()
