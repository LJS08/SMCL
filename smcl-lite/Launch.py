import os
import json
import hashlib

# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}


def _read_json_file(read_json_file_src):
    with open(read_json_file_src, mode='r') as f:
        data = f.read(-1)
        read_json_file_json = json.loads(data)
        f.close()
    return read_json_file_json


class CoreBootstrapMainError(Exception):
    def __init__(self, message):
        super().__init__(message)


def _encrypt(fpath: str, algorithm: str) -> str:  # https://blog.csdn.net/qq_42951560/article/details/125080544
    with open(fpath, mode='rb') as f:
        return hashlib.new(algorithm, f.read()).hexdigest()





def core_start_IN(java_path, mc_path, launcher_name, username, uuid_val, aT, launcher_name_version,
                  G1NewSizePercent_size="20", G1ReservePercent_size="20", Xmn="128m", Xmx="1024M",
                  cph=None):  # java_path以后可以升个级作判断，自己检测Java
    """
		java_path:Java路径（字符串）（可以填写java)

		mc_path:游戏目录（到.minecraft）

		launcher_name：需要启动的游戏版本（字符串）

		username:玩家名（字符串）

		uuid_val：uuid(字符串)

		aT:accessToken位，用于正版登录。一般随便填（盗版登录）（字符串）

		launcher_name_version：启动器版本

		G1NewSizePercent_size:20（字符串）

		G1ReservePercent_size：20（字符串）

		Xmn:最小内存（默认128m）

		Xmx:最大分配内存（默认1024M)

		cph:此位保留，无用处。不返回。可填None.
"""
    # java_path:Java路径（字符串）（可以填写java)
    # mc_path:游戏目录（到.minecraft）
    # G1NewSizePercent_size:20（字符串）
    # G1ReservePercent_size：20（字符串）
    # launcher_name：需要启动的游戏版本（字符串）
    # launcher_version：启动的客户端版本（字符串）（被弃用）（等于launcher_name）
    # client_jar_path：客户端路径（版本隔离）（字符串）(被弃用）
    # username:玩家名（字符串）
    # gameversion：游戏版本（字符串）(被弃用）
    # assets_index_path：资源索引文件所在文件夹路径(被弃用）
    # assets_index_name:一般为1.12这种形式(被弃用）
    # uuid_val：uuid(字符串)
    # aT:accessToken位，用于正版登录。一般随便填（盗版登录）（字符串）
    # launcher_name_version：启动器版本
    # Xmn:最小内存（默认128m）
    # Xmx:最大分配内存（默认1024M)
    # cph:此位保留，无用处。不返回。可填None.
    # 这个版本还在写，仅为测试版本。原版启动正常，forge启动有问题。

    assets_index_path = os.path.join(mc_path, "assets")
    client_jar_path = os.path.join(mc_path, 'versions', launcher_name)
    launcher_version = launcher_name  # 这两个值相同
    gameversion = launcher_name
    # G1NewSizePercent_size 传入值是字符串类型（默认20）#以后可以改为int,在这个函数内进行转换
    # G1ReservePercent_size 传入值是字符串类型（默认20）#以后可以改为int,在这个函数内进行转换
    launcher_name_self = '"SMCL ' + launcher_name_version + '"'
    try:
        with open(os.path.join(mc_path, 'versions', launcher_version, launcher_version) + ".json", mode='r') as f:
            data = f.read(-1)
        start_json = json.loads(data)
    except FileNotFoundError as e:
        raise CoreBootstrapMainError("错误, 无法找到描述文件, 请检查您的安装")
    try:

        pathes_other = start_json["patches"]  # forge

    except KeyError as e:

        mod_loder = False

    assets_index_name = start_json["assets"]

    library_download_list = start_json["libraries"]
    nat_dir = os.path.join(mc_path, "versions", gameversion, "natives-windows-x86_64")
    downloads_things_list = []
    downloads_artifact_inlib_list = []
    downloads_natives_sha1_list = []
    downloads_natives_path_list = []
    downloads_natives_list = []
    downloads_natives_url_list = []
    run_time_environment = os.name
    downloads_artifact_url_inlib_list = []
    downloads_lib_name = []
    downloads_things_list_rules = []
    lib_path = os.path.join(mc_path, "libraries")
    i = 0
    for item in library_download_list:
        i = i + 1
        downloads_things_list.append(item["downloads"])

    # for item in downloads_things_list:
    # i = i + 1
    # try:
    i = 0
    for items in library_download_list:
        i = i + 1
        try:
            downloads_things_list_rules.append(items["rules"])
            if items["rules"][0]["os"]["name"] == "osx":
                pass
        except KeyError as e:
            try:
                downloads_artifact_inlib_list.append(items["downloads"]["artifact"]["path"])
                downloads_artifact_url_inlib_list.append(items["downloads"]["artifact"]["url"])
            except KeyError as e:
                print(e)

    # downloads_artifact_inlib_list.append(item["artifact"]["path"])
    # downloads_artifact_url_inlib_list.append(item["artifact"]["url"])
    # except KeyError as e:
    # try:
    # if run_time_environment == 'nt':
    # downloads_natives_sha1_list.append(item["classifiers"]["natives-windows"]["sha1"])
    # downloads_natives_path_list.append(item["classifiers"]["natives-windows"]["path"])
    # downloads_natives_url_list.append(item["classifiers"]["natives-windows"]["url"])
    # else:
    # downloads_natives_list.append(item["classifiers"])
    # except KeyError as e:
    # pass
    # raise CoreBootstrapMainError("错误,未定义的数据.In 1.12.2.json. It doesn't have classifiers or the mojang update?")

    print(downloads_things_list_rules)
    temp_1 = java_path + " -Dfile.encoding=GB18030 -Dminecraft.client.jar=" + client_jar_path + "\\" + gameversion + ".jar" + " -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=" + G1NewSizePercent_size + \
             " -XX:G1ReservePercent=" + G1ReservePercent_size + \
             " -XX:MaxGCPauseMillis=50" + \
             " -XX:G1HeapRegionSize=16m" + \
             " -XX:-UseAdaptiveSizePolicy" + \
             " -XX:-OmitStackTraceInFastThrow" + \
             " -XX:-DontCompileHugeMethods" + \
             " -Xmn" + Xmn + \
             " -Xmx" + Xmx + \
             " -Dfml.ignoreInvalidMinecraftCertificates=true" + \
             " -Dfml.ignorePatchDiscrepancies=true" + \
             " -Djava.rmi.server.useCodebaseOnly=true" + \
             " -Dcom.sun.jndi.rmi.object.trustURLCodebase=false" + \
             " -Dcom.sun.jndi.cosnaming.object.trustURLCodebase=false" + \
             " -Dlog4j2.formatMsgNoLookups=true" + \
             " -Dlog4j.configurationFile=" + client_jar_path + "\\" + "log4j2.xml" + \
             " -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump " + \
             "-Djava.library.path=" + nat_dir + \
             " -Dminecraft.launcher.brand=" + "SMCL" + \
             " -Dminecraft.launcher.version=" + "0.0.1" + \
             " -cp "
    temp_2 = temp_1
    if start_json["mainClass"] == "net.minecraft.client.main.Main":
        for downloads_artifact_inlib in downloads_artifact_inlib_list:
            temp_2 = temp_2 + (os.path.join(lib_path, (downloads_artifact_inlib.replace("/", "\\")) + ";"))
        print(downloads_artifact_inlib)
        the_temp = "\\"
        temp_3 = client_jar_path + the_temp + gameversion + ".jar" + " net.minecraft.client.main.Main" + " --username " + username + " --version " + gameversion + " --gameDir " + mc_path + \
                 " --assetsDir " + assets_index_path + \
                 " --assetIndex " + assets_index_name + \
                 " --uuid " + uuid_val + \
                 " --accessToken " + aT + \
                 " --userType Legacy" + \
                 ' --versionType ' + launcher_name_self + \
                 " --width 854" + \
                 " --height 480"
        os.system(temp_2 + temp_3)
        return "ok", temp_2 + temp_3

    elif start_json["mainClass"] == "cpw.mods.modlauncher.Launcher":
        argument_forge = []  # forge
        for item in pathes_other:  # forge
            if item["id"] == "forge":  # forge
                forge = item  # forge

        for item in forge["libraries"]:
            temp = item["name"]
            temp_split = temp.split(":")
            temp_split = temp_split[-1]
            temp = temp.replace(".", "\\", 1)
            temp = temp.replace(":", "\\")
            temp_2 = temp_2 + (os.path.join(lib_path, temp, temp_split) + ".jar" + ";")
            break
        print(temp_2)

        for downloads_artifact_inlib in downloads_artifact_inlib_list:
            if downloads_artifact_inlib == "":
                pass
            temp_2 = temp_2 + (os.path.join(lib_path, (downloads_artifact_inlib.replace("/", "\\")) + ";"))
        # print(downloads_artifact_inlib)
        the_temp = "\\"
        temp_3_t = client_jar_path + the_temp + gameversion + ".jar"

        for item in forge["arguments"]["jvm"]:
            temp_3_t = temp_3_t + " " + item

        temp_3 = temp_3_t + " cpw.mods.modlauncher.Launcher" + " --username " + username + " --version " + gameversion + " --gameDir " + mc_path + \
                 " --assetsDir " + assets_index_path + \
                 " --assetIndex " + assets_index_name + \
                 " --uuid " + uuid_val + \
                 " --accessToken " + aT + \
                 " --userType Legacy" + \
                 ' --versionType ' + launcher_name_self + \
                 " --width 854" + \
                 " --height 480"

        item_i = 0  # forge

        for item in forge["arguments"]["game"]:  # forge
            argument_forge.append(item)  # forge
            item_i += 1  # forge
        item_i = 0  # forge

        for item in argument_forge:  # forge
            temp_3 = temp_3 + " " + argument_forge[item_i] + " " + argument_forge[item_i + 1]  # forge
            item_i += 2  # forge
            # emm
            # 当第一次循环时 item_i = 0 所以是 0 1
            # 当第8次时实际访问的是 8 9
            # but 因为是+2
            # 所以可能会列表（数组）访问出界
            # 提示：列表是从0开始
            if item_i == 8:
                break

        return temp_2 + temp_3