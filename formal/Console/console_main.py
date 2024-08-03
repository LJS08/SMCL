import platform
import os
import webbrowser
from rich.console import Console
import time
from rich.panel import Panel
import requests  # 兼容CurseForge_Task用
from loguru import logger
import Core.mkdir
import Core.ModDownload.CurseForge_Task
import Core.core_start
import json
from rich.table import Table
import sys


def clear_screen():
    try:
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
    except Exception:
        print("不支持os库?清屏执行错误")


clear_screen()
logger.add('log/Consoles_{time}.log', rotation="5 MB", compression='zip', encoding='utf-8', retention='180 days', enqueue=True)

running_src = os.getcwd()

if os.path.exists(os.path.join(running_src, ".minecraft")):  # 如果 .minecraft 存在的话
    game_dir = os.path.join(running_src, ".minecraft")  # 如果 .minecraft 存在的话,则默认为游戏文件夹

else:  # 如果 .minecraft 不存在的话
    game_dir = None

java_path = "java"
minecraft_user_dict_list = []
minecraft_user_dict = {}
launcher_name_version = "Dev-Consoles 0.0.1"

mod_list = []
author_list = []
self_set_status_key = False
status_key = ">"  # 默认的提示符样式
a_s_bit = False

help_page = '''
[bold gold1]帮助[/]
[bold bright_blue]输入 help 或 0 查看本帮助[/]
[bright_white]你也可以输入序号进行搜索[/]
[bright_white]1.输入 exit 退出[/]
[bright_white]2.输入 Mod Search 进行mod搜索[/]
[bright_white]3.输入 init 初始化启动器[/]
[bright_white]4.输入 launch 启动游戏[/]
[bright_white]5.输入 downloads_minecraft 下载游戏[/]
[bright_white]6.输入 Settings 进入设置页面[/]
'''

mod_search_page = '''
[bold bright_green]Mod搜索[/]
[bright_white]输入back取消搜索[/]
[bright_white]输入Mod名并回车开始搜索[/]
'''

init_page_str = '''
[bold bright_green]Init初始化[/]
[bright_white]1.输入minecraft_dir初始化Minecraft游戏文件夹[/]
[bright_white]2.输入save_json初始化启动器设置文件[/]
'''

launch_page_str = '''
[bold bright_green]启动游戏页面[/]
[bright_white]输入help查看本帮助[/]
[bright_white]输入back返回[/]
[bright_white]输入下表中的序号或版本启动游戏[/]
'''

downloads_minecraft_page_str = '''
[bold bright_green]下载界面[/]
[bright_white]0.输入help查看此界面[/]
[bright_white]1.输入back返回[/]
[bright_white]2.输入expand_versions展开版本列表[/]
'''

settings_page_str = '''
[bold gold1]设置页面[/]
[bright_white]0.输入help查看此页面[/]
[bright_white]1.输入back返回[/]
[bright_white]2.输入Show_all_user显示所有用户列表[/]
[bright_white]3.输入show_MS_user_accesstoken_r_t显示所有正版用户的AccessToken和RefreshToken列表[/]
[bright_white]4.输入add_offline_user添加离线用户[/]
[bright_white]5.输入add_online_user添加正版用户[/]
[bright_white]6.输入select_user选择用户[/]
'''


class ConsolesLaunchError(Exception):
    def __init__(self, message):
        super().__init__(message)


def get_dir_name(dir_get):
    dirs_list = os.listdir(dir_get)
    for dirs in dirs_list:
        if os.path.isfile(os.path.join(dir_get, dirs)):
            dirs_list.remove(dirs)
    return dirs_list


def while_input_verified(color_obj, color_name, verified_str):
    global status_key
    xhkz = True
    while xhkz:
        color_obj.print("{}".format(verified_str), style=color_name)
        v_input = input(status_key)
        if v_input == "y" or v_input == "Y":
            xhkz = False        # 结束循环
            return True
        elif v_input == "n" or v_input == "N":
            xhkz = False        # 结束循环
            return False
        else:
            color_obj.print("不正确的输入", style="bold bright_red")


def Consoles():
    color = Console(color_system='auto', style=None)

    def mod_search():
        global author_list

        color.print(Panel("{}".format(mod_search_page)))

        ret_about = Core.ModDownload.CurseForge_Task.about()
        print("Version:{0}.{1}.Build by {2}.".format(ret_about["ver"], ret_about["PF"], ret_about["Copyright"]))

        mod_name_input = input(">")

        if mod_name_input != "back":
            with color.status("[red]Working...[/]"):

                ret = Core.ModDownload.CurseForge_Task.mod_search(mod_name_input)
                mod_name_list = []
                for item in ret["data"]:
                    mod_name_list.append(item["slug"])

                    mod_authors_str = ""
                    for item_authors in item["authors"]:

                        mod_authors_str = mod_authors_str + item_authors["name"] + " "

                    author_list.append(mod_authors_str)

                table = Table()
                table.add_column('[red] Mod Name')
                table.add_column('[red] Authors')
                i_mod = 0
                for item in mod_name_list:
                    table.add_row('[blue]{}'.format(item), "{}".format(author_list[i_mod]))
                    i_mod += 1
            color.print(table)
        color.print(Panel(f"{help_page}"))

    def init_page():
        color.print(Panel(init_page_str))
        global status_key
        global game_dir

        init_p_cil_input = input(status_key)
        if init_p_cil_input == "1" or init_p_cil_input == "minecraft_dir":
            init_p_f = Core.mkdir.Files()
            init_p_f.make_mc_dir(".")
            game_dir = os.path.join(running_src, ".minecraft")
        elif init_p_cil_input == "2" or init_p_cil_input == "save_json":
            if os.path.exists(os.path.join(running_src, "config.json")):
                init_p_s_j_w_i = while_input_verified(color, "bold gold1 on red", "警告:此操作将会覆盖目前的配置文件!是否确认继续进行此操作[Y/n]")
                if not init_p_s_j_w_i:
                    color.print("[green]取消操作[/]")
                    return -1
                logger.info("覆盖了配置文件")

            if game_dir is None:
                color.print("[bright_red]创建Save_Json失败.请先设置或初始化文件夹[/]")
                logger.error("创建Save_Json失败.请先设置或初始化文件夹")
            else:
                Core.config.write(dotmc = game_dir)
                color.print("[green]操作完成.Save_Json创建完毕[/]")
                logger.info("操作完成.Save_Json创建完毕")

    def advanced_settings_page():
        global a_s_bit
        global status_key
        global self_set_status_key

        color.print("输入1给提示符后添加/去除空格", style="bright_white")
        color.print("输入0返回", style="bright_white")
        a_s_p_c_input = input("Advanced Settings{}".format(status_key))
        if a_s_p_c_input == "1":
            if self_set_status_key:
                status_key = ">"
                self_set_status_key = False     # 设置目前提示符状态标志位
                color.print("空格已去除", style="green")
            else:
                status_key = "> "
                self_set_status_key = True     # 设置目前提示符状态标志位
                color.print("空格已添加", style="green")
        a_s_bit = True

    def launch_page():
        global java_path
        global game_dir
        global launcher_name_version
        global minecraft_user_dict

        global status_key
        with color.status("[red]Working...[/]"):
            if game_dir is None:
                color.print("[bright_red]启动游戏失败.请先设置或初始化文件夹[/]")
                raise ConsolesLaunchError("启动游戏失败.没有.minecraft文件夹")

            ret = get_dir_name(os.path.join(game_dir, "versions"))
            if len(ret) == 0:
                color.print("[bright_red]启动游戏失败:没有可用的游戏[/]")
                raise ConsolesLaunchError("启动游戏失败:没有可用的游戏")

            table = Table()
            table.add_column('[gold1] 序号')
            table.add_column('[bright_blue] 版本')

            l_p_i = 0
            launch_version_dict_list = []
            launch_version_list = []
            launch_version_ser_num_list = []
            for item in ret:
                table.add_row('[gold1]{}[/]'.format(l_p_i), "[bright_blue]{}[/]".format(item))
                launch_version_dict_list.append({"ser_num": l_p_i, "version_name": item})
                launch_version_list.append(item)
                launch_version_ser_num_list.append(l_p_i)
                l_p_i += 1

        color.print(launch_page_str)
        color.print("[bright_blue]可用的游戏版本[/]")
        color.print(table)
        color.print("[bright_white]输入序号或版本号进行选择[/]")

        l_p_input_while = True
        while l_p_input_while:
            l_p_cil_input = input("launch{}".format(status_key))
            # 注意:这里input的返回是str,launch_version_ser_num_list中的数是int
            try:
                int_l_p_cil_input = int(l_p_cil_input)
            except ValueError as VE:
                logger.info(f"{VE}")
                int_l_p_cil_input = None

            if int_l_p_cil_input in launch_version_ser_num_list or l_p_cil_input in launch_version_list:        # 如果l_p_cil_input在launch_version_ser_num_list或launch_version_list中

                if int(l_p_cil_input) in launch_version_ser_num_list:        # 如果输入的是序号,那么:
                    launch_version_name = launch_version_list[int(l_p_cil_input)]
                else:       # 如果输入的是版本号
                    launch_version_name = l_p_cil_input     # 直接将版本号给lauch_version_name

                minecraft_username = minecraft_user_dict["username"]
                launch_minecraft_uuid_yn = minecraft_user_dict["launch_minecraft_uuid_yn"]
                minecraft_uuid_val = minecraft_user_dict["uuid"]
                minecraft_aT = minecraft_user_dict["access_token"]
                if minecraft_aT is None:
                    minecraft_aT = "None"

                color.print("[bright_blue]准备启动.游戏版本为:{}[/]".format(launch_version_name))
                ret_lauch = Core.core_start.core_start_IN(java_path, game_dir, launch_version_name, minecraft_username, minecraft_uuid_val, minecraft_aT, launcher_name_version, launch_minecraft_uuid_yn)
                if not launch_minecraft_uuid_yn:
                    minecraft_uuid_val = ret_lauch[2]
                    color.print("[bright_blue]您的临时UUID为:{}[/]".format(minecraft_uuid_val))
                    launch_minecraft_uuid_yn = True
                    minecraft_user_dict["launch_minecraft_uuid_yn"] = launch_minecraft_uuid_yn
                    for item in minecraft_user_dict_list:
                        if item["username"] == minecraft_username:
                            item["uuid"] = minecraft_uuid_val
                            item["launch_minecraft_uuid_yn"] = launch_minecraft_uuid_yn

            elif l_p_cil_input == "help":
                color.print(launch_page_str)
                color.print("[bright_blue]可用的游戏版本[/]")
                color.print(table)

            elif l_p_cil_input == "back":
                return 0

            else:
                color.print("[bold bright_red]不正确的输入,请重试.[/]")
                color.print(launch_page_str)
                color.print("[bright_blue]可用的游戏版本[/]")
                color.print(table)

    def downloads_minecraft_page():
        global game_dir
        with color.status("[red]请稍后...[/]"):
            version_name_dict = Core.core_start.core_Get_Version_list("LTS", "Latest")
            # try:
            #    get_version_json = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest_v2.json")
            # except Exception as e:
            #    logger.error(f"下载错误:{e}.{get_version_json.content}")
            #    try:
            #        get_version_json = requests.get("https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json")
            #    except Exception as e:
            #        logger.error(f"下载失败:{e}.{get_version_json.content}")
            #        raise ConsolesLaunchError("下载游戏失败:无法获取版本JSON")
            # get_version_json = get_version_json.json()
            # version_id = []
            # for item in get_version_json["versions"]:
            #    version_id.append(item)
            table = Table()
            table.add_column('[gold1] 序号')
            table.add_column('[bright_blue] 版本')
            version_id = 0
            version_name = []
            for item in version_name_dict:
                table.add_row("[gold1]{}[/]".format(version_id), "[bright_blue]{}[/]".format(item["id"]))
                version_name.append(item["id"])
                version_id += 1

        color.print(Panel(downloads_minecraft_page_str))
        color.print("[bright_white]输入序号或版本号进行选择[/]")
        d_m_p_xhkz = True
        while d_m_p_xhkz:
            d_m_p_input = input("Download_Minecraft{}".format(status_key))
            if d_m_p_input == "0" or d_m_p_input == "help":
                color.print(Panel(downloads_minecraft_page_str))
                color.print("[bright_white]输入序号或版本号进行选择[/]")

            elif d_m_p_input == "1" or d_m_p_input == "back":
                d_m_p_xhkz = False
                return 0

            elif d_m_p_input == "2" or d_m_p_input == "expand_versions":
                color.print(Panel(table))
                d_m_p_sel_xhkz = True
                while d_m_p_sel_xhkz:
                    color.print("[bright_white]输入back退出[/]")
                    d_m_p_sel_input = str(input("Download_Minecraft_Select{}".format(status_key)))
                    if d_m_p_sel_input in version_name:
                        Core.core_start.core_bootstrap_main(True, game_dir, d_m_p_sel_input, "BMCLAPI")

                    elif d_m_p_sel_input == "back":
                        d_m_p_sel_xhkz = False
                        d_m_p_xhkz = False
                        return 0

                    else:
                        color.print(Panel(table))
                        color.print("[bright_white]输入序号或版本号进行选择[/]")
                        color.print("[bold bright_red]不正确的输入,请重试.[/]")

            else:
                color.print(Panel(downloads_minecraft_page_str))
                color.print("[bright_white]输入序号或版本号进行选择[/]")
                color.print("[bold bright_red]不正确的输入,请重试.[/]")

    def MS_login_page():
        global minecraft_user_dict_list
        global status_key
        MS_l_p_xhkz = True
        while MS_l_p_xhkz:
            color.print("[bright_white]1.输入back返回[/]\n[bright_white]2.输入login登录[/]")
            MS_l_p_input = input("Microsoft Login{}".format(status_key))
            if MS_l_p_input == "login" or MS_l_p_input == "2":
                if platform.system() != "Windows":
                    webbrowser.open("https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf")
                    MS_l_p_back_url = input("请输入回调链接:")
                    ret_c_s_L = Core.core_start.core_start_Login(False, None, True, True, MS_l_p_back_url)
                    minecraft_user_dict_list.append({"username": ret_c_s_L["name_MS_xbox"], "uuid": ret_c_s_L["uuid_MS_xbox"], "access_token": ret_c_s_L["MinecraftAccessToken"], "R_T": ret_c_s_L["MS_T_back_R_T"], "minecraft_MS_Login_bit": True, "launch_minecraft_uuid_yn":True})
                else:
                    with color.status("[bright_blue]请稍后...[/]"):
                        ret_c_s_L = Core.core_start.core_start_Login(False, None, True, True)
                        minecraft_user_dict_list.append(
                            {
                             "username": ret_c_s_L["name_MS_xbox"],
                             "uuid": ret_c_s_L["uuid_MS_xbox"],
                             "access_token": ret_c_s_L["MinecraftAccessToken"],
                             "R_T": ret_c_s_L["MS_T_back_R_T"],
                             "minecraft_MS_Login_bit": True,
                             "launch_minecraft_uuid_yn": True
                            }
                            )
                    color.print("[bright_green]添加正版用户完成:[/][bright_blue]用户名:{}[/]".format(ret_c_s_L["name_MS_xbox"]))

            elif MS_l_p_input == "1" or MS_l_p_input == "back":
                MS_l_p_xhkz = False

            else:
                color.print("[bold bright_red]不正确的输入,请重试.[/]")

    def downloads_mods_page():
        pass

    def settings_page():
        set_p_xhkz = True
        while set_p_xhkz:
            color.print(settings_page_str)
            color.print("[gold1]Settings[/]", end="")
            set_p_input = input("{}".format(status_key))
            if set_p_input == "2" or set_p_input == "Show_all_user":
                if not len(minecraft_user_dict_list) == 0:
                    with color.status("[bright_blue]请稍后...[/]"):

                        table = Table()
                        table.add_column('[gold1] 序号')
                        table.add_column('[bright_blue] 用户名')
                        table.add_column('[bright_blue] 是否为正版账号')
                        table.add_column('[bright_blue] uuid')
                        table.add_column('[bright_yellow] Access_Token')
                        table.add_column('[bright_yellow] Refresh_Token')

                        set_p_userlist_i = 0
                        for item in minecraft_user_dict_list:
                            if item["minecraft_MS_Login_bit"]:
                                MS_or_offline_Login_bit_str = "正版账户"
                                AT_str_on_str = "******"
                                R_T_str_on_str = "******"
                            else:
                                MS_or_offline_Login_bit_str = "离线账户"
                                AT_str_on_str = "离线账户,无AccessToken"
                                R_T_str_on_str = "离线账户,无Refresh_Token"

                            table.add_row(str(set_p_userlist_i), item["username"], MS_or_offline_Login_bit_str, item["uuid"], AT_str_on_str, R_T_str_on_str)
                            set_p_userlist_i += 1

                    color.print(table)
                else:
                    color.print("[bold bright_red]您没有登录任何账户[/]")

            elif set_p_input == "3" or set_p_input == "show_MS_user_accesstoken_r_t":
                if not len(minecraft_user_dict_list) == 0:
                    with color.status("[bright_blue]请稍后...[/]"):
                        table = Table()
                        table.add_column('[gold1] 序号')
                        table.add_column('[bright_blue] 用户名')
                        table.add_column('[bright_blue] uuid')
                        table.add_column('[bright_yellow] Access_Token')

                        set_p_userlist_i = 0
                        set_p_userlist_for_true_i = 0
                        for item in minecraft_user_dict_list:
                            set_p_userlist_for_true_i += 1
                            if item["minecraft_MS_Login_bit"]:
                                print(1)
                                AT_str_on_str = item["access_token"]
                                R_T_str_on_str = item["R_T"]
                            else:
                                if set_p_userlist_i == 0 and set_p_userlist_for_true_i != 1:
                                    color.print("[bold bright_red]您没有登录任何正版账户[/]")
                                    break

                                continue

                            table.add_row(str(set_p_userlist_i), item["username"], item["uuid"], AT_str_on_str, R_T_str_on_str)
                            color.print("[bright_white]序号:[/][gold1]{0}[/]\n[bright_white]用户名:[/][gold1]{1}[/]\n[bright_white]AccessToken:[/][gold1]{2}[/]\n[bright_white]RefreshToken:[/][gold1]{3}[/]".format(str(set_p_userlist_i), item["username"], AT_str_on_str, R_T_str_on_str))
                            set_p_userlist_i += 1

                else:
                    color.print("[bold bright_red]您没有登录任何账户[/]")

            elif set_p_input == "4" or set_p_input == "add_offline_user":
                color.print("[bright_blue]请输入用户名[/]", end="")
                minecraft_username = input("{}".format(status_key))
                launch_minecraft_uuid_yn = False
                while True:
                    color.print("[bright_blue]请输入uuid(为空自动生成)[/]", end="")
                    minecraft_uuid = input("{}".format(status_key))
                    if len(minecraft_uuid) == 0:
                        launch_minecraft_uuid_yn = False
                        break
                    elif not len(minecraft_uuid) == 32:
                        color.print("[bold bright_red]此UUID可能不标准.请重试(长度应为32位,实际只有{}位)[/]".format(len(minecraft_uuid)))
                    else:
                        launch_minecraft_uuid_yn = True
                        break

                minecraft_user_dict_list.append(
                    {
                     "username": minecraft_username,
                     "uuid": minecraft_uuid,
                     "access_token": None,
                     "R_T": None,
                     "minecraft_MS_Login_bit": False,
                     "launch_minecraft_uuid_yn": launch_minecraft_uuid_yn
                     }
                )
                color.print("[bright_green]添加离线账户完成:[/][bright_white]用户名为:[/][gold1]{}[/]".format(minecraft_username))

            elif set_p_input == "5" or set_p_input == "add_online_user":
                MS_login_page()

            elif set_p_input == "6" or set_p_input == "select_user" or set_p_input == "sel":
                global minecraft_user_dict
                if len(minecraft_user_dict_list) != 0:
                    with color.status("[bright_blue]请稍后...[/]"):

                        table = Table()
                        table.add_column('[gold1] 序号')
                        table.add_column('[bright_blue] 用户名')
                        table.add_column('[bright_blue] 是否为正版账号')
                        table.add_column('[bright_blue] uuid')
                        table.add_column('[bright_yellow] Access_Token')
                        table.add_column('[bright_yellow] Refresh_Token')

                        set_p_userlist_i = 0
                        for item in minecraft_user_dict_list:
                            if item["minecraft_MS_Login_bit"]:
                                MS_or_offline_Login_bit_str = "正版账户"
                                AT_str_on_str = "******"
                                R_T_str_on_str = "******"
                            else:
                                MS_or_offline_Login_bit_str = "离线账户"
                                AT_str_on_str = "离线账户,无AccessToken"
                                R_T_str_on_str = "离线账户,无Refresh_Token"

                            table.add_row(str(set_p_userlist_i), item["username"], MS_or_offline_Login_bit_str,
                                          item["uuid"], AT_str_on_str, R_T_str_on_str)
                            set_p_userlist_i += 1

                    color.print(table)
                    while True:
                        color.print("[bright_blue]请输入用户名[/]", end="")
                        minecraft_username = input("{}".format(status_key))
                        minecraft_user_sel = False
                        for item in minecraft_user_dict_list:
                            if item["username"] == minecraft_username:
                                minecraft_user_dict = item
                                minecraft_user_sel = True
                                break
                        if minecraft_user_sel:
                            color.print("[bright_green]选择账户完成:[/][bright_white]用户名为:[/][gold1]{}[/]".format(minecraft_username))
                            break
                        else:
                            color.print("[bold bright_red]选择账户失败,未找到此账户.[/]")

                else:
                    color.print("[bold bright_red]您没有登录任何账户,请先添加账户.[/]")

            elif set_p_input == "0" or set_p_input == "help":
                color.print(settings_page_str)

            elif set_p_input == "1" or set_p_input == "back":
                set_p_xhkz = False
                return 0
            else:
                color.print("[bold bright_red]不正确的输入,请重试.[/]")

    def install_Forge_ModLauncher():
        global game_dir
        global launcher_name_version

        global status_key
        with color.status("[red]Working...[/]"):
            if game_dir is None:
                color.print("[bright_red]Forge安装失败.请先设置或初始化文件夹[/]")
                raise ConsolesLaunchError("Forge安装失败.没有.minecraft文件夹")

            ret = get_dir_name(os.path.join(game_dir, "versions"))
            if len(ret) == 0:
                color.print("[bright_red]Forge安装失败:没有可用的游戏[/]")
                raise ConsolesLaunchError("Forge安装失败:没有可用的游戏")

            table = Table()
            table.add_column('[gold1] 序号')
            table.add_column('[bright_blue] 版本')

            l_p_i = 0
            launch_version_dict_list = []
            launch_version_list = []
            launch_version_ser_num_list = []
            for item in ret:
                table.add_row('[gold1]{}[/]'.format(l_p_i), "[bright_blue]{}[/]".format(item))
                launch_version_dict_list.append({"ser_num": l_p_i, "version_name": item})
                launch_version_list.append(item)
                launch_version_ser_num_list.append(l_p_i)
                l_p_i += 1

        color.print(launch_page_str)
        color.print("[bright_blue]可用的游戏版本[/]")
        color.print(table)
        color.print("[bright_white]输入序号或版本号进行选择[/]")

        l_p_input_while = True
        while l_p_input_while:
            color.print("[bright_blue]Forge_install[/]")
            l_p_cil_input = input("{}".format(status_key))
            # 注意:这里input的返回是str,launch_version_ser_num_list中的数是int
            try:
                int_l_p_cil_input = int(l_p_cil_input)
            except ValueError as VE:
                logger.info(f"{VE}")
                int_l_p_cil_input = None

            if int_l_p_cil_input in launch_version_ser_num_list or l_p_cil_input in launch_version_list:  # 如果l_p_cil_input在launch_version_ser_num_list或launch_version_list中

                if int(l_p_cil_input) in launch_version_ser_num_list:  # 如果输入的是序号,那么:
                    launch_version_name = launch_version_list[int(l_p_cil_input)]
                else:  # 如果输入的是版本号
                    launch_version_name = l_p_cil_input  # 直接将版本号给lauch_version_name

                color.print("[bright_blue]准备安装Forge.游戏版本为:{}[/]".format(launch_version_name))
                try:
                    ret_install_Forge = Core.core_start.core_Forge_install_clint(launch_version_name, game_dir, False, "latest")
                except Core.core_start.CoreForgeInstallError as CFIE:
                    logger.error(f"{CFIE}")
                    raise ConsolesLaunchError(f"{CFIE}")

                if ret_install_Forge == 0:
                    color.print("[bright_green]{} 安装Forge完成".format(launch_version_name))

            elif l_p_cil_input == "help":
                color.print(launch_page_str)
                color.print("[bright_blue]可用的游戏版本[/]")
                color.print(table)

            elif l_p_cil_input == "back":
                return 0

            else:
                color.print("[bold bright_red]不正确的输入,请重试.[/]")
                color.print(launch_page_str)
                color.print("[bright_blue]可用的游戏版本[/]")
                color.print(table)

    def net_page(n_p_cil_input):
        if "net" in n_p_cil_input:
            print(n_p_cil_input[4:])

    # main
    color.rule("[bold red]Console SMCL")
    color.print("此为实验性功能,后续是否保留可能不确定", style="white on bright_blue")
    color.print(Panel(f"{help_page}"))

    while True:
        global status_key
        global a_s_bit

        cil_input = input(status_key)
        if cil_input == "exit" or cil_input == "1":
            sys.exit()

        elif cil_input == "help" or cil_input == "0":
            # 加上一句“好吧,那就再告诉你一遍。这次可不准忘记了！” ？(人性化优化选项)
            color.print(Panel(f"{help_page}"))

        elif cil_input == "Mod Search" or cil_input == "2":
            mod_search()

        elif cil_input == "init" or cil_input == "3":
            init_page()

        elif cil_input == "launch" or cil_input == "4":
            try:
                launch_page()
            except ConsolesLaunchError as CLE:
                logger.error(CLE)

        elif cil_input == "downloads_minecraft" or cil_input == "5":
            try:
                downloads_minecraft_page()
            except ConsolesLaunchError as CLE:
                logger.error(CLE)

        elif cil_input == "Settings" or cil_input == "6":
            settings_page()

        elif cil_input == "" or cil_input == "7":
            # 可以把这个单独做一个ModLauncher安装界面
            try:
                install_Forge_ModLauncher()
            except ConsolesLaunchError as CLE:
                logger.error(CLE)

        elif cil_input == "advanced_settings" or cil_input == "高级设置ver001":
            advanced_settings_page()

        elif cil_input == "net" and a_s_bit:
            net_page(cil_input)

        else:
            color.print("[bold red]指令不正确,输入help查看帮助页面[/]")
