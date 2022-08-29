from alive_progress import alive_bar
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.message import EmailMessage
import hashlib
import json
import loguru
import multiprocessing
import os
import requests
import sys
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as CService
import threading
import time
import uuid
import zipfile
import webbrowser


# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}


def calc_divisional_range(filesize, chuck=10):
	step = filesize // chuck
	arr = list(range(0, filesize, step))
	result = []
	for i in range(len(arr) - 1):
		s_pos, e_pos = arr[i], arr[i + 1] - 1
		result.append([s_pos, e_pos])
	result[-1][-1] = filesize - 1
	return result

# 下载方法


def range_download(downloads_file_url_src, s_pos, e_pos, url, mkfile):
	headers = {"Range": f"bytes={s_pos}-{e_pos}"}
	res = requests.get(url, headers=headers, stream=True)
	try:
		with open(downloads_file_url_src, mode="rb") as f:
			f.seek(s_pos)
			for chunk in res.iter_content(chunk_size=64 * 1024):
				if chunk:
					f.write(chunk)
			f.close()
	except FileNotFoundError as e:
		if mkfile:
			with open(downloads_file_url_src, mode="rb+") as f:
				f.seek(s_pos)
				for chunk in res.iter_content(chunk_size=64 * 1024):
					if chunk:
						f.write(chunk)
				f.close()
			return "OK"
		else:
			raise CoreBootstrapMainError("错误, 无法找到文件")


def _downloads_file_urls(file_url, downloads_file_url_src, mkfile):
	res = requests.head(file_url)
	filesize = int(res.headers['Content-Length'])
	divisional_ranges = calc_divisional_range(filesize)
	# 先创建空文件
	with ThreadPoolExecutor() as p:
		futures = []
		for s_pos, e_pos in divisional_ranges:
			print(s_pos, e_pos)
			futures.append(p.submit(range_download, file_url, s_pos, e_pos, downloads_file_url_src, mkfile))
		# 等待所有任务执行完毕
		as_completed(futures)

def _downloads_file_url_threading(file_url, downloads_file_url_src, mkfile):
	"""file_url 是链接地址。downloads_file_url_src 文件地址.mkfile 传参，在没有这个文件时决定是否创建此文件。多线程下载（新）"""
	# 老版单线程改名为_downloads_file_urls,传参不变
	e = threading.Event()

	def _downloads_help_things(start, end, file_url, downloads_file_url_src, mkfile):
		lock = threading.Lock()  # 初始化锁
		headers = {
			'Range': f'bytes={start}-{end}',
		}
		# 传递头，表明分段下载
		with requests.get(file_url, stream=True, headers=headers) as downloads_file_url_response:
			pos = start  # 文件指针就等于（pos）开始（start)
			for i in downloads_file_url_response.iter_content(chunk_size=1024, decode_unicode=True):  # 设置每次传输的大小r.content.decode(r.apparent_encoding)
				if i:  # 判断是否为空数据
					# decoded_i = i.decode('utf-8')	 # 将i转码（没用到）
					try:
						with open(downloads_file_url_src, mode="wb") as f:
							lock.acquire()  # 获得使用权
							f.seek(pos)
							f.write(i)
							lock.release()  # 释放使用权
					except FileNotFoundError as es:
						if mkfile:
							with open(downloads_file_url_src, mode="wb+") as f:
								lock.acquire()  # 获得使用权
								f.seek(pos)
								f.write(i)
								lock.release()  # 释放使用权
						else:
							raise CoreBootstrapMainError("错误, 无法找到文件")

				pos = pos + 1024  # 自增
		e.set()
	with requests.get(file_url, stream=True) as r2:		# 开启流式下载
		thread_num = multiprocessing.cpu_count() * 4	 # 线程数量
		size = int(r2.headers['Content-Length'])
		print(r2.headers['Content-Length'])
		global threads_downloads_file_url
		threads_downloads_file_url = []  # 记录线程号
		for i in range(thread_num):
			if i == thread_num - 1:
				t1 = threading.Thread(target=_downloads_help_things, args=(i * (size // thread_num), size, file_url, downloads_file_url_src, mkfile))
				t1.start()
				#t1.join()
				threads_downloads_file_url.append(t1)		# 将线程名添加到threads_downloads_file_url列表
			else:
				t1 = threading.Thread(target=_downloads_help_things, args=(i * (size // thread_num), (i + 1) * (size // thread_num), file_url, downloads_file_url_src, mkfile))
				t1.start()
				threads_downloads_file_url.append(t1)		# 将线程名添加到threads_downloads_file_url列表

		for thread in threads_downloads_file_url:		# 从threads_downloads_file_url列表中获得线程名，然后一个个join
			e.wait()
			thread.join()



def _downloads_hash_bugs(link_downloads_assets, Max_try, file_dir, downloads_file_url_where, back_dir, file_path_name, hash_need_mode, sha1_objects_else, hash_asserts_json_objects_hash_name):
	"""
	temp_link_downloads_assets是像http://resources.download.minecraft.net/的。
	Max_try 是最大尝试次数。
	file_dir 需要验证的文件所在的文件夹
	downloads_file_url_where 是下载参数
	back_dir 回到的目录
	file_path_name需要验证的文件所在的位置
	hash_need_mode获得hash码的格式（字符串）（sha1,md5,sha256)
	sha1_objects_else hash(外部算）
	hash_asserts_json_objects_hash_name 应该的hash值
	"""
	bmcl_link = link_downloads_assets
	hash_yn_too_many_try = 0
	hash_yn = 1
	while hash_yn == 0:
		hash_yn_too_many_try = hash_yn_too_many_try + 1
		if hash_yn_too_many_try >= 5:  # 如果验证失败超过五次那么就更改为官方源下载
			print("mojang")  # debug
			link_downloads_assets = "http://resources.download.minecraft.net/"  #temp_link_downloads_assets
		if hash_yn_too_many_try >= Max_try:
			raise CoreBootstrapMainError("验证资源文件时尝试次数过多")
		print(hash_yn_too_many_try)  # debug
		if hash_asserts_json_objects_hash_name == sha1_objects_else:
			hash_yn = 1  # 如果hash正确就跳出循环
		else:
			os.chdir(file_dir)  # 到达应该下载的目录
			_downloads_file_url(downloads_file_url_where)  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性。。。
			sha1_objects_else = _hash_get_val(file_path_name, hash_need_mode)  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。  # 获得objects中的资源文件的hash(sha1)
			os.chdir(back_dir)  # 返回objects目录
			print(sha1_objects_else)  # debug
	link_downloads_assets = bmcl_link  # 恢复为原来使用的源
	return "OK"


def _downloads_file_url(file_url, downloads_file_url_src, mkfile):
	"""file_url 是链接地址。downloads_file_url_src 文件地址.mkfile 传参，在没有这个文件时决定是否创建此文件（老版本）"""
	# 新版为_downloads_file_url多线程下载
	# 老版（改名了）(原名：_downloads_file_url）
	#
	# file_url 是链接地址
	# downloads_file_url_src 文件地址
	# mkfile 传参，在没有这个文件时决定是否创建此文件
	downloads_file_url_response = requests.get(file_url)
	try:
		with open(downloads_file_url_src, mode="wb") as f:
			f.write(downloads_file_url_response.content)
			f.close()
	except FileNotFoundError as e:
		if mkfile:
			with open(downloads_file_url_src, mode="wb+") as f:
				f.write(downloads_file_url_response.content)
				f.close()
			return "OK"
		else:
			raise CoreBootstrapMainError("错误, 无法找到文件")


def multprocessing_task(tasks, cores: int, join: bool = True):
	threads = []
	def _run():
		while threads:
			try:
				task = tasks.pop(0)
				print(task)
				task_download_url = task["url"]
				task_need_src = task["path"]
				task_need_mkfile = task["mkfile"]
				_downloads_file_url(task_download_url, task_need_src, task_need_mkfile)
				# function(task)
			except KeyError as ke:
				print(ke)
			except IndexError as IndexE:
				break
	for i in range(cores+1):
		thread = threading.Thread(target=_run)
		thread.start()
		threads.append(thread)
	if join:
		for thread in threads:
			thread.join()

def _read_json_file(read_json_file_src):
	with open(read_json_file_src, mode='r') as f:
		data = f.read(-1)
		read_json_file_json = json.loads(data)
		f.close()
	return read_json_file_json


class CoreBootstrapMainError(Exception):
	def __init__(self, message):
		super().__init__(message)


def _encrypt(fpath: str, algorithm: str) -> str:#https://blog.csdn.net/qq_42951560/article/details/125080544
	with open(fpath, mode='rb') as f:
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

	global link_downloads_launcher
	if link_type == "mojang" or link_type is None:		#使用mojang api

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

	elif link_type == "BMCLAPI":		# 使用BMCLAPI

		link_downloads_version_manifest = "https://bmclapi2.bangbang93.com/mc/game/version_manifest.json"
		link_downloads_snapshot_manifest = "https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json"
		link_downloads_launchermeta = "https://bmclapi2.bangbang93.com/"
		link_downloads_launcher = "https://bmclapi2.bangbang93.com/"
		link_downloads_assets = "https://bmclapi2.bangbang93.com/assets/"
		link_downloads_libraries = "https://bmclapi2.bangbang93.com/maven/"
		link_downloads_Mojang_java = "https://bmclapi2.bangbang93.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json"
		link_downloads_forge = "https://bmclapi2.bangbang93.com/maven/"
		link_downloads_liteloader = "https://bmclapi.bangbang93.com/maven/com/mumfrey/liteloader/versions.json"
		link_downloads_authlib_injector = "https://bmclapi2.bangbang93.com/mirrors/authlib-injector"
		link_downloads_fabric_meta = "https://bmclapi2.bangbang93.com/fabric-meta"
		link_downloads_maven = "https://bmclapi2.bangbang93.com/maven"

	elif link_type == "MCBBS":		# 使用MCBBS api
		pass

	else:		# 如果都不是就用mojang(重复？)
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

	if selfup:
		# global running_src
		running_src = os.getcwd()		# 获得当前工作目录
		CPU_CORE = multiprocessing.cpu_count()

		if os.path.isdir(os.path.join(mc_path, "versions", jar_version)):
			print("客户端目录：存在")
		else:
			print("客户端目录:不存在")
			print("正在创建")
			os.chdir(os.path.join(mc_path, "versions"))
			os.mkdir(jar_version)
			os.chdir(running_src)		# 返回工作目录

		if os.path.isfile(os.path.join(mc_path, "versions", jar_version, jar_version) + ".jar"):
			print("主游戏文件:存在")
		else:
			print("主游戏文件:不存在")
			print("正在下载,这可能需要一段时间")
			with alive_bar(len(range(100)), force_tty=True) as bar:	#这里没卵用，主要是因为没开异步
				for item in range(50):  # 遍历任务
					bar()		# 显示进度
					time.sleep(0.01)
				bar()
				_downloads_file_url(link_downloads_launcher + "version/" + jar_version + "/jar", os.path.join(mc_path, "versions", jar_version, jar_version) + ".jar", True)
				for item in range(30):  # 遍历任务
					bar()		# 显示进度
					time.sleep(0.000001)
				for item in range(19):  # 遍历任务
					bar()  # 显示进度
					time.sleep(0.1)
			print("下载完毕")

		if os.path.isfile(os.path.join(mc_path, "versions", jar_version, jar_version) + ".json"):
			print("配置文档:存在")
		else:
			print("配置文档:不存在")
			print("正在下载,这可能需要一段时间")
			_downloads_file_url(link_downloads_launcher + "version/" + jar_version + "/json", os.path.join(mc_path, "versions", jar_version, jar_version) + ".json", True)		# 下载JSON配置文件
			print("下载完毕")


		print("正在预加载:配置文档")
		try:
			with open(os.path.join(mc_path, 'versions', jar_version, jar_version) + ".json", mode='r') as f:
				data = f.read(-1)
			start_json = json.loads(data)
		except FileNotFoundError as e:
			print("预加载配置文档失败")
			raise CoreBootstrapMainError("错误, 无法找到描述文件, 请检查您的安装")

		assets_Index_sh1 = start_json['assetIndex']['sha1']
		assets_Index_id = start_json['assetIndex']['id']
		assets_Index_download_url = start_json['assetIndex']["url"]
		library_download_list = start_json["libraries"]
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
		if run_time_environment == 'nt':
			natives_path = os.path.join(mc_path, "versions", jar_version, "natives-windows-x86_64")
		i = 0
		for item in library_download_list:
			temp = item["name"]
			print(temp, temp.count("."))	# debug
			if temp.count(".") >= 3 and i == 0:
				t2 = temp.replace(".", "/", 1)
			if temp.count(".") == 1 and i == 1:	 # oshi-project:oshi-core:1.1
				pass
			if temp.count(".") == 1 and i == 1:
				pass
			downloads_lib_name.append(t2.replace(":", "/"))
			i = i + 1

		for item in library_download_list:
			i = i + 1
			downloads_things_list.append(item["downloads"])
		for item in downloads_things_list:
			i = i + 1
			try:
				print(item)
				downloads_artifact_inlib_list.append(item["artifact"]["path"])
				downloads_artifact_url_inlib_list.append(item["artifact"]["url"])

				if run_time_environment == 'nt':
					try:
						if item["natives"]["windows"] == "natives-windows":
							print(1)
							downloads_natives_sha1_list.append(item["classifiers"]["natives-windows"]["sha1"])
							downloads_natives_path_list.append(item["classifiers"]["natives-windows"]["path"])
							downloads_natives_url_list.append(item["classifiers"]["natives-windows"]["url"])
					except KeyError as KE:
						print(KE)

			except KeyError as e:
				try:
					if run_time_environment == 'nt':
						try:
							if item["natives"]["windows"] == "natives-windows":
								downloads_natives_sha1_list.append(item["classifiers"]["natives-windows"]["sha1"])
								downloads_natives_path_list.append(item["classifiers"]["natives-windows"]["path"])
								downloads_natives_url_list.append(item["classifiers"]["natives-windows"]["url"])
						except KeyError as KE:
							print(KE)

					else:
						downloads_natives_list.append(item["classifiers"])
				except KeyError as e:
					raise CoreBootstrapMainError("错误,未定义的数据.In 1.12.2.json. It doesn't have classifiers or the mojang update?")
		
		for item in library_download_list:
			if run_time_environment == 'nt':
				try:
					if item["natives"]["windows"] == "natives-windows":
						downloads_natives_sha1_list.append(item["downloads"]["classifiers"]["natives-windows"]["sha1"])
						downloads_natives_path_list.append(item["downloads"]["classifiers"]["natives-windows"]["path"])
						downloads_natives_url_list.append(item["downloads"]["classifiers"]["natives-windows"]["url"])
				except KeyError as KE:
					print(KE)
		#print(downloads_artifact_inlib_list)
		#print(downloads_natives_list)		# 此列表被移除但未更改
		#print(downloads_lib_name)
		print(downloads_natives_path_list)
		print(run_time_environment)
		# 本来想把lib下载放在这里

		assets_index_path = os.path.join(mc_path, "assets\\indexes\\")    # 拼接index文件夹路径
		assets_objects_path = os.path.join(mc_path, "assets\\objects\\")

		if os.path.isdir(assets_index_path):		# indexes文件夹是否存在？
			pass
		else:
			os.chdir(os.path.join(mc_path, "assets"))
			os.mkdir("indexes")		# 所有版本的资源索引文件都在这

		file_index_objects = os.path.isfile(assets_index_path + assets_Index_id + ".json")    # 1.12.json文件是否存在?
		if file_index_objects:  # 如果file_index_objects的值为真（1.12.json存在的情况）
			sha1_json = _hash_get_val(assets_index_path + assets_Index_id + ".json", 'sha1')
			# 获得index中的1.12.json的hash(sha1)
			if assets_Index_sh1 == sha1_json:   # 如果文件的sha1值正常
				print("资源索引文件正常")		# 1.12.json

			else:
				hash_yn = 0		# 重复了没有1.12.json的操作中的验证hash步骤
				hash_yn_too_many_try = 0
				while hash_yn == 0:
					hash_yn_too_many_try = hash_yn_too_many_try + 1
					if hash_yn_too_many_try >= 10:
						raise CoreBootstrapMainError("验证资源索引文件时尝试次数过多")

					if assets_Index_sh1 == sha1_json_else:
						hash_yn = 1		# 如果hash正确就跳出循环
					else:
						os.chdir(assets_index_path)	 # 到达应该下载的目录
						response = requests.get(assets_Index_download_url)	 # 下载
						with open(assets_Index_id + ".json", mode="wb+") as f:		# 写入
							f.write(response.content)
							f.close()
						sha1_json_else = _hash_get_val(assets_index_path + assets_Index_id + ".json", 'sha1')  # 获得index中的1.12.json的hash(sha1)
						os.chdir(running_src)	# 返回程序运行时目录

		else:       # 1.12.json不存在的情况
			os.chdir(assets_index_path)
			response = requests.get(assets_Index_download_url)
			with open(assets_Index_id + ".json", mode="wb+") as f:
				f.write(response.content)
				f.close()
			sha1_json_else = _hash_get_val(assets_index_path + assets_Index_id + ".json", 'sha1')  # 获得index中的1.12.json的hash(sha1)
			hash_yn = 0		# 验证hash是否正确
			hash_yn_too_many_try = 0
			while hash_yn == 0:
				hash_yn_too_many_try = hash_yn_too_many_try + 1
				if hash_yn_too_many_try >= 10:		# 尝试次数过多就引发这个错误,防止程序一直卡在这
					raise CoreBootstrapMainError("验证资源索引文件时尝试次数过多")		# 可以考虑在参数上加上循环次数过多时候是否退出（core_bootstrap_main)

				if assets_Index_sh1 == sha1_json_else:
					hash_yn = 1
				else:
					os.chdir(assets_index_path)
					response = requests.get(assets_Index_download_url)
					with open(assets_Index_id + ".json", mode="wb+") as f:
						f.write(response.content)
						f.close()
					sha1_json_else = _hash_get_val(assets_index_path + assets_Index_id + ".json", 'sha1') # 获得index中的1.12.json的hash(sha1)
					os.chdir(running_src)

		# 下面就有1.12.json
		# 是在是太多了,所以,我决定将它直接整合到一起（下个版本）
		# 下个版本使用for循环加列表简化资源下载
		print("开始检查资源")
		if os.path.isdir(assets_objects_path):
			print("资源主目录存在")
		else:
			os.chdir(os.path.join(mc_path, "assets"))
			os.mkdir("objects")
			os.chdir(running_src)


		os.chdir(os.path.join(mc_path, "assets"))  # 切换到assets目录（最后记得移动回去）
		# 其实上面不回去就行了，不过这样更明显一点

		ret_read_json_val = _read_json_file(assets_index_path + assets_Index_id + ".json")
		# 获得1.12.json文件中的内容并序列化为字典
		os.chdir(running_src)		# 回去了 331
		# with open('1.12.2(g).json', mode="w+") as f:
		# f.write(json.dumps(start_json, indent=4, ensure_ascii=False))
		# https://blog.csdn.net/weixin_30411455/article/details/114407713
		# 可以自动格式化json，成为人能看懂的,而且带有缩进

		asserts_json_objects = []
		asserts_json_objects_item = []
		asserts_json_objects_hash = []
		print("正在获得资源名")
		with alive_bar(len(range(1305)), force_tty=True) as bar:
			for key, item in ret_read_json_val["objects"].items():		# 获得资源名
				bar()
				asserts_json_objects_item.append(item)
				asserts_json_objects.append(key)

		# print(asserts_json_objects_item)		# debug list dict
		# print(asserts_json_objects_item[0])		# debug dict list[0]

		for list_hash in asserts_json_objects_item:		# dict
			asserts_json_objects_hash.append(list_hash["hash"])		# dict to list

		os.chdir(assets_objects_path)		# 前往objects文件夹准备建立资源文件夹
		print("正在检查资源文件")
		downloads_file_url_list = []
		with alive_bar(len(range(1305)), force_tty=True) as bar:
			for asserts_json_objects_hash_name in asserts_json_objects_hash:
				if os.path.isdir(os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2])):		# 资源文件夹是否存在
					if os.path.isfile(os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)):
						# 资源文件是否存在
						# 存在的话验证

						sha1_objects_else = _hash_get_val(os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name), 'sha1')		# emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。
						print("s:", sha1_objects_else)		# debug
						if asserts_json_objects_hash_name == sha1_objects_else:
							pass
						else:
							print("Error")
						# 参考了没有1.12.json的操作中的验证hash步骤
						# from 394-412
						# 修改了 返回的目录位置
						# 使用封装后的下载函数
						# 修改了文件名
						# 将变量名sha1_json_else 改为 sha1_objects_else
						# 将sha1_objects_else 的赋值后面的语句中更改了一下就像“由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题”
						# emm os.path.join这个语句后面不封口，也就是在后面没有“//”封口
						# 由于17文件的hash问题,超过五次失败就换成官方源
						# 封装了一下验证
						bmcl_link = "https://bmclapi2.bangbang93.com/assets/"
						hash_yn_too_many_try = 0
						hash_yn = 1
						while hash_yn == 0:
							hash_yn_too_many_try = hash_yn_too_many_try + 1
							if hash_yn_too_many_try >= 5:  # 如果验证失败超过五次那么就更改为官方源下载
								print("mojang")  # debug
								link_downloads_assets = "http://resources.download.minecraft.net/"  # temp_link_downloads_assets
							if hash_yn_too_many_try >= 100:
								raise CoreBootstrapMainError("验证资源文件时尝试次数过多")
							print(hash_yn_too_many_try)  # debug
							if asserts_json_objects_hash_name == sha1_objects_else:
								hash_yn = 1  # 如果hash正确就跳出循环
							else:
								os.chdir(asserts_json_objects_hash_name[0:2])  # 到达应该下载的目录
								_downloads_file_url(link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name, (os.path.join(assets_objects_path,  asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)), True)  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性。。。
								sha1_objects_else = _hash_get_val((os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)), "sha1")  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。  # 获得objects中的资源文件的hash(sha1)
								os.chdir(assets_objects_path)  # 返回objects目录
								print(sha1_objects_else)  # debug
						link_downloads_assets = bmcl_link  # 恢复为原来使用的源
						bar()

					else:		# 资源文件不存在的情况,但资源文件需要的文件夹存在
						# _downloads_file_url(link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name, os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name), True)	# emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性。。。
						downloads_file_url_list.append({"url": (link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name), "path": (os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)), "hash": asserts_json_objects_hash_name, "mkfile": True})
						# 上面这一大串构建了 "url":构造完毕的下载链接 ,"path":这里是路径,"mkfile":恒定为True
						# sha1_objects_else = _hash_get_val(os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name), 'sha1')		# emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。
						# print("s:", sha1_objects_else)		# debug

						# 参考了没有1.12.json的操作中的验证hash步骤
						# 修改了 返回的目录位置
						# 使用封装后的下载函数
						# 修改了文件名
						# 将变量名sha1_json_else 改为 sha1_objects_else
						# 封装了一下验证
						# 封装过的验证有大问题,无法进行有效的判断。现在弃用
						# bmcl_link = "https://bmclapi2.bangbang93.com/assets/"
						# hash_yn_too_many_try = 0
						# hash_yn = 1
						# while hash_yn == 0:
						# 	hash_yn_too_many_try = hash_yn_too_many_try + 1
						# 	if hash_yn_too_many_try >= 5:  # 如果验证失败超过五次那么就更改为官方源下载
						# 		print("mojang")  # debug
						# 		link_downloads_assets = "http://resources.download.minecraft.net/"  # temp_link_downloads_assets
						# 	if hash_yn_too_many_try >= 100:
						# 		raise CoreBootstrapMainError("验证资源文件时尝试次数过多")
						# 	print(hash_yn_too_many_try)  # debug
						# 	if asserts_json_objects_hash_name == sha1_objects_else:
						# 		hash_yn = 1  # 如果hash正确就跳出循环
						# 	else:
						# 		os.chdir(asserts_json_objects_hash_name[0:2])  # 到达应该下载的目录
						# 		_downloads_file_url(link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name, (os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)), True)  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性。。。
						# 		sha1_objects_else = _hash_get_val((os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)), "sha1")  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。  # 获得objects中的资源文件的hash(sha1)
						# 		os.chdir(assets_objects_path)  # 返回objects目录
						# 		print(sha1_objects_else)  # debug
						# link_downloads_assets = bmcl_link  # 恢复为原来使用的源
						bar()
				else:
					os.mkdir(asserts_json_objects_hash_name[0:2])
					# 下面这段直接使用了上面有资源文件夹时下载的步骤
					# _downloads_file_url(link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name, os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name), True)  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性。。。
					downloads_file_url_list.append({"url": (link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name), "path": (os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)), "hash": asserts_json_objects_hash_name, "mkfile": True})
					# 上面这一大串构建了 "url":构造完毕的下载链接 ,"path":这里是路径,"mkfile":恒定为True
					# sha1_objects_else = _hash_get_val(os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name), 'sha1')		# emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。
					# print("s:", sha1_objects_else)		# debug
					# 参考了没有1.12.json的操作中的验证hash步骤
					# 修改了 返回的目录位置
					# 使用封装后的下载函数
					# 修改了文件名
					# 将变量名sha1_json_else 改为 sha1_objects_else
					# 封装了一下验证
					# bmcl_link = "https://bmclapi2.bangbang93.com/assets/"
					# hash_yn_too_many_try = 0
					# hash_yn = 1
					# while hash_yn == 0:
					# 	hash_yn_too_many_try = hash_yn_too_many_try + 1
					# 	if hash_yn_too_many_try >= 5:  # 如果验证失败超过五次那么就更改为官方源下载
					# 		print("mojang")  # debug
					# 		link_downloads_assets = "http://resources.download.minecraft.net/"  # temp_link_downloads_assets
					# 	if hash_yn_too_many_try >= 100:
					# 		raise CoreBootstrapMainError("验证资源文件时尝试次数过多")
					# 	print(hash_yn_too_many_try)  # debug
					# 	if asserts_json_objects_hash_name == sha1_objects_else:
					# 		hash_yn = 1  # 如果hash正确就跳出循环
					# 	else:
					# 		os.chdir(asserts_json_objects_hash_name[0:2])  # 到达应该下载的目录
					# 		_downloads_file_url(link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name, (os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)), True)  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性。。。
					# 		sha1_objects_else = _hash_get_val((os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)), "sha1")  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。  # 获得objects中的资源文件的hash(sha1)
					# 		os.chdir(assets_objects_path)  # 返回objects目录
					# 		print(sha1_objects_else)  # debug
					# link_downloads_assets = bmcl_link  # 恢复为原来使用的源
					bar()

		multprocessing_task(downloads_file_url_list, 32, True)
		os.chdir(running_src)
		print("资源文件验证完毕")
		print("正在下载lib文件")
		# lib文件下载
		i_2 = 0
		with alive_bar(len(range(37)), force_tty=True) as bar:
			for item in downloads_artifact_inlib_list:		# 单个lib文件路径
				tmp = item.split("/")
				tmplong = len(tmp)
				i = 0
				os.chdir(lib_path)
				#for items in tmp:		# 创建文件夹并下载
				for items in tmp:
					print(items)
					if ".jar" in items:
						if os.path.exists(items):
							pass
						else:
							_downloads_file_url(downloads_artifact_url_inlib_list[i_2], items, True)
					elif os.path.exists(items):
						os.chdir(items)
					elif i <= tmplong - 1:
						os.mkdir(items)
						os.chdir(items)
					#i += 1
				i_2 += 1

				os.chdir(lib_path)
				bar()
		# 以上是lib文件下载部分
		print("lib ok")
		print(downloads_natives_path_list)
		i_2 = 0
		i = 0
		for item in downloads_natives_path_list:
			tmp = item.split("/")
			tmplong = len(tmp)
			i = 0
			os.chdir(lib_path)
			for items in tmp:  # 创建文件夹并下载
				if os.path.exists(items):
					print("ok")
				elif ".jar" in items:
					_downloads_file_url(downloads_natives_url_list[i_2], items, True)
					try:
						with zipfile.ZipFile(items, mode="r") as archive:
							archive.extractall(natives_path)
							archive.close()
					except zipfile.BadZipFile as zBZ:
						print(zBZ,"解压失败")
				elif i < tmplong - 1:		# 这里被淘汰
					os.mkdir(items)
					os.chdir(items)
				i += 1
			i_2 += 1

			os.chdir(lib_path)
		print("ok")

		log4j2type = start_json["logging"]["client"]["type"]
		log4j2 = log4j2type.replace("-", ".")
		log4j2_download_url = start_json["logging"]["client"]["file"]["url"]
		if not os.path.exists(log4j2):
			_downloads_file_url(log4j2_download_url, (os.path.join(mc_path, "versions", jar_version, log4j2)), True)
		print("All Right")


	else:
		raise CoreBootstrapMainError("暂不支持")


class CoreStartLoginError(Exception):
	def __init__(self, message):
		super().__init__(message)


def core_start_Login(Update_Token, Refresh_Token, Mojang_MS_login=False, MS_login=False, back_url: str = None, Mojang_login=False):
	"""
	Update_Token:更新AccessToken令牌
	Refresh_Token:刷新令牌用的令牌
	Mojang_MS_login:正版登录（直接填True）
	MS_login：进行微软/Xbox登录填True,否则填False
	back_url：微软/Xbox登录返回的链接，也就是访问https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf
	这个网址跳转的链接
	Mojang_login:进行Mojang登录（未完成）（默认为False）(可不填)
	"""

	mojang_Yggdrasil = "https://authserver.mojang.com"
	cookie = "token=code_space;"
	header = {
		"cookie": cookie,
		"Accept": "*/*",
		"Accept-Encoding": "gzip, deflate, br",
		"Accept-Language": "zh-CN,zh;q=0.9",
		"Connection": "keep-alive",
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
	}
	MS_login_token_get_link = "https://login.live.com/oauth20_token.srf"
	if Mojang_MS_login:
		if MS_login:
			try:
				back_url_code_place = back_url.find("code=")
				back_url_code_place_end = back_url.find("&")
				back_url = back_url[back_url_code_place+5:back_url_code_place_end-1]
			except AttributeError as eab:

				if eab == "'int' object has no attribute 'replace'":
					raise CoreStartLoginError(("back_url不应该是int类型,应该是str", eab))

				elif eab == "'float' object has no attribute 'replace'":
					raise CoreStartLoginError(("back_url不应该是float类型,应该是str", eab))

				elif eab == "'NoneType' object has no attribute 'replace'":
					raise CoreStartLoginError(("back_url不应该是NoneType类型,应该是str", eab))

				raise CoreStartLoginError(eab)
			if "M.R3_BAY" in back_url:
				pass
			else:
				raise CoreStartLoginError("无法提取到OAuth code")

			MS_head = {
				"cookie": cookie,
				"Accept": "*/*",
				"Accept-Encoding": "gzip, deflate, br",
				"Accept-Language": "zh-CN,zh;q=0.9",
				"Connection": "keep-alive",
				"Content-Type": "application/x-www-form-urlencoded",
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
			}
			XBL_head = {
				"cookie": cookie,
				"Accept": "application/json",
				"Accept-Encoding": "gzip, deflate, br",
				"Accept-Language": "zh-CN,zh;q=0.9",
				"Connection": "keep-alive",
				"Content-Type": "application/json",
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
			}

			#q = webbrowser.get().open_new("https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf")
			#print(q)

			MS_authcode = back_url		# 填入code进行访问OAuth,debug时可直接填入code=后&前的code
			post_ms_AT = \
						"client_id=00000000402b5328&code=" + MS_authcode +\
						"&grant_type=authorization_code&redirect_uri=https://login.live.com/oauth20_desktop.srf" + \
						"&scope=service::user.auth.xboxlive.com::MBI_SSL"

			r = requests.post(MS_login_token_get_link, data=post_ms_AT, headers=MS_head)
			post_json_ms_token_back_json = json.loads(r.text)
			try:		# 看看有没有error这个键
				post_json_ms_token_back_json_error = post_json_ms_token_back_json["error"]
				print(post_json_ms_token_back_json_error)
				print(post_json_ms_token_back_json)
				if post_json_ms_token_back_json["error_description"] == "The provided value for the 'code' parameter is not valid. The code has expired.":
					print("验证过期")		# 过期了
					raise CoreStartLoginError("无法通过Microsoft OAuth,验证过期.请重新进行登录操作")
				else:
					raise CoreStartLoginError("无法通过Microsoft OAuth\n"+post_json_ms_token_back_json["error_description"])
					# 不知道哪里错了,抛出错误
			except KeyError as KE:
				pass

			print(r.text)		# debug
			MS_T_back_A_T = post_json_ms_token_back_json["access_token"]		# 全称为 MS_Token_back_Access_Token
			MS_T_back_R_T = post_json_ms_token_back_json["refresh_token"]		# 全称为 MS_Token_back_Refresh_Token
			MS_T_back_user_id = post_json_ms_token_back_json["user_id"]			# 全称为 MS_Token_back_user_id
			MS_Token_back_timeout = post_json_ms_token_back_json["expires_in"]  # 全称为 MS_Token_back_timeout
			print(MS_T_back_A_T)
			print(MS_T_back_R_T)
			# 微软完成下面是XBL
			XBL_login_token_get_link = "https://user.auth.xboxlive.com/user/authenticate"
			post_xbl_auth = {
				"Properties": {
					"AuthMethod": "RPS",
					"SiteName": "user.auth.xboxlive.com",
					"RpsTicket": "{}".format(MS_T_back_A_T)
				},
				"RelyingParty": "http://auth.xboxlive.com",
				"TokenType": "JWT"
			}
			print(post_xbl_auth)
			post_xbl_auth_json = json.dumps(post_xbl_auth)		# 将字典转为json格式
			print(post_xbl_auth_json)
			r = requests.post(XBL_login_token_get_link, data=post_xbl_auth_json, headers=XBL_head)
			print(r.text)
			XBL_ret_json = json.loads(r.text)
			try:
				XBL_ret_token = XBL_ret_json["Token"]
				XBL_ret_xui_list = XBL_ret_json["DisplayClaims"]["xui"][0]
				XBL_ret_token_ush = XBL_ret_xui_list["uhs"]		# 获得user hash
			except KeyError as KE:
				print(XBL_ret_json)
				raise CoreStartLoginError("XBL认证失败\n"+XBL_ret_json)
			# XBL验证完毕,下面是XSTS
			post_xsts_auth = {
								"Properties": {
								"SandboxId": "RETAIL",
								"UserTokens": [
										XBL_ret_token
								]
								},
								"RelyingParty": "rp://api.minecraftservices.com/",
								"TokenType": "JWT"
								}

			XSTS_login_token_get_link = "https://xsts.auth.xboxlive.com/xsts/authorize"
			XSTS_head = XBL_head		# XSTS和XBL的请求头一致
			post_xsts_auth_json = json.dumps(post_xsts_auth)		# 将字典转为json格式

			r = requests.post(XSTS_login_token_get_link, data=post_xsts_auth_json, headers=XSTS_head)

			XSTS_ret_json = json.loads(r.text)
			try:
				XSTSL_ret_token = XSTS_ret_json["Token"]
				XSTS_ret_xui_list = XSTS_ret_json["DisplayClaims"]["xui"][0]
				XSTS_ret_token_ush = XSTS_ret_xui_list["uhs"]  # 获得user hash,XSTS的.不过应该为空
			except KeyError as KE:
				print(KE)
				raise CoreStartLoginError("XSTS认证失败\n" + XSTS_ret_json)

			# XSTS令牌获得完毕,下一步得到启动令牌(accessToken for Minecraft)

			login_with_xbox_or_MS_link = "https://api.minecraftservices.com/authentication/login_with_xbox"

			post_Minecraft_auth_get_A_T = {
				"identityToken": "XBL3.0 x={0};{1}".format(XBL_ret_token_ush, XSTSL_ret_token)
			}

			post_Minecraft_auth_get_A_T_json = json.dumps(post_Minecraft_auth_get_A_T)  # 将字典转为json格式
			r = requests.post(login_with_xbox_or_MS_link, data=post_Minecraft_auth_get_A_T_json, headers=header)
			Minecraft_AccessToken_json = json.loads(r.text)
			try:
				MinecraftAccessToken = Minecraft_AccessToken_json["access_token"]
			except KeyError as KE:
				print(KE)
				raise CoreStartLoginError("获取MinecraftAccessToken时出现错误,可能是XSTS令牌过期")

			# 查看该用户是否拥有Minecraft
			header_Minecraft = {
				"cookie": cookie,
				"Authorization": "Bearer {}".format(MinecraftAccessToken),
				"Accept": "application/json",
				"Accept-Encoding": "gzip, deflate, br",
				"Accept-Language": "zh-CN,zh;q=0.9",
				"Connection": "keep-alive",
				"Content-Type": "application/json",
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
			}
			Minecraft_have_Y_N_link = "https://api.minecraftservices.com/entitlements/mcstore"
			r = requests.get(Minecraft_have_Y_N_link, headers=header_Minecraft)
			print(r.text)

			uuid_get_link = "https://api.minecraftservices.com/minecraft/profile"
			r = requests.get(uuid_get_link, headers=header_Minecraft)
			print(r.text)
			uuid_name_json = r.json()
			try:
				uuid_MS_xbox = uuid_name_json["id"]
				name_MS_xbox = uuid_name_json["name"]
			except KeyError as KE:
				raise CoreStartLoginError("账号验证错误:没有Minecraft(uuid/name)")

			return name_MS_xbox, uuid_MS_xbox, MinecraftAccessToken


		elif Mojang_login:
			post_json = 9
			r = requests.post(mojang_Yggdrasil + "/authenticate", data=post_json, headers=header)
		# print(r.text)

def core_start_IN(java_path, mc_path, launcher_name, username, uuid_val, aT, launcher_name_version, uuid_yn = False, G1NewSizePercent_size="20", G1ReservePercent_size="20", Xmn="128m", Xmx="1024M", cph=None):  # java_path以后可以升个级作判断，自己检测Java
	'''
		java_path:Java路径（字符串）（可以填写java)

		mc_path:游戏目录（到.minecraft）

		launcher_name：需要启动的游戏版本（字符串）

		username:玩家名（字符串）

		uuid_val：uuid(字符串)

		aT:accessToken位，用于正版登录。一般随便填（盗版登录）（字符串）

		launcher_name_version：启动器版本

		uuid_yn:是否有（需要生成）uuid(默认为False需要生成）（可不填（需要生成））（bool）

		G1NewSizePercent_size:20（字符串）

		G1ReservePercent_size：20（字符串）

		Xmn:最小内存（默认128m）

		Xmx:最大分配内存（默认1024M)

		cph:此位保留，无用处。不返回。可填None.
	'''

	# java_path:Java路径（字符串）（可以填写java)
	#mc_path:游戏目录（到.minecraft）
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
	# uuid_yn:是否有（需要生成）uuid(默认为False需要生成）（可不填（需要生成））（bool）
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
	if not uuid_yn:		# 如果没有uuid那就生成一个
		launcher_uuid_uuid = uuid.uuid4()
		launcher_uuid = launcher_uuid_uuid.hex
		uuid_val = launcher_uuid
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
		if uuid_yn:
			return "ok", temp_2 + temp_3
		else:
			return "ok", temp_2 + temp_3, launcher_uuid

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

		if uuid_yn:
			return "ok", temp_2 + temp_3
		else:
			return "ok", temp_2 + temp_3, launcher_uuid
