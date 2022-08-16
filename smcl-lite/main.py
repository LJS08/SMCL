import easygui, os, Download, Launch


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
    window = easygui.buttonbox("功能菜单：", "SMCL Lite - Hello,World!", ["下载", "启动", "声明", "设置"])
    if window == "下载":
        download_page()
    elif window == "启动":
        launch_page()
    elif window == "声明":
        saying_page()
    elif window == "设置":
        setting_page()
    else:
        pass


def launch_page():
    window = easygui.choicebox('选择启动的版本', '启动', ["1.8.9","1.16.5"])
    if window:
        Launch.core_start_IN(basic_info[0], basic_info[1], window, basic_info[2], "0", "0", "Lite", "20", "20", "128M", basic_info[3])
    # 返回主页20
    main_page()


def download_page():
    downloader = Download.DownMC()
    verlist = []
    for i in downloader.get_version_list()[1]:
        verlist.append(i["id"])
    window = easygui.choicebox("以下是版本列表：", "选择下载的版本", verlist)
    main_page()  # 返回主页
    if window:
        downloader.download_version(window)


def saying_page():
    easygui.msgbox("SMCL Lite 1.0 by Sharll\nSMDC Develop Bar, 2022\n", "声明")
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
