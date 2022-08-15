import os
import json

# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
# Chrome/54.0.2840.99 Safari/537.36"}


def _read_json_file(read_json_file_src):
    with open(read_json_file_src, mode='r') as f:
        data = f.read(-1)
        read_json_file_json = json.loads(data)
        f.close()
    return read_json_file_json


class CoreBootstrapMainError(Exception):
    def __init__(self, message):
        super().__init__(message)


def core_start_IN(java_path, mc_path, G1NewSizePercent_size, G1ReservePercent_size, launcher_name, launcher_version,
                  client_jar_path, username, gameversion, assets_index_path, assets_index_name, uuid_val, aT,
                  launcher_name_self, cph):  # java_path以后可以升个级作判断，自己检测Java
    """
        java_path:Java路径（字符串）（可以填写java)
        mc_path:游戏目录（到.minecraft）
        G1NewSizePercent_size:20（字符串）
        G1ReservePercent_size：20（字符串）
        launcher_name：启动的版本名（字符串）
        launcher_version：启动的客户端版本（字符串）
        client_jar_path：客户端路径（版本隔离）（字符串）
        username:玩家名（字符串）
        gameversion：游戏版本（字符串）
        assets_index_path：资源索引文件所在文件夹路径
        assets_index_name:一般为1.12这种形式
        uuid_val：uuid(字符串)
        aT:accessToken位，用于正版登录。一般随便填（盗版登录）（字符串）
        launcher_name_self：启动器名（未使用，默认为SMCL DEV 0.0.1)
        cph:此位保留，无用处。不返回。可填None.
    """
    # G1NewSizePercent_size 传入值是字符串类型（默认20）#以后可以改为int,在这个函数内进行转换
    # G1ReservePercent_size 传入值是字符串类型（默认20）#以后可以改为int,在这个函数内进行转换

    try:

        with open(os.path.join(mc_path, 'versions', launcher_version, launcher_version) + ".json", mode='r') as f:
            data = f.read(-1)
        start_json = json.loads(data)

    except FileNotFoundError as e:

        raise CoreBootstrapMainError("错误, 无法找到描述文件, 请检查您的安装")

    assets_Index_sh1 = start_json['assetIndex']['sha1']
    assets_Index_id = start_json['assetIndex']['id']
    assets_Index_download_url = start_json['assetIndex']["url"]
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

    lib_path = os.path.join(mc_path, "libraries")
    i = 0

    for item in library_download_list:
        i = i + 1
        downloads_things_list.append(item["downloads"])

    for item in downloads_things_list:
        i = i + 1

        try:

            downloads_artifact_inlib_list.append(item["artifact"]["path"])
            downloads_artifact_url_inlib_list.append(item["artifact"]["url"])

        except KeyError as e:

            try:

                if run_time_environment == 'nt':

                    downloads_natives_sha1_list.append(item["classifiers"]["natives-windows"]["sha1"])
                    downloads_natives_path_list.append(item["classifiers"]["natives-windows"]["path"])
                    downloads_natives_url_list.append(item["classifiers"]["natives-windows"]["url"])

                else:

                    downloads_natives_list.append(item["classifiers"])

            except KeyError as e:

                raise CoreBootstrapMainError(
                    "错误,未定义的数据.In " + assets_index_name + ".json. It doesn't have classifiers or the mojang update?")

    temp_1 = java_path + " -Dfile.encoding=GB18030 -Dminecraft.client.jar=" + client_jar_path + "\\" + gameversion + ".jar" + " -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=" + G1NewSizePercent_size + \
             " -XX:G1ReservePercent=" + G1ReservePercent_size + \
             " -XX:MaxGCPauseMillis=50" + \
             " -XX:G1HeapRegionSize=16m" + \
             " -XX:-UseAdaptiveSizePolicy" + \
             " -XX:-OmitStackTraceInFastThrow" + \
             " -XX:-DontCompileHugeMethods" + \
             " -Xmn128m" + \
             " -Xmx2238m" + \
             " -Dfml.ignoreInvalidMinecraftCertificates=true" + \
             " -Dfml.ignorePatchDiscrepancies=true" + \
             " -Djava.rmi.server.useCodebaseOnly=true" + \
             " -Dcom.sun.jndi.rmi.object.trustURLCodebase=false" + \
             " -Dcom.sun.jndi.cosnaming.object.trustURLCodebase=false" + \
             " -Dlog4j2.formatMsgNoLookups=true" + \
             " -Dlog4j.configurationFile=" + client_jar_path + "\\" + "log4j2.xml" + \
             " -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump " + \
             "-Djava.library.path=" + nat_dir + \
             " -Dminecraft.launcher.brand=" + "SMCL-DEV" + \
             " -Dminecraft.launcher.version=" + "v0.0.1" + \
             " -cp "

    temp_2 = temp_1

    for downloads_artifact_inlib in downloads_artifact_inlib_list:
        temp_2 = temp_2 + (os.path.join(lib_path, (downloads_artifact_inlib.replace("/", "\\")) + ";"))

    the_temp = "\\"

    temp_3 = client_jar_path + the_temp + gameversion + ".jar" + " net.minecraft.client.main.Main" + " --username " + username + " --version " + gameversion + " --gameDir " + mc_path + \
             " --assetsDir " + assets_index_path + \
             " --assetIndex " + assets_index_name + \
             " --uuid " + uuid_val + \
             " --accessToken " + aT + \
             " --userType Legacy" + \
             ' --versionType "SMCL Lite"	'  # +launcher_name_self+\
    " --width 854"
    " --height 480"

    os.system(temp_2 + temp_3)  # 启动
    return temp_2 + temp_3  # 返回启动参数
