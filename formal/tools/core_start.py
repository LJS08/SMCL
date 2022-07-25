import os
import sys
import logging
import json
import hashlib
import requests


# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}

def core_start_IN(java_path, mc_path, G1NewSizePercent_size, G1ReservePercent_size, launcher_name, launcher_version):#java_path以后可以升个级作判断，自己检测Java
	# G1NewSizePercent_size 传入值是字符串类型（默认20）#以后可以改为int,在这个函数内进行转换
	# G1ReservePercent_size 传入值是字符串类型（默认20）#以后可以改为int,在这个函数内进行转换
	return java_path+" -Dfile.encoding=GB18030 -Dminecraft.client.jar="+mc_path+"\versions\1.12.2\1.12.2.jar -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent="+G1NewSizePercent_size+\
	"-XX:G1ReservePercent="+G1ReservePercent_size+\
	" -XX:MaxGCPauseMillis=50"+\
	" -XX:G1HeapRegionSize=16m"+\
	" -XX:-UseAdaptiveSizePolicy"+\
	" -XX:-OmitStackTraceInFastThrow"+\
	" -XX:-DontCompileHugeMethods"+\
	" -Xmn128m"+\
	" -Xmx2238m"+\
	" -Dfml.ignoreInvalidMinecraftCertificates=true"+\
	" -Dfml.ignorePatchDiscrepancies=true"+\
	" -Djava.rmi.server.useCodebaseOnly=true"+\
	" -Dcom.sun.jndi.rmi.object.trustURLCodebase=false"+\
	" -Dcom.sun.jndi.cosnaming.object.trustURLCodebase=false"+\
	"-Dlog4j2.formatMsgNoLookups=true"+\
	" -Dlog4j.configurationFile="+mc_path+"\versions\1.12.2\log4j2.xml"+\
	" -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump "+\
	"-Djava.library.path=E:\HMCLminecraft\.minecraft\versions\1.12.2\natives-windows-x86_64"+\
	" -Dminecraft.launcher.brand="+launcher_name+\
	"-Dminecraft.launcher.version="+launcher_version+\
	" -cp "+\
	mc_path+"\libraries\net\minecraftforge\forge\1.12.2-14.23.5.2860\forge-1.12.2-14.23.5.2860.jar;"+\
	mc_path+"\libraries\org\ow2\asm\asm-debug-all\5.2\asm-debug-all-5.2.jar; "+\
	mc_path+"\libraries\net\minecraft\launchwrapper\1.12\launchwrapper-1.12.jar;"+\
	mc_path+"\libraries\org\jline\jline\3.5.1\jline-3.5.1.jar;"+\
	mc_path+"\libraries\com\typesafe\akka\akka-actor_2.11\2.3.3\akka-actor_2.11-2.3.3.jar;"+\
	mc_path+"\libraries\com\typesafe\config\1.2.1\config-1.2.1.jar;"+\
	mc_path+"\libraries\org\scala-lang\scala-actors-migration_2.11\1.1.0\scala-actors-migration_2.11-1.1.0.jar;"+\
	mc_path+"\libraries\org\scala-lang\scala-compiler\2.11.1\scala-compiler-2.11.1.jar;"+\
	mc_path+"\libraries\org\scala-lang\plugins\scala-continuations-library_2.11\1.0.2_mc\scala-continuations-library_2.11-1.0.2_mc.jar;"+\
	mc_path+"\libraries\org\scala-lang\plugins\scala-continuations-plugin_2.11.1\1.0.2_mc\scala-continuations-plugin_2.11.1-1.0.2_mc.jar;"+\
	mc_path+"\libraries\org\scala-lang\scala-library\2.11.1\scala-library-2.11.1.jar;"+\
	mc_path+"\libraries\org\scala-lang\scala-parser-combinators_2.11\1.0.1\scala-parser-combinators_2.11-1.0.1.jar;"+\
	mc_path+"\libraries\org\scala-lang\scala-reflect\2.11.1\scala-reflect-2.11.1.jar;"+\
	mc_path+"\libraries\org\scala-lang\scala-swing_2.11\1.0.1\scala-swing_2.11-1.0.1.jar;"+\
	mc_path+"\libraries\org\scala-lang\scala-xml_2.11\1.0.2\scala-xml_2.11-1.0.2.jar;"+\
	mc_path+"\libraries\lzma\lzma\0.0.1\lzma-0.0.1.jar;"+\
	mc_path+"\libraries\java3d\vecmath\1.5.2\vecmath-1.5.2.jar;"+\
	mc_path+"\libraries\net\sf\trove4j\trove4j\3.0.3\trove4j-3.0.3.jar;"+\
	mc_path+"\libraries\org\apache\maven\maven-artifact\3.5.3\maven-artifact-3.5.3.jar;"+\
	mc_path+"\libraries\net\sf\jopt-simple\jopt-simple\5.0.3\jopt-simple-5.0.3.jar;"+\
	mc_path+"\libraries\org\apache\logging\log4j\log4j-api\2.15.0\log4j-api-2.15.0.jar;"+\
	mc_path+"\libraries\org\apache\logging\log4j\log4j-core\2.15.0\log4j-core-2.15.0.jar;"+\
	mc_path+"\.minecraft\libraries\com\mojang\patchy\1.3.9\patchy-1.3.9.jar;"+\
	mc_path+"\libraries\oshi-project\oshi-core\1.1\oshi-core-1.1.jar;"+\
	mc_path+"\libraries\net\java\dev\jna\jna\4.4.0\jna-4.4.0.jar;"+\
	mc_path+"\libraries\net\java\dev\jna\platform\3.4.0\platform-3.4.0.jar;"+\
	mc_path+"\libraries\com\ibm\icu\icu4j-core-mojang\51.2\icu4j-core-mojang-51.2.jar;"+\
	mc_path+"\libraries\com\paulscode\codecjorbis\20101023\codecjorbis-20101023.jar;"+\
	mc_path+"\libraries\com\paulscode\codecwav\20101023\codecwav-20101023.jar;"+\
	mc_path+"\libraries\com\paulscode\libraryjavasound\20101123\libraryjavasound-20101123.jar;"+\
	mc_path+"\libraries\com\paulscode\librarylwjglopenal\20100824\librarylwjglopenal-20100824.jar;"+\
	mc_path+"\libraries\com\paulscode\soundsystem\20120107\soundsystem-20120107.jar;"+\
	mc_path+"\libraries\io\netty\netty-all\4.1.9.Final\netty-all-4.1.9.Final.jar;"+\
	mc_path+"\libraries\com\google\guava\guava\21.0\guava-21.0.jar;"+\
	"E:\HMCLminecraft\.minecraft\libraries\org\apache\commons\commons-lang3\3.5\commons-lang3-3.5.jar;"+\
	mc_path+"\libraries\commons-io\commons-io\2.5\commons-io-2.5.jar;E:\HMCLminecraft\.minecraft\libraries\commons-codec\commons-codec\1.10\commons-codec-1.10.jar;"+\
	mc_path+"\libraries\net\java\jinput\jinput\2.0.5\jinput-2.0.5.jar;"+\
	mc_path+"\libraries\net\java\jutils\jutils\1.0.0\jutils-1.0.0.jar;"+\
	mc_path+"\libraries\com\google\code\gson\gson\2.8.0\gson-2.8.0.jar;"+\
	mc_path+"\libraries\com\mojang\authlib\1.5.25\authlib-1.5.25.jar;"+\
	mc_path+"\libraries\com\mojang\realms\1.10.22\realms-1.10.22.jar;"+\
	mc_path+"\libraries\org\apache\commons\commons-compress\1.8.1\commons-compress-1.8.1.jar;"+\
	mc_path+"\libraries\org\apache\httpcomponents\httpclient\4.3.3\httpclient-4.3.3.jar;"+\
	mc_path+"\libraries\commons-logging\commons-logging\1.1.3\commons-logging-1.1.3.jar;"+\
	mc_path+"/libraries/orgapache/httpcomponents/httpcore/4.3.2/httpcore-4.3.2.jar;"+\
	mc_path+"/libraries/it/unimi/dsi/fastutil/7.1.0/fastutil-7.1.0.jar;"+\
	mc_path+"/libraries/org/lwjgl/lwjgl/lwjgl/2.9.4-nightly-20150209/lwjgl-2.9.4-nightly-20150209.jar;"+\
	mc_path+"/libraries/org/lwjgl/lwjgl/lwjgl_util/2.9.4-nightly-20150209/lwjgl_util-2.9.4-nightly-20150209.jar;"+\
	mc_path+"/libraries/com/mojang/text2speech/1.10.3/text2speech-1.10.3.jar;"+\
	mc_path+"/versions/1.12.2/1.12.2.jar"+\
	" -javaagent:"+\
	" net.minecraft.launchwrapper.Launch "+\
	"--tweakClass "+game_mode_launcher+\
	"--username "+username
	"--version "+game_version
	"--gameDir "+mc_path+'/'+\
	"--assetsDir "+mc_path+"/assets"
	"--assetIndex "+1.12
	"--uuid "+uuid_val
	"--accessToken "+accessToken_val
	"--userType, "+game_Type_use
	"--versionType"+Forge # 启动器版本，不知道为什么使用Forge时就不写启动器名了。。。
	"--width "+width_val+\
	"--height, 480"
# C:\Users\刘志军\AppData\Roaming\.hmcl\log4j-patch-agent-1.0.jar=false
	# net.minecraftforge.fml.common.launcher.FMLTweaker
	# 启动器版本，不知道为什么使用Forge时就不写启动器名了。。。


def _downloads_file_url(file_url, downloads_file_url_src):
	downloads_file_url_response = requests.get(file_url)
	with open(downloads_file_url_src, "wb") as f:
		f.write(downloads_file_url_response.content)
		f.close()


def _read_json_file(read_json_file_src):
	with open(read_json_file_src, mode='r') as f:
		data = f.read(-1)
		read_json_file_json = json.loads(data)
		f.close()
	return read_json_file_json


class CoreBootstrapMainError(Exception):
	def __init__(self,message):
		super().__init__(message)


def _encrypt(fpath: str, algorithm: str) -> str:#https://blog.csdn.net/qq_42951560/article/details/125080544
	with open(fpath, 'rb') as f:
		return hashlib.new(algorithm, f.read()).hexdigest()


def _hash_get_val(hash_file_src,hash_need_type):
	'''hash_need_type是想要得到的hash值的类型(字符串)，只有sha1,sha256.md5.hash_file_src是需要得到hash值的文件的路径（字符串）'''
	for algorithm in ('md5', 'sha1', 'sha256'):# https://blog.csdn.net/qq_42951560/article/details/125080544
		hexdigest = _encrypt(hash_file_src, algorithm)
		# print(f'{algorithm}: {hexdigest}')
		# 第一次为MD5，第二次为sha1,第三次为sha256
		if algorithm == hash_need_type:
			return hexdigest


def core_bootstrap_main(selfup, mc_path, jar_version, link_type):
	if link_type == "mojang" or link_type is None:

		link_downloads_version_manifest = "http://launchermeta.mojang.com/mc/game/version_manifest.json"
		link_downloads_snapshot_manifest = "http://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
		link_downloads_launchermeta = "https://launchermeta.mojang.com/"
		link_downloads_launcher = "https://launcher.mojang.com/"
		link_downloads_assets = "http://resources.download.minecraft.net/"
		link_downloads_libraries = "https://libraries.minecraft.net/"
		link_downloads_Mojang_java = "https://launchermeta.mojang.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json"
		link_downloads_forge = "https://files.minecraftforge.net/maven"
		link_downloads_liteloader = "http://dl.liteloader.com/versions/versions.json"
		link_downloads_authlib_injector = "https://authlib-injector.yushi.moe"
		link_downloads_fabric_meta = "https://meta.fabricmc.net"
		link_downloads_maven = "https://maven.fabricmc.net"

	elif link_type == "BMCLAPI":

		link_downloads_version_manifest = "https://bmclapi2.bangbang93.com/mc/game/version_manifest.json"
		link_downloads_snapshot_manifest = "https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json"
		link_downloads_launchermeta = "https://launchermeta.mojang.com/"
		link_downloads_launcher = "https://launcher.mojang.com/"
		link_downloads_assets = "http://resources.download.minecraft.net/"
		link_downloads_libraries = "https://libraries.minecraft.net/"
		link_downloads_Mojang_java = "https://launchermeta.mojang.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json"
		link_downloads_forge = "https://files.minecraftforge.net/maven"
		link_downloads_liteloader = "http://dl.liteloader.com/versions/versions.json"
		link_downloads_authlib_injector = "https://authlib-injector.yushi.moe"
		link_downloads_fabric_meta = "https://meta.fabricmc.net"
		link_downloads_maven = "https://maven.fabricmc.net"

	if selfup:
		running_src = os.getcwd()
		if os.path.isfile(os.path.join(mc_path, "version", jar_version, ".jar")):
			print("主游戏文件:存在")
		else:
			print("主游戏文件:不存在")
			print("正在下载")


		print("正在预加载:配置文档")
		try:
			with open(mc_path+'\\versions\\1.12.2\\1.12.2.json', mode='r') as f:
				data = f.read(-1)
			start_json = json.loads(data)
		except FileNotFoundError as e:
			print("预加载配置文档失败")
			raise CoreBootstrapMainError("错误, 无法找到描述文件, 请检查您的安装")

		assert_Index_sh1 = start_json['assetIndex']['sha1']
		assert_Index_id = start_json['assetIndex']['id']
		assert_Index_download_url = start_json['assetIndex']["url"]
		assert_index_path = os.path.join(mc_path, "assets\\indexes\\")    # 拼接index文件夹路径
		assert_objects_path = os.path.join(mc_path, "assets\\objects\\")
		print(assert_index_path)
		if os.path.isdir(assert_index_path):
			pass
		else:
			os.chdir(os.path.join(mc_path, "assets"))
			os.mkdir("indexes")

		file_index_objects = os.path.isfile(assert_index_path + assert_Index_id + ".json")    # 1.12.json文件是否存在?
		if file_index_objects:  # 如果file_index_objects的值为真（1.12.json存在的情况）
			sha1_json = _hash_get_val(assert_index_path + assert_Index_id + ".json", 'sha1')
			# 获得index中的1.12.json的hash(sha1)
			if assert_Index_sh1 == sha1_json:   # 如果文件的sha1值正常
				ret_read_json_val = _read_json_file(os.path.join(assert_index_path, "1.12.json"))
				# 获得1.12.json文件中的内容并序列化为字典
				assert_json_objects = ret_read_json_val["objects"]["icons/icon_16x16.png"]["hash"]
				assert_json_objects[0:2]
				_downloads_file_url(link_downloads_assets + assert_json_objects[0:2] + "/" + assert_json_objects, )

			else:
				os.chdir(assert_index_path)

		else:       # 1.12.json不存在的情况
			os.chdir(assert_index_path)
			response = requests.get(assert_Index_download_url)
			with open(assert_Index_id + ".json", "wb") as f:
				f.write(response.content)
				f.close()
			sha1_json_else = _hash_get_val(assert_index_path + assert_Index_id + ".json", 'sha1') # 获得index中的1.12.json的hash(sha1)
			hash_yn = 0
			while hash_yn == 0:
				if assert_Index_sh1 == sha1_json_else:
					hash_yn = 1
				else:
					os.chdir(assert_index_path)
					response = requests.get(assert_Index_download_url)
					with open(assert_Index_id + ".json", "wb") as f:
						f.write(response.content)
						f.close()
					sha1_json_else = _hash_get_val(assert_index_path + "1.12.json", 'sha1') # 获得index中的1.12.json的hash(sha1)

	else:
		pass


try:
	core_bootstrap_main(True, "D:\\smcl\\formal\\tools\\.minecraft", "1.12.2")
except CoreBootstrapMainError as e:
	print(e)
