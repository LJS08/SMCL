# Copyright © 2022-2023 LJS80 All Rights Reserved
from alive_progress import alive_bar
from . import constant as const  # 常量定义用
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib
import json
from loguru import logger
import multiprocessing
import os
import requests
import re
import sqlite3
import sys
import subprocess
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as CService
from selenium.webdriver.edge.service import Service as EService
import tempfile
import threading
import time
import uuid
import winreg
import xml
import xml.dom.minidom
import xmlrpc
import zipfile

logger.add('log/core_start_{time}.log', rotation="50 MB", compression='zip', encoding='utf-8')

lock = threading.Lock()  # 初始化锁

# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
core_start_version = "0.0.1"
header_smcl = {f"User-Agent": "SMCL/{core_start_version}"}


class _CheckVersionError(Exception):
	def __init__(self, message):
		super().__init__(message)


def _Check_versions_in(CV_version_name):
	"""此函数用来分解版本字符串,内部版本"""

	i = 0
	# 看起来是不是很熟悉?其实这个是从Update_Main.py直接copy来的

	version_name_split = []
	version_name_split = CV_version_name.split(".")
	MAX_VERSION = 999
	LOW_VERSION = 0
	print(version_name_split)
	for item in version_name_split:
		i += 1
	print(i)
	if i <= 2:
		version_name_split.append(0)
	elif i > 3:
		raise _CheckVersionError("版本字符串过高,无法分解。请检查您的版本号是否超过3位")
	frist_num = int(version_name_split[0]) * 999 * 999  # 1.0.0 = 0.999.999+1 = 1.0.0
	nd_2_num = int(version_name_split[1]) * 999
	rd_3_num = int(version_name_split[2])
	CV_version_num = frist_num + nd_2_num + rd_3_num
	print(CV_version_num)
	return CV_version_num


def _downloads_file_url(file_url, downloads_file_url_src, mkfile):
	"""file_url 是链接地址。downloads_file_url_src 文件地址.mkfile 传参，在没有这个文件时决定是否创建此文件（老版本）"""
	# 新版为_downloads_file_url多线程下载
	# 老版（改名了）(原名：_downloads_file_url）
	#
	# file_url 是链接地址
	# downloads_file_url_src 文件地址
	# mkfile 传参，在没有这个文件时决定是否创建此文件
	# 还是单线程稳定。。。
	downloads_file_url_response = requests.get(file_url, headers=header_smcl)
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
			raise CoreBootstrapMainError(f"错误, 无法找到文件:{e}")


class CoreBootstrapMainError(Exception):
	def __init__(self, message):
		super().__init__(message)


def calc_divisional_range(file_size: int, chuck=10) -> list:
	"""
	此函数用于将文件分块
	file_size: 文件总大小
	chuck: 块数
	"""
	# 被弃用,4个提交后添加崩溃报告
	step = file_size // chuck
	arr = list(range(0, file_size, step))
	result = []
	for i in range(len(arr) - 1):
		s_pos, e_pos = arr[i], arr[i + 1] - 1
		result.append([s_pos, e_pos])
	result[-1][-1] = file_size - 1
	return result


def range_download_old(downloads_file_url_src, s_pos, e_pos, url, mkfile):
	"""被弃用,4个提交后添加崩溃报告"""
	# 被弃用
	headers = {"Range": f"bytes={s_pos}-{e_pos}", f"User-Agent": "SMCL/{core_start_version}"}
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


def range_download(start, end, file_url, downloads_file_fp, bar, temp_file_bit, mkfile):
	headers = {
		'Range': f'bytes={start}-{end}', f"User-Agent": "SMCL/{core_start_version}",
	}
	# 传递头，表明分段下载
	pos = start  # 文件指针就等于（pos）开始（start)
	logger.debug(f"pos={pos} start={start} end={end}")
	tmp_file = False

	with requests.get(file_url, stream=True, headers=headers) as downloads_file_url_response:
		for item in downloads_file_url_response.iter_content(chunk_size=1024):  # 设置每次传输的大小r.content.decode(r.apparent_encoding)
			if item:  # 判断是否为空数据
				# decoded_i = i.decode('utf-8')	 # 将i转码（没用到）
				try:
					if temp_file_bit:		# 试验内容
						lock.acquire()  # 获得使用权
						downloads_file_fp.seek(pos, 0)
						downloads_file_fp.write(item)
						lock.release()  # 释放使用权

					else:
						while_write = False
						while lock.locked():
							if lock.locked() and not while_write:
								tmp_file = tempfile.TemporaryFile()
								tmp_file.seek(0)
								tmp_file.write(item)
								while_write = True
								if lock.locked():
									time.sleep(0.01)
								else:
									break

							elif lock.locked() and while_write:
								time.sleep(0.01)

							elif not lock.locked():
								break
							else:
								break

						lock.acquire()  # 获得使用权
						try:
							if while_write:
								with open(downloads_file_fp, mode="rb+") as f:
									tmp_file.seek(0)
									f.seek(pos, 0)
									f.write(tmp_file.read())
									tmp_file.close()

							else:
								with open(downloads_file_fp, mode="rb+") as f:
									f.seek(pos, 0)
									f.write(item)

						except PermissionError as PE:
							logger.error(PE)

						except FileNotFoundError as FNFE:
							raise FileNotFoundError(FNFE)

						except Exception as E:
							logger.error(E)

						lock.release()  # 释放使用权

				except FileNotFoundError as FNFE:
					if tmp_file:
						tmp_file.close()

					if lock.locked():
						lock.release()

					logger.info("FileNotFound: {}}".format(FNFE))
					if mkfile:
						try:
							lock.acquire()  # 获得使用权
							with open(downloads_file_fp, mode="wb+") as f:
								f.seek(pos)
								f.write(item)
								f.close()
							lock.release()  # 释放使用权
						except Exception as E:
							logger.error(f"{E}")
					else:
						logger.error(f"错误, 无法找到文件:{FNFE}")
						raise CoreBootstrapMainError(f"错误, 无法找到文件:{FNFE}")

				except Exception as E:
					if tmp_file:
						tmp_file.close()
					if lock.locked():
						lock.release()

					logger.error(E)

			else:
				logger.debug("空数据: \n {}".format(item))

			pos = pos + 1024  # 自增
		bar()


def _range_downloads_file_url(file_url, downloads_file_fp, temp_file_bit=False, allow_redirect=False, ranges_check=False, force_download=False, mkfile=False):
	"""
	file_url: 需要下载的文件的链接
	downloads_file_fp: 文件名（或者当temp_file_bit为True是应该为临时文件对象）
	temp_file_bit: 是否写入到的是临时文件(默认为False)(当为True时，将会使用downloads_file_fp作为文件对象直接向临时文件写入)
	allow_redirect: 是否允许重定向?(默认为False)(部分文件的下载链接可能为短链接, 实际上会经过重定向到下载文件。启用此选项有被攻击的风险, 可能会被恶意重定向)
	ranges_check: 是否为Ranges Check模式?(默认为False)(当为此模式时不会下载文件， 而是探测是否此文件允许分段下载.如果允许分段下载则返回True, 不允许则为False)
	force_download: 是否强制下载?(默认为False)(正常情况下, 下载函数检测到被下载文件不允许分段回源时, 会raise一个Exception. 如果启用此选项, 下载函数不会报错, 而是转为单线程下载(不支持temp_file)。)
	mkfile: 是否在无法找寻到文件时创建一个新的文件?(默认为False)
	"""
	# 曾用名 _downloads_file_urls
	# 实际上这应该替换的是两个多线程下载

	response = requests.head(file_url)
	logger.debug(response.headers)
	while allow_redirect:

		if 'Location' in response.headers:
			logger.debug("Location在header中:head:\n{}".format(response.headers))
			redirect_location = response.headers["Location"]

			if "gitee" in redirect_location or "github" in redirect_location:
				response = requests.head(redirect_location)
				logger.info("跳转向{}".format(redirect_location))

			else:
				logger.error("错误, 跳转的链接异常.无法确认来源.")

		elif 'Content-Length' in response.headers:
			logger.debug("Content-Length在header中:head:\n{}".format(response.headers))

			if "Accept-Ranges" in response.headers and response.headers["Accept-Ranges"] != "None":
				logger.info("请求头中有有效的Accept-Ranges")
				break

			else:
				logger.info("请求头中无有效的Accept-Ranges")
				if force_download and not temp_file_bit:
					logger.info("进入单线程下载")
					ret_download = _downloads_file_url(file_url, downloads_file_fp, mkfile)
					return ret_download

				elif ranges_check:
					return False

				else:
					if response.headers["Accept-Ranges"] == "None":
						raise CoreBootstrapMainError("请求的文件不允许分片回源")

					else:
						raise CoreBootstrapMainError("请求的文件不支持分片回源")

		else:
			logger.debug("其他情况 {}".format(response.headers))
			break

	if allow_redirect and ranges_check:		# 如果允许重定向并且是ranges_check
		return response.headers["Accept-Ranges"]

	if not allow_redirect and "Accept-Ranges" in response.headers:		# 如果不允许重定向并且有正确的响应头
		return response.headers["Accept-Ranges"]

	elif not allow_redirect and "Accept-Ranges" not in response.headers:		# 如果没有正确的响应头
		if force_download and not temp_file_bit:
			ret_download = _downloads_file_url(file_url, downloads_file_fp, mkfile)
			return ret_download

		elif ranges_check:
			return False

		else:
			raise CoreBootstrapMainError("请求的文件不支持分片回源")

	filesize = int(response.headers['Content-Length'])
	file_url = response.url
	divisional_ranges = calc_divisional_range(filesize)		# 分下载块
	# 创建线程池
	with alive_bar(len(divisional_ranges), force_tty=True) as bar:
		# max_workers = 10
		with ThreadPoolExecutor() as p:
			futures = []
			logger.info("正在创建工作线程")
			for s_pos, e_pos in divisional_ranges:
				logger.debug("start_pos: {0}, end_pos: {1}".format(s_pos, e_pos))
				futures.append(p.submit(range_download, s_pos, e_pos, file_url, downloads_file_fp, bar, temp_file_bit, mkfile))
			logger.debug(futures)
			# 等待所有任务执行完毕
			as_completed(futures)


def _downloads_file_url_threading(file_url, downloads_file_url_src, mkfile):
	"""file_url 是链接地址。downloads_file_url_src 文件地址.mkfile 传参，在没有这个文件时决定是否创建此文件。多线程下载（新）被弃用,4个提交后添加崩溃报告"""
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
							raise CoreBootstrapMainError(f"错误, 无法找到文件:{es}")

				pos = pos + 1024  # 自增
		e.set()

	with requests.get(file_url, stream=True) as r2:  # 开启流式下载
		thread_num = multiprocessing.cpu_count() * 4  # 线程数量
		size = int(r2.headers['Content-Length'])
		print(r2.headers['Content-Length'])
		global threads_downloads_file_url
		threads_downloads_file_url = []  # 记录线程号
		for i in range(thread_num):
			if i == thread_num - 1:
				t1 = threading.Thread(target=_downloads_help_things,
									  args=(i * (size // thread_num), size, file_url, downloads_file_url_src, mkfile))
				t1.start()
				# t1.join()
				threads_downloads_file_url.append(t1)  # 将线程名添加到threads_downloads_file_url列表
			else:
				t1 = threading.Thread(target=_downloads_help_things, args=(
				i * (size // thread_num), (i + 1) * (size // thread_num), file_url, downloads_file_url_src, mkfile))
				t1.start()
				threads_downloads_file_url.append(t1)  # 将线程名添加到threads_downloads_file_url列表

		for thread in threads_downloads_file_url:  # 从threads_downloads_file_url列表中获得线程名，然后一个个join
			e.wait()
			thread.join()

# _downloads_hash_bugs已经被弃用,原因：无法正常被使用。现已经被集成进入multprocessing_task函数.此提醒将会在1个提交后删除。


def _read_json_file(read_json_file_src, ERROR_MSG="错误: 无法找到需要加载的文件,", PRINT_MSG=None):
	try:
		with open(read_json_file_src, mode='r', encoding="gbk") as f:
			data = f.read(-1)
			read_json_file_json = json.loads(data)
			f.close()
		return read_json_file_json

	except FileNotFoundError as e:
		print("{}".format(PRINT_MSG))
		raise CoreBootstrapMainError("{0}{1}".format(ERROR_MSG, e))

	except UnicodeDecodeError:
		try:
			with open(read_json_file_src, mode='r') as f:
				data = f.read(-1)
				read_json_file_json = json.loads(data)
				f.close()
		except FileNotFoundError as e:
			print("{}".format(PRINT_MSG))
			raise CoreBootstrapMainError("{0}{1}".format(ERROR_MSG, e))  # 这里估计用不到，前面都已经有侦测到编码错误应该是有文件了。但保险起见，还是加上吧

		except UnicodeDecodeError as UDE:
			print("{}".format(PRINT_MSG))
			print("编码错误{}".format(UDE))


def _encrypt(fpath: str, algorithm: str) -> str:  # https://blog.csdn.net/qq_42951560/article/details/125080544
	with open(fpath, mode='rb') as f:
		return hashlib.new(algorithm, f.read()).hexdigest()


def _hash_get_val(hash_file_src, hash_need_type, hash_mode = "file"):
	'''hash_need_type是想要得到的hash值的类型(字符串)，只有sha1,sha256.md5.hash_file_src是需要得到hash值的文件的路径（字符串）(当hash_mode为str时为需要得到hash值的文本)，hash_mode是生成hash的模式'''
	if hash_mode == "file":
		for algorithm in ('md5', 'sha1', 'sha256'):  # https://blog.csdn.net/qq_42951560/article/details/125080544
			hexdigest = _encrypt(hash_file_src, algorithm)
			# print(f'{algorithm}: {hexdigest}')
			# 第一次为MD5，第二次为sha1,第三次为sha256
			if algorithm == hash_need_type:
				return hexdigest

	elif hash_mode == "str":
		for algorithm in ('md5', 'sha1', 'sha256'):  # https://blog.csdn.net/qq_42951560/article/details/125080544
			hexdigest = hashlib.new(algorithm, hash_file_src.encode()).hexdigest()
			# print(f'{algorithm}: {hexdigest}')
			# 第一次为MD5，第二次为sha1,第三次为sha256
			if algorithm == hash_need_type:
				return hexdigest


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
				if task["hash-check"]:  # 检测hash-check位是否为True
					logger.debug("新版下载时验证(多线程兼容版)")
					# 以下是检查hash的多线程下载(受到GIL限制)

					# 适应性变量声明区
					mupt_nolink_downloads_assets = task[
						"nolink_downloads_assets"]  # 相当于没有link_downloads_assets的link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name
					mupt_asserts_json_objects_hash_name = task["asserts_json_objects_hash_name"]
					mupt_assets_objects_path = task["assets_objects_path"]

					_downloads_file_url(task_download_url, task_need_src, task_need_mkfile)
					sha1_objects_else = _hash_get_val(task_need_src, 'sha1')  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。
					# 参考了没有1.12.json的操作中的验证hash步骤
					# 修改了 返回的目录位置
					# 使用封装后的下载函数
					# 修改了文件名
					# 将变量名sha1_json_else 改为 sha1_objects_else
					# 封装了一下验证
					# 从下面搬过来的
					bmcl_link = "https://bmclapi2.bangbang93.com/assets/"
					mupt_link_downloads_assets = bmcl_link
					hash_yn_too_many_try = 0
					hash_yn = 1
					while hash_yn == 0:
						hash_yn_too_many_try = hash_yn_too_many_try + 1
						if hash_yn_too_many_try >= 5:  # 如果验证失败超过五次那么就更改为官方源下载
							logger.info("Try mojang API to download(尝试次数过多){}".format(hash_yn_too_many_try))  # debug
							mupt_link_downloads_assets = "http://resources.download.minecraft.net/"  # temp_link_downloads_assets
						if hash_yn_too_many_try >= 100:
							logger.error("验证资源文件时尝试次数过多,你这都100次尝试都失败了。看看你的网络是不是有什么大病。。。")
							raise CoreBootstrapMainError("验证资源文件时尝试次数过多")
						print(hash_yn_too_many_try)  # debug
						if mupt_asserts_json_objects_hash_name == sha1_objects_else:
							hash_yn = 1  # 如果hash正确就跳出循环
						else:
							os.chdir(mupt_asserts_json_objects_hash_name[0:2])  # 到达应该下载的目录
							_downloads_file_url(mupt_link_downloads_assets + mupt_nolink_downloads_assets,
												task_need_src,
												task_need_mkfile)  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性。。。

							sha1_objects_else = _hash_get_val(task_need_src,
															  "sha1")  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。  # 获得objects中的资源文件的hash(sha1)
							os.chdir(mupt_asserts_json_objects_hash_name)  # 返回objects目录
							print(sha1_objects_else)  # debug
					mupt_link_downloads_assets = bmcl_link  # 恢复为原来使用的源
				else:
					_downloads_file_url(task_download_url, task_need_src, task_need_mkfile)
			# function(task)
			except KeyError as ke:
				print(ke)
			except IndexError as IndexE:
				break

	for i in range(cores + 1):
		thread = threading.Thread(target=_run)
		thread.start()
		threads.append(thread)
	if join:
		for thread in threads:
			thread.join()


link_downloads_launcher = ""


def core_bootstrap_main(selfup, mc_path, jar_version, link_type):
	global link_downloads_launcher
	if link_type == "mojang" or link_type is None:  # 使用mojang api
		logger.warning("using Mojang api")
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

	elif link_type == "BMCLAPI":  # 使用BMCLAPI
		logger.info("using BMCLAPI")
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

	elif link_type == "MCBBS":  # 使用MCBBS api
		logger.error("using MCBBS api ,there is nothing.")
		pass

	else:  # 如果都不是就用mojang(重复？)
		logger.warning("using Mojang api")
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

	if selfup:		# 命令启动模式
		running_src = os.getcwd()  # 获得当前工作目录
		CPU_CORE = multiprocessing.cpu_count()

		if os.path.isdir(os.path.join(mc_path, "versions", jar_version)):
			logger.info("客户端目录：存在")
			logger.info("客户端目录：存在{}".format(os.path.join(mc_path, "versions", jar_version)))
		else:
			logger.info("客户端目录:不存在")
			logger.info("客户端目录:不存在{}".format(os.path.join(mc_path, "versions", jar_version)))
			logger.info("正在创建")
			logger.info("正在创建:{}".format(os.path.join(mc_path, "versions", jar_version)))
			os.chdir(os.path.join(mc_path, "versions"))
			logger.debug("移动到:{}".format(os.path.join(mc_path, "versions")))
			os.mkdir(jar_version)
			logger.debug("创建文件夹:{}".format(jar_version))
			os.chdir(running_src)  # 返回工作目录
			logger.debug("返回工作目录:{}".format(running_src))

		if os.path.isfile(os.path.join(mc_path, "versions", jar_version, jar_version) + ".jar"):
			logger.info("主游戏文件:存在")
			logger.info("主游戏文件:存在,{}".format((os.path.join(mc_path, "versions", jar_version, jar_version) + ".jar")))
		else:
			logger.info("主游戏文件:不存在")
			logger.info("主游戏文件:不存在,{}".format((os.path.join(mc_path, "versions", jar_version, jar_version) + ".jar")))
			logger.info("正在下载,这可能需要一段时间")
			with alive_bar(len(range(100)), force_tty=True) as bar:  # 这里没卵用，主要是因为没开异步
				for item in range(50):  # 遍历任务
					bar()  # 显示进度
					time.sleep(0.01)
				bar()
				_downloads_file_url(link_downloads_launcher + "version/" + jar_version + "/jar", os.path.join(mc_path, "versions", jar_version, jar_version) + ".jar", True)
				for item in range(30):  # 遍历任务
					bar()  # 显示进度
					time.sleep(0.000001)
				for item in range(19):  # 遍历任务
					bar()  # 显示进度
					time.sleep(0.1)
			logger.info("下载完毕")

		if os.path.isfile(os.path.join(mc_path, "versions", jar_version, jar_version) + ".json"):
			logger.info("配置文档:存在")
		else:
			logger.info("配置文档:不存在")
			logger.info("正在下载,这可能需要一段时间")
			_downloads_file_url(link_downloads_launcher + "version/" + jar_version + "/json", os.path.join(mc_path, "versions", jar_version, jar_version) + ".json", True)  # 下载JSON配置文件
			logger.info("下载完毕")

		logger.info("正在预加载:配置文档")
		start_json = _read_json_file((os.path.join(mc_path, 'versions', jar_version, jar_version) + ".json"), "错误, 无法找到描述文件, 请检查您的安装", "预加载配置文档失败")
		logger.info("配置加载完毕")

		# 我早知道就不在这里用单独的部分了。。。

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
		natives_path = os.path.join(mc_path, "versions", jar_version, "natives")
		if run_time_environment == 'nt':
			natives_path = os.path.join(mc_path, "versions", jar_version, "natives-windows-x86_64")
		i = 0
		for item in library_download_list:
			temp = item["name"]
			print(temp, temp.count("."))  # debug
			if temp.count(".") >= 3 and i == 0:
				t2 = temp.replace(".", "/", 1)
			if temp.count(".") == 1 and i == 1:  # oshi-project:oshi-core:1.1
				pass
			if temp.count(".") == 1 and i == 1:
				pass
			downloads_lib_name.append(t2.replace(":", "/"))  # t2可能在赋值前引用,注意。但无法复现
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
							logger.error(KE)

					else:
						downloads_natives_list.append(item["classifiers"])
				except KeyError as e:
					raise CoreBootstrapMainError(
						"错误,未定义的数据.In 1.12.2.json. It doesn't have classifiers or the mojang update?")

		for item in library_download_list:
			if run_time_environment == 'nt':
				try:
					if item["natives"]["windows"] == "natives-windows":
						downloads_natives_sha1_list.append(item["downloads"]["classifiers"]["natives-windows"]["sha1"])
						downloads_natives_path_list.append(item["downloads"]["classifiers"]["natives-windows"]["path"])
						downloads_natives_url_list.append(item["downloads"]["classifiers"]["natives-windows"]["url"])
				except KeyError as KE:
					logger.error(KE)
		# print(downloads_artifact_inlib_list)
		# print(downloads_natives_list)		# 此列表被移除但未更改
		# print(downloads_lib_name)
		logger.debug(downloads_natives_path_list)
		logger.debug(run_time_environment)
		# 本来想把lib下载放在这里

		assets_index_path = os.path.join(mc_path, "assets\\indexes\\")  # 拼接index文件夹路径
		assets_objects_path = os.path.join(mc_path, "assets\\objects\\")

		if os.path.isdir(assets_index_path):  # indexes文件夹是否存在？
			pass
		else:
			os.chdir(os.path.join(mc_path, "assets"))
			os.mkdir("indexes")  # 所有版本的资源索引文件都在这

		file_index_objects = os.path.isfile(assets_index_path + assets_Index_id + ".json")  # 1.12.json文件是否存在?
		if file_index_objects:  # 如果file_index_objects的值为真（1.12.json存在的情况）
			sha1_json = _hash_get_val(assets_index_path + assets_Index_id + ".json", 'sha1')
			# 获得index中的1.12.json的hash(sha1)
			if assets_Index_sh1 == sha1_json:  # 如果文件的sha1值正常
				logger.info("资源索引文件正常")  # 1.12.json

			else:
				hash_yn = 0  # 重复了没有1.12.json的操作中的验证hash步骤
				hash_yn_too_many_try = 0
				sha1_json_else = _hash_get_val(assets_index_path + assets_Index_id + ".json", 'sha1')
				while hash_yn == 0:
					hash_yn_too_many_try = hash_yn_too_many_try + 1
					if hash_yn_too_many_try >= 10:
						raise CoreBootstrapMainError("验证资源索引文件时尝试次数过多")

					if assets_Index_sh1 == sha1_json_else:
						hash_yn = 1  # 如果hash正确就跳出循环
					else:
						os.chdir(assets_index_path)  # 到达应该下载的目录
						response = requests.get(assets_Index_download_url, headers=header_smcl)  # 下载
						with open(assets_Index_id + ".json", mode="wb+") as f:  # 写入
							f.write(response.content)
							f.close()
						sha1_json_else = _hash_get_val(assets_index_path + assets_Index_id + ".json", 'sha1')  # 获得index中的1.12.json的hash(sha1)
						os.chdir(running_src)  # 返回程序运行时目录

		else:  # 1.12.json不存在的情况
			os.chdir(assets_index_path)
			response = requests.get(assets_Index_download_url, headers=header_smcl)
			with open(assets_Index_id + ".json", mode="wb+") as f:
				f.write(response.content)
				f.close()
			sha1_json_else = _hash_get_val(assets_index_path + assets_Index_id + ".json", 'sha1')  # 获得index中的1.12.json的hash(sha1)
			hash_yn = 0  # 验证hash是否正确
			hash_yn_too_many_try = 0
			while hash_yn == 0:
				hash_yn_too_many_try = hash_yn_too_many_try + 1
				if hash_yn_too_many_try >= 10:  # 尝试次数过多就引发这个错误,防止程序一直卡在这
					raise CoreBootstrapMainError("验证资源索引文件时尝试次数过多")  # 可以考虑在参数上加上循环次数过多时候是否退出（core_bootstrap_main)

				if assets_Index_sh1 == sha1_json_else:
					hash_yn = 1
				else:
					os.chdir(assets_index_path)
					response = requests.get(assets_Index_download_url, headers=header_smcl)
					with open(assets_Index_id + ".json", mode="wb+") as f:
						f.write(response.content)
						f.close()
					sha1_json_else = _hash_get_val(assets_index_path + assets_Index_id + ".json", 'sha1')  # 获得index中的1.12.json的hash(sha1)
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
		os.chdir(running_src)  # 回去了 331

		asserts_json_objects = []
		asserts_json_objects_item = []
		asserts_json_objects_hash = []
		logger.info("正在获得资源名")
		with alive_bar(len(range(1305)), force_tty=True) as bar:
			for key, item in ret_read_json_val["objects"].items():  # 获得资源名
				bar()
				asserts_json_objects_item.append(item)
				asserts_json_objects.append(key)

		# print(asserts_json_objects_item)		# debug list dict
		# print(asserts_json_objects_item[0])		# debug dict list[0]

		for list_hash in asserts_json_objects_item:  # dict
			asserts_json_objects_hash.append(list_hash["hash"])  # dict to list

		os.chdir(assets_objects_path)  # 前往objects文件夹准备建立资源文件夹
		logger.info("正在检查资源文件")
		downloads_file_url_list = []
		with alive_bar(len(range(1305)), force_tty=True) as bar:
			for asserts_json_objects_hash_name in asserts_json_objects_hash:
				if os.path.isdir(os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2])):  # 资源文件夹是否存在
					if os.path.isfile(os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)):
						# 资源文件是否存在
						# 存在的话验证

						sha1_objects_else = _hash_get_val(
							os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2],
										 asserts_json_objects_hash_name),
							'sha1')  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。
						print("s:", sha1_objects_else)  # debug
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
								_downloads_file_url(link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name, (os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2],asserts_json_objects_hash_name)), True)  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性。。。
								sha1_objects_else = _hash_get_val((os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)), "sha1")  # emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性,这就和下载一样，这个名字有点问题。。。  # 获得objects中的资源文件的hash(sha1)
								os.chdir(assets_objects_path)  # 返回objects目录
								print(sha1_objects_else)  # debug
						link_downloads_assets = bmcl_link  # 恢复为原来使用的源
						bar()

					else:  # 资源文件不存在的情况,但资源文件需要的文件夹存在
						# _downloads_file_url(link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name, os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name), True)	# emm,由于最后面没有“/"但是这个是个文件就有些问题，我之前写对了，后来忘了这个特性。。。
						downloads_file_url_list.append(
							{
							"url": (link_downloads_assets + asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name),
							"path": (os.path.join(assets_objects_path, asserts_json_objects_hash_name[0:2], asserts_json_objects_hash_name)),
							"hash": asserts_json_objects_hash_name,
							"mkfile": True,
							"hash-check": True,
							"nolink_downloads_assets": asserts_json_objects_hash_name[0:2] + "/" + asserts_json_objects_hash_name,
							"assets_objects_path": assets_objects_path,
							"asserts_json_objects_hash_name": asserts_json_objects_hash_name
							}
						)
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
		logger.info("资源文件验证完毕")
		logger.info("正在下载lib文件")
		# lib文件下载
		i_2 = 0
		with alive_bar(len(range(37)), force_tty=True) as bar:
			for item in downloads_artifact_inlib_list:  # 单个lib文件路径
				tmp = item.split("/")
				tmplong = len(tmp)
				i = 0
				os.chdir(lib_path)
				# for items in tmp:		# 创建文件夹并下载
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
				# i += 1
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
						print(zBZ, "解压失败")
				elif i < tmplong - 1:  # 这里被淘汰
					os.mkdir(items)
					os.chdir(items)
				i += 1
			i_2 += 1

			os.chdir(lib_path)
		print("ok")

		# 下面是log4j的下载
		try:
			log4j2type = start_json["logging"]["client"]["type"]
			log4j2 = log4j2type.replace("-", ".")
			log4j2_download_url = start_json["logging"]["client"]["file"]["url"]
		except KeyError as KE:
			logger.error("log4j2下载链接获取失败")
			raise CoreBootstrapMainError("Install:log4j2下载链接获取失败")

		if not os.path.exists(log4j2):
			_downloads_file_url(log4j2_download_url, (os.path.join(mc_path, "versions", jar_version, log4j2)), True)
		print("All Right")

	else:		# GUI模式
		raise CoreBootstrapMainError("暂不支持")


class CoreStartLoginError(Exception):
	def __init__(self, message):
		super().__init__(message)


# 浏览器注册表信息
_browser_regs = {
	'IE': r"SOFTWARE\Clients\StartMenuInternet\IEXPLORE.EXE\DefaultIcon",
	'chrome': r"SOFTWARE\Clients\StartMenuInternet\Google Chrome\DefaultIcon",
	'edge': r"SOFTWARE\Clients\StartMenuInternet\Microsoft Edge\DefaultIcon",
	'firefox': r"SOFTWARE\Clients\StartMenuInternet\FIREFOX.EXE\DefaultIcon",
	'360': r"SOFTWARE\Clients\StartMenuInternet\360Chrome\DefaultIcon",
}


def get_browser_path(browser):
	"""
	获取浏览器的安装路径

	browser: 浏览器名称
	"""
	try:
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _browser_regs[browser])
	except FileNotFoundError:
		return None
	value, _type = winreg.QueryValueEx(key, "")
	print(value.split(',')[0])
	return value.split(',')[0]


def browser_init():
	edge_bit = True
	try:
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\Clients\StartMenuInternet")
	except FileNotFoundError:
		return None
	value, _type = winreg.QueryValueEx(key, "")

	driver_name = ""
	unzip_name = ""
	url = ""
	file_name = ""
	webbrowser_name = ""
	ret_list = []

	# if "IE" in value.split(',')[0]:
	# 	url = "https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.7.0/IEDriverServer_Win32_4.7.0.zip"
	# 	file_name = "IEDriverServer_Win32_4.7.0.zip"
	# 	unzip_name = "IEDriverServer_Win32_4.7.0"
	# 	driver_name = "IEDriverServer.exe"
	# 	webbrowser_name = "IE"

	running_src = os.getcwd()

	edge_src = get_browser_path("edge").replace(get_browser_path("edge").split(os.sep)[-1], "")
	print(edge_src)

	dom = xml.dom.minidom.parse(
		os.path.join(edge_src, "msedge.VisualElementsManifest.xml"))  # 读取edge文件夹下面的xml文件(包含版本信息)
	dom_ele = dom.documentElement
	ve = dom_ele.getElementsByTagName('VisualElements')
	ve_text = ve[0].toxml()  # 包含版本号的字符串文本
	rematch = re.match(r'(.*)\"(.*)\\VisualElements\\Logo.png', ve_text)
	edge_version = rematch.group(2)  # 匹配得到版本号
	print(edge_version)
	url = "https://msedgedriver.azureedge.net/{}/edgedriver_win64.zip".format(edge_version)
	file_name = "{}_edgedriver_win64.zip".format(edge_version)
	unzip_name = "{}_edgedriver_win64".format(edge_version)
	driver_name = "msedgedriver.exe"
	webbrowser_name = "Edge"

	if "Edge" in value.split(',')[0]:
		edge_src = get_browser_path("edge").replace(get_browser_path("edge").split(os.sep)[-1], "")
		print(edge_src)

		dom = xml.dom.minidom.parse(os.path.join(edge_src, "msedge.VisualElementsManifest.xml"))  	# 读取edge文件夹下面的xml文件(包含版本信息)
		dom_ele = dom.documentElement
		ve = dom_ele.getElementsByTagName('VisualElements')
		ve_text = ve[0].toxml()  # 包含版本号的字符串文本
		rematch = re.match(r'(.*)\"(.*)\\VisualElements\\Logo.png', ve_text)
		edge_version = rematch.group(2)  # 匹配得到版本号
		print(edge_version)
		url = "https://msedgedriver.azureedge.net/{}/edgedriver_win64.zip".format(edge_version)
		file_name = "{}_edgedriver_win64.zip".format(edge_version)
		unzip_name = "{}_edgedriver_win64".format(edge_version)
		driver_name = "msedgedriver.exe"
		webbrowser_name = "Edge"

	if "Firefox" in value.split(',')[0] or "FIREFOX.EXE" in value.split(','):
		url = "https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-win32.zip"
		file_name = "geckodriver-v0.32.0-win32.zip"
		unzip_name = "geckodriver-v0.32.0-win32"
		driver_name = "geckodriver.exe"
		webbrowser_name = "Firefox"

	try:
		r = requests.get(url)
	except requests.exceptions.SSLError as RESE:
		print(RESE)
		r = requests.get(url, verify=False)

	temp_src = os.getenv("TEMP")
	file_src = os.path.join(temp_src, file_name)
	os.chdir(temp_src)
	temp_dir_name = "SMCL_{}".format(str(time.time()))
	os.mkdir(temp_dir_name)
	os.chdir(temp_dir_name)

	# time.time_ns() ?

	with open(file_name, mode="wb+") as f:
		f.write(r.content)
		f.close()

	try:
		with zipfile.ZipFile(file_name, mode="r") as archive:
			archive.extractall(unzip_name)
			archive.close()
	except zipfile.BadZipFile as zBZ:
		print(zBZ, "解压失败")

	os.chdir(running_src)

	ret_list.append(os.path.join(temp_dir_name, unzip_name, driver_name))
	ret_list.append(webbrowser_name)
	ret_list.append(temp_dir_name)

	return ret_list
	#env = os.environ
	#print(env["LOCALAPPDATA"])		# 可获得local appdata的路径

def core_start_Login(Refresh_Token, refresh_token_str=None, Mojang_MS_login=False, MS_login=False, back_url: str = None, Mojang_login=False):
	"""
	Refresh_Token:更新AccessToken令牌
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

			browser_init_list = browser_init()
			webdiver_src = browser_init_list[0]
			try:
				driver = None
				if browser_init_list[1] == "Edge":
					s = selenium.webdriver.edge.service.Service(webdiver_src)  # get_browser_path("chrome"))
					driver = webdriver.Edge(service=s)

				elif browser_init_list[1] == "Firefox":
					s = selenium.webdriver.edge.service.Service(webdiver_src)
					driver = webdriver.Edge(service=s)

				#driver = webdriver.Chrome(service=s)
				driver.get("https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf")
				while "code=" not in driver.current_url:
					back_url = driver.current_url
				back_url = driver.current_url
			except Exception:
				logger.error("此版本不支持除Chrome外的其他浏览器")
				raise CoreStartLoginError("浏览器错误:浏览器不受支持")

			try:
				print(back_url)
				back_url_code_place = back_url.find("code=")
				back_url_code_place_end = back_url.find("&")
				back_url = back_url[back_url_code_place + 5:back_url_code_place_end]
			except AttributeError as eab:

				if eab == "'int' object has no attribute 'replace'":
					logger.error(("back_url不应该是int类型,应该是str", eab))
					raise CoreStartLoginError(("back_url不应该是int类型,应该是str", eab))

				elif eab == "'float' object has no attribute 'replace'":
					logger.error(("back_url不应该是float类型,应该是str", eab))
					raise CoreStartLoginError(("back_url不应该是float类型,应该是str", eab))

				elif eab == "'NoneType' object has no attribute 'replace'":
					logger.error(("back_url不应该是NoneType类型,应该是str", eab))
					raise CoreStartLoginError(("back_url不应该是NoneType类型,应该是str", eab))

				logger.error(("未知错误", eab))
				raise CoreStartLoginError(eab)
			if "M.R3_BAY" in back_url:
				logger.info("OAuth code提取成功")
			else:
				logger.error("无法提取到OAuth code")
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

			# q = webbrowser.get().open_new("https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf")
			# print(q)


			MS_authcode = back_url  # 填入code进行访问OAuth,debug时可直接填入code=后&前的code
			post_ms_AT = \
				"client_id=00000000402b5328&code=" + MS_authcode + \
				"&grant_type=authorization_code&redirect_uri=https://login.live.com/oauth20_desktop.srf" + \
				"&scope=service::user.auth.xboxlive.com::MBI_SSL"

			r = requests.post(MS_login_token_get_link, data=post_ms_AT, headers=MS_head)
			post_json_ms_token_back_json = json.loads(r.text)
			try:  # 看看有没有error这个键
				post_json_ms_token_back_json_error = post_json_ms_token_back_json["error"]
				print(post_json_ms_token_back_json_error)
				print(post_json_ms_token_back_json)
				if post_json_ms_token_back_json[
					"error_description"] == "The provided value for the 'code' parameter is not valid. The code has expired.":
					print("验证过期")  # 过期了
					raise CoreStartLoginError("无法通过Microsoft OAuth,验证过期.请重新进行登录操作")
				else:
					logger.error("无法通过Microsoft OAuth " + post_json_ms_token_back_json["error_description"])
					raise CoreStartLoginError(
						"无法通过Microsoft OAuth\n" + post_json_ms_token_back_json["error_description"])
			# 不知道哪里错了,抛出错误
			except KeyError as KE:
				pass

			print(r.text)  # debug
			MS_T_back_A_T = post_json_ms_token_back_json["access_token"]  # 全称为 MS_Token_back_Access_Token
			MS_T_back_R_T = post_json_ms_token_back_json["refresh_token"]  # 全称为 MS_Token_back_Refresh_Token
			MS_T_back_user_id = post_json_ms_token_back_json["user_id"]  # 全称为 MS_Token_back_user_id
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
			post_xbl_auth_json = json.dumps(post_xbl_auth)  # 将字典转为json格式
			print(post_xbl_auth_json)
			r = requests.post(XBL_login_token_get_link, data=post_xbl_auth_json, headers=XBL_head)
			print(r.text)
			XBL_ret_json = json.loads(r.text)
			try:
				XBL_ret_token = XBL_ret_json["Token"]
				XBL_ret_xui_list = XBL_ret_json["DisplayClaims"]["xui"][0]
				XBL_ret_token_ush = XBL_ret_xui_list["uhs"]  # 获得user hash
			except KeyError as KE:
				print(XBL_ret_json)
				raise CoreStartLoginError("XBL认证失败\n" + XBL_ret_json)
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
			XSTS_head = XBL_head  # XSTS和XBL的请求头一致
			post_xsts_auth_json = json.dumps(post_xsts_auth)  # 将字典转为json格式

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

			ReturnDict = {"name_MS_xbox": name_MS_xbox, "uuid_MS_xbox": uuid_MS_xbox, "MinecraftAccessToken": MinecraftAccessToken, "MS_T_back_R_T": MS_T_back_R_T}
			return ReturnDict


		elif Mojang_login:
			post_json = 9
			r = requests.post(mojang_Yggdrasil + "/authenticate", data=post_json, headers=header)

	if Refresh_Token:
		# 更新Refresh_Token并刷新AccessToken
		XBL_head = {
			"cookie": cookie,
			"Accept": "application/json",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "zh-CN,zh;q=0.9",
			"Connection": "keep-alive",
			"Content-Type": "application/json",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
		}
		MS_head = {
			"cookie": cookie,
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "zh-CN,zh;q=0.9",
			"Connection": "keep-alive",
			"Content-Type": "application/x-www-form-urlencoded",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
		}
		post_ms_AT = \
			"client_id=00000000402b5328" \
			"&refresh_token=" + refresh_token_str + \
			"&grant_type=refresh_token" \
			"&redirect_uri=https://login.live.com/oauth20_desktop.srf" + \
			"&scope=service::user.auth.xboxlive.com::MBI_SSL"

		r = requests.post(MS_login_token_get_link, data=post_ms_AT, headers=MS_head)
		post_json_ms_token_back_json = json.loads(r.text)
		try:  # 看看有没有error这个键
			post_json_ms_token_back_json_error = post_json_ms_token_back_json["error"]
			print(post_json_ms_token_back_json_error)
			print(post_json_ms_token_back_json)
			if post_json_ms_token_back_json["error_description"] == "The provided value for the 'code' parameter is not valid. The code has expired.":
				print("刷新令牌过期")  # 过期了
				raise CoreStartLoginError("无法通过Microsoft OAuth,刷新令牌过期.请重新进行登录操作")
			else:
				logger.error("无法通过Microsoft OAuth " + post_json_ms_token_back_json["error_description"])
				raise CoreStartLoginError("无法通过Microsoft OAuth\n" + post_json_ms_token_back_json["error_description"])
		# 不知道哪里错了,抛出错误
		except KeyError as KE:
			pass

		print(r.text)  # debug
		MS_T_back_A_T = post_json_ms_token_back_json["access_token"]  # 全称为 MS_Token_back_Access_Token
		MS_T_back_R_T = post_json_ms_token_back_json["refresh_token"]  # 全称为 MS_Token_back_Refresh_Token
		MS_T_back_user_id = post_json_ms_token_back_json["user_id"]  # 全称为 MS_Token_back_user_id
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
		post_xbl_auth_json = json.dumps(post_xbl_auth)  # 将字典转为json格式
		print(post_xbl_auth_json)
		r = requests.post(XBL_login_token_get_link, data=post_xbl_auth_json, headers=XBL_head)
		print(r.text)
		XBL_ret_json = json.loads(r.text)
		try:
			XBL_ret_token = XBL_ret_json["Token"]
			XBL_ret_xui_list = XBL_ret_json["DisplayClaims"]["xui"][0]
			XBL_ret_token_ush = XBL_ret_xui_list["uhs"]  # 获得user hash
		except KeyError as KE:
			print(XBL_ret_json)
			raise CoreStartLoginError("XBL认证失败\n" + XBL_ret_json)
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
		XSTS_head = XBL_head  # XSTS和XBL的请求头一致
		post_xsts_auth_json = json.dumps(post_xsts_auth)  # 将字典转为json格式

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

		ReturnDict = {"name_MS_xbox": name_MS_xbox, "uuid_MS_xbox": uuid_MS_xbox, "MinecraftAccessToken": MinecraftAccessToken, "MS_T_back_R_T": MS_T_back_R_T}
		return ReturnDict


def core_start_IN(java_path, mc_path, launcher_name, username, uuid_val, aT, launcher_name_version, uuid_yn=False, G1NewSizePercent_size="20", G1ReservePercent_size="20", Xmn="128m", Xmx="1024M", cph=None):  # java_path以后可以升个级作判断，自己检测Java
	"""
		java_path:Java路径(字符串)(可以填写java)

		mc_path:游戏目录（到.minecraft)

		launcher_name:需要启动的游戏版本(字符串)

		username:玩家名（字符串）

		uuid_val:uuid(字符串)

		aT:accessToken位,用于正版登录。一般随便填（盗版登录）（字符串）

		launcher_name_version:启动器版本

		uuid_yn:是否有(需要生成)uuid(默认为False需要生成)(可不填(需要生成))(bool)

		G1NewSizePercent_size:20(字符串)

		G1ReservePercent_size:20(字符串)

		Xmn:最小内存(默认128m)

		Xmx:最大分配内存(默认1024M)

		cph:此位保留,无用处。不返回。可填None.
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
	# uuid_yn:是否有（需要生成）uuid(默认为False需要生成）（可不填（需要生成））（bool）
	# Xmn:最小内存（默认128m）
	# Xmx:最大分配内存（默认1024M)
	# cph:此位保留，无用处。不返回。可填None.
	# 这个版本还在写，仅为测试版本。原版启动正常，forge启动有问题。
	# forge完成(补了一下，之前写完后忘了加)
	if os.name == "nt":		# 如果平台为Windows，则执行添加双引号的操作
		temp_mc_path = ""		# 设置一个temp变量
		java_path = '"{}"'.format(java_path)		# 将java_path重新赋值为修改后的java_path
		if " " in mc_path:  # mc_path里面是否有空格?
			# split_mc_path = mc_path.split(os.sep)		# 分割mc_path(用os.sep可以防止平台间的路径分隔符不同带来的问题)
			# i_f_m_p = 0
			# for item in split_mc_path:
			# 	if " " in item:		# 如果item里面有空格
			# 		if i_f_m_p == 0:
			# 			item = '{0}"{1}"'.format(os.sep, item)
			# 		else:
			# 			item = '"{}"'.format(item)
			#
			# 	temp_mc_path = os.path.join(temp_mc_path, item)  # 将分割后的路径重新拼回去

			# mc_path = temp_mc_path
			#mc_path = '"{}"'.format(mc_path)
			print(mc_path)
			#del temp_mc_path  # 解除占用（真的有必要吗？）
			#del split_mc_path  # 解除占用（真的有必要吗？）

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
		try:
			downloads_things_list.append(item["downloads"])
		except KeyError as e:
			pass

	library_num = i

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
	if not uuid_yn:  # 如果没有uuid那就生成一个
		launcher_uuid_uuid = uuid.uuid4()
		launcher_uuid = launcher_uuid_uuid.hex
		uuid_val = launcher_uuid

	global forge_things_g
	forge_things_g = None

	if start_json["mainClass"] == "net.minecraft.client.main.Main":

		if _Check_versions_in(launcher_name) < _Check_versions_in("1.8.0"):  # 这是低于1.8.0的解决方案
			for downloads_artifact_inlib in downloads_artifact_inlib_list:
				temp_2 = temp_2 + (os.path.join(lib_path, (downloads_artifact_inlib.replace("/", "\\")) + ";"))
			print(downloads_artifact_inlib)
			the_temp = "\\"
			temp_3 = client_jar_path + the_temp + gameversion + ".jar" + " net.minecraft.client.main.Main" + " --username " + username + " --version " + gameversion + " --gameDir " + mc_path + \
					 " --assetsDir " + assets_index_path + \
					 " --assetIndex " + assets_index_name + \
					 " --uuid " + uuid_val + \
					 " --accessToken " + aT + \
					 " --userProperties {}" + \
					 " --userType Legacy" + \
					 ' --versionType ' + launcher_name_self + \
					 " --width 854" + \
					 " --height 480"
			subprocess.run(temp_2 + temp_3)
			if uuid_yn:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return return_IN_list
			else:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return_IN_list.append(launcher_uuid)
				return return_IN_list

		else:
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
			subprocess.run(temp_2 + temp_3)
			if uuid_yn:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return return_IN_list
			else:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return_IN_list.append(launcher_uuid)
				return return_IN_list

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

		if _Check_versions_in(launcher_name) < _Check_versions_in("1.8.0"):  # 这是低于1.8.0的解决方案
			temp_3 = temp_3_t + " cpw.mods.modlauncher.Launcher" + " --username " + username + " --version " + gameversion + " --gameDir " + mc_path + \
					 " --assetsDir " + assets_index_path + \
					 " --assetIndex " + assets_index_name + \
					 " --uuid " + uuid_val + \
					 " --accessToken " + aT + \
					 " --userProperties {}" + \
					 " --userType Legacy" + \
					 ' --versionType ' + launcher_name_self + \
					 " --width 854" + \
					 " --height 480"
		else:
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
			return_IN_list = []
			return_IN_list.append("ok")
			return_IN_list.append((temp_2 + temp_3))
			return return_IN_list
		else:
			return_IN_list = []
			return_IN_list.append("ok")
			return_IN_list.append((temp_2 + temp_3))
			return_IN_list.append(launcher_uuid)
			return return_IN_list

	elif start_json["mainClass"] == "net.fabricmc.loader.impl.launch.knot.KnotClient":

		argument_forge = []  # forge
		for item in pathes_other:  # forge
			if item["id"] == "fabric":  # forge
				fabric = item  # forge

		for library_download_farbric in library_download_list:
			try:
				if library_download_farbric["url"] == "https://maven.fabricmc.net/":		# 判断是否是fabric的lib
					library_download_farbric = library_download_farbric["name"]		# 获取name
					library_download_farbric_jar_name_place =  library_download_farbric.find(":")		# 保存“:” 号第一次出现的位置
					library_download_farbric_jar_name = library_download_farbric[library_download_farbric_jar_name_place+1:]
					logger.debug("library_farbric_jar_name:{}".format(library_download_farbric_jar_name))
					if "net" not in library_download_farbric:
						# 分两种情况,这里处理的是类似 "name": "net.fabricmc:access-widener:2.1.0"这样的name
						temp_2 = temp_2 + (os.path.join(lib_path, ((library_download_farbric.replace("/", "\\").replace(":", "\\")).replace(".", "\\", 2)), library_download_farbric_jar_name.replace(":", "-") + ".jar;"))		# 进行格式化字符串并添加到lib暂存区

					else:
						# 分两种情况,这里处理的是类似 "name": "org.ow2.asm:asm:9.3" 这样的name
						temp_2 = temp_2 + (os.path.join(lib_path, ((library_download_farbric.replace("/", "\\").replace(":", "\\")).replace(".", "\\", 1)), library_download_farbric_jar_name.replace(":", "-") + ".jar;"))		# 进行格式化字符串并添加到lib暂存区

			except KeyError as eke:
				pass

		if _Check_versions_in(launcher_name) < _Check_versions_in("1.8.0"):  # 这是低于1.8.0的解决方案
			for downloads_artifact_inlib in downloads_artifact_inlib_list:  # 但我并不确定在这里会有用,毕竟是神奇的fabric
				temp_2 = temp_2 + (os.path.join(lib_path, (downloads_artifact_inlib.replace("/", "\\")) + ";"))
			print(downloads_artifact_inlib)
			the_temp = "\\"
			temp_3 = client_jar_path + the_temp + gameversion + ".jar" + " net.fabricmc.loader.impl.launch.knot.KnotClient" + " --username " + username + " --version " + gameversion + " --gameDir " + mc_path + \
					 " --assetsDir " + assets_index_path + \
					 " --assetIndex " + assets_index_name + \
					 " --uuid " + uuid_val + \
					 " --accessToken " + aT + \
					 " --userProperties {}" + \
					 " --userType mojang" + \
					 ' --versionType ' + launcher_name_self + \
					 " --width 854" + \
					 " --height 480"
			subprocess.run(temp_2 + temp_3)
			if uuid_yn:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return return_IN_list
			else:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return_IN_list.append(launcher_uuid)
				return return_IN_list

		else:
			for downloads_artifact_inlib in downloads_artifact_inlib_list:
				temp_2 = temp_2 + (os.path.join(lib_path, (downloads_artifact_inlib.replace("/", "\\")) + ";"))
			print(downloads_artifact_inlib)
			the_temp = "\\"
			temp_3 = client_jar_path + the_temp + gameversion + ".jar" + " net.fabricmc.loader.impl.launch.knot.KnotClient" + " --username " + username + " --version " + gameversion + " --gameDir " + mc_path + \
					 " --assetsDir " + assets_index_path + \
					 " --assetIndex " + assets_index_name + \
					 " --uuid " + uuid_val + \
					 " --accessToken " + aT + \
					 " --userType mojang" + \
					 ' --versionType ' + launcher_name_self + \
					 " --width 854" + \
					 " --height 480"
			subprocess.run(temp_2 + temp_3)
			if uuid_yn:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return return_IN_list
			else:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return_IN_list.append(launcher_uuid)
				return return_IN_list

	elif start_json["mainClass"] == "net.minecraft.launchwrapper.Launch":

		if _Check_versions_in(launcher_name) < _Check_versions_in("1.8.0"):  # 这是低于1.8.0的解决方案
			for downloads_artifact_inlib in downloads_artifact_inlib_list:
				temp_2 = temp_2 + (os.path.join(lib_path, (downloads_artifact_inlib.replace("/", "\\")) + ";"))
			print(downloads_artifact_inlib)
			the_temp = "\\"
			temp_3 = client_jar_path + the_temp + gameversion + ".jar" + " net.minecraft.launchwrapper.Launch" + " --username " + username + " --version " + gameversion + " --gameDir " + mc_path + \
					 " --assetsDir " + assets_index_path + \
					 " --assetIndex " + assets_index_name + \
					 " --uuid " + uuid_val + \
					 " --accessToken " + aT + \
					 " --userProperties {}" + \
					 " --userType Legacy" + \
					 ' --versionType ' + launcher_name_self + \
					 " --width 854" + \
					 " --height 480"
			subprocess.run(temp_2 + temp_3)
			if uuid_yn:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return return_IN_list
			else:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return_IN_list.append(launcher_uuid)
				return return_IN_list

		else:
			for downloads_artifact_inlib in downloads_artifact_inlib_list:
				temp_2 = temp_2 + (os.path.join(lib_path, (downloads_artifact_inlib.replace("/", "\\")) + ";"))
			print(downloads_artifact_inlib)
			the_temp = "\\"
			temp_3 = client_jar_path + the_temp + gameversion + ".jar" + " net.minecraft.launchwrapper.Launch" + " --username " + username + " --version " + gameversion + " --gameDir " + mc_path + \
					 " --assetsDir " + assets_index_path + \
					 " --assetIndex " + assets_index_name + \
					 " --uuid " + uuid_val + \
					 " --accessToken " + aT + \
					 " --userType Legacy" + \
					 ' --versionType ' + launcher_name_self + \
					 " --width 854" + \
					 " --height 480"
			subprocess.run(temp_2 + temp_3)
			if uuid_yn:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return return_IN_list
			else:
				return_IN_list = []
				return_IN_list.append("ok")
				return_IN_list.append((temp_2 + temp_3))
				return_IN_list.append(launcher_uuid)
				return return_IN_list


def core_Get_Version_list(list_type, link_type, SVONLY=None):
	"""
list_type: The type of Minecraft
link_type: BMCLAPI or mojang?
SVONLY: You don't need to care about it.It's useless to you.
	"""

	release_list = []
	if link_type == "BMCLAPI" or "Latest":
		link_get_version_list = "https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json"
	else:
		link_get_version_list = "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"

	r = requests.get(link_get_version_list, headers=header_smcl)
	if link_type == "Latest" and link_get_version_list == "https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json":
		# 判断bmclapi是不是最新的(默认mojang的是最新的)
		r2 = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest_v2.json", headers=header_smcl)
		r_hash = _hash_get_val(r.text, "sha1", "str")
		r2_hash = _hash_get_val(r2.text, "sha1", "str")
		if not r2_hash == r_hash:
			logger.info(r_hash)
			logger.info(r2_hash)
			r = r2

	version_json_v1 = r.json()

	if list_type == "LTS" or list_type == "release":
		for items in version_json_v1["versions"]:
			if not items["type"] == "snapshot" and not items["type"] == "old_beta" and not items["type"] == "old_alpha":
				release_list.append(items)
		return release_list


class CoreMcserverInitializationError(Exception):
	def __init__(self, message):
		super().__init__(message)


def core_mcserver(server_version, server_type=None):
	"""
	server_version:服务端版本
	server_type：服务端类型(Vanilla/paper/Forge/spigot/sponge/spongeFore)
	"""
	# 未完成
	const.USER_NAME = os.getlogin()
	user_name = const.USER_NAME
	if not os.name == "nt":
		logger.critical("暂不支持除Windows NT 平台外的操作系统{}".format(os.name))
		CoreMcserverInitializationError("暂不支持除Windows NT 平台外的操作系统{}".format(os.name))

	if not os.path.exists(os.path.join("C:\\Users\\", user_name, "", ".minecraftserver")):
		os.chdir(os.environ.get["appdata"])
	if server_type == "Vanilla" or server_type is None:
		_downloads_file_url()


class CoreForgeInstallError(Exception):
	def __init__(self, message):
		super().__init__(message)


def core_Forge_install_clint_version_Get(version=None, type="All"):
	"""
	此函数用来获取Forge可用版本列表
	如果什么也不填就返回可使用Forge的Minecraft版本
	只输入某个版本（version）返回此版本的所有build号和所有可用版本号
	输入某个版本（version）和某个模式（type)可获取对应模式的返回。如，type=All时返回此版本Forge的所有build号和所有可用版本号
	type=build时返回此版本的所有build号
	type=versions时返回此版本Forge所有可用版本号
	如果version不填或为None那么返回支持Forge的列表
	"""
	r = requests.get("https://bmclapi2.bangbang93.com/forge/minecraft", headers=header_smcl)
	rt = r.json()

	r_Forge_version_list = requests.get("https://bmclapi2.bangbang93.com/forge/minecraft/{}".format(version), headers=header_smcl)
	Forge_version_list = r_Forge_version_list.json()
	forge_build_list = []
	forge_versions_list = []
	for item in Forge_version_list:
		forge_build_list.append(item["build"])  # 将build版本号添加到列表
		forge_versions_list.append(item["version"])  # 将版本号添加到列表
	if version is None:
		return rt  # 返回受Forge支持的Minecraft版本列表

	if version in rt:
		if type == "All" or type == "all" or type == "ALL":  # 这里最规范的用法应该是All其次是all
			return forge_build_list, forge_versions_list
		elif type == "build":
			return forge_build_list
		elif type == "versions":
			return forge_versions_list


def core_Forge_install_clint(version_game, mc_path, VT_bit, version_forge, forge_install_headless_type = "BMCLAPI"):
	# 未完成
	r = requests.get("https://bmclapi2.bangbang93.com/forge/minecraft", headers=header_smcl)
	rt = r.json()
	logger.debug("version={}".format(version_game))
	if version_game == "":
		logger.critical("version变量不合法,它不应该为空")
		CoreForgeInstallError("version变量不合法,它不应该为空")
	if version_game not in rt:
		logger.critical("{}版本不支持Forge,无法下载".format(version_game))
		CoreForgeInstallError("此版本不支持Forge!")

	# 常量定义区
	const.RUNNING_PATH = os.getcwd()
	const.GAME_PATH = os.path.join(mc_path, 'versions', version_game)
	const.FORGE_INSTALL_HEADLESS_PATH = "forge-installer-headless.jar"
	const.FORGE_INSTALL_HEADLESS_BMCLAPI_PATH = "forge-install-bootstrapper.0.2.0.jar"

	# 此区域无实际意义,主要用于方便程序编写（让语法提示器正常工作）
	game_path = const.GAME_PATH  # 指向const.GAME_PATH的指针(伪)
	forge_install_headless_path = const.FORGE_INSTALL_HEADLESS_PATH  # 指向const.FORGE_INSTALL_HEADLESS_PATH的指针(伪)
	forge_install_headless_BMCLAPI = const.FORGE_INSTALL_HEADLESS_BMCLAPI_PATH  # 指向const.FORGE_INSTALL_HEADLESS_BMCLAPI_PATH的指针(伪)
	running_path = const.RUNNING_PATH  # 指向const.RUNNING_PATH的指针(伪)

	r_Forge_version_list = requests.get("https://bmclapi2.bangbang93.com/forge/minecraft/{}".format(version_game), headers=header_smcl)
	Forge_version_list = r_Forge_version_list.json()
	print(Forge_version_list)
	forge_build_list = []
	forge_versions_list = []
	for item in Forge_version_list:
		forge_build_list.append(item["build"])  # 将build版本号添加到列表
		forge_versions_list.append(item["version"])  # 将版本号添加到列表

	if version_forge == "latest":
		# for items in forge_versions_list:
		# print(_Check_versions_in(items)) 本来想用这个的,但一想下面这个方法更简洁

		for item in Forge_version_list:
			if item["build"] == max(forge_build_list):
				forge_downloads_clint_install = item["files"]
				forge_downloads_clint_install_version = item["version"]

				logger.debug("latest-jar:{}".format(forge_downloads_clint_install))  # log记录jar json
				logger.debug("latest-build-num:{}".format(max(forge_build_list)))  # log记录build
				logger.debug("latest-jar-version:{}".format(item["version"]))

		for items in forge_downloads_clint_install:
			if items["format"] == "jar":
				forge_downloads_clint_install_hash = items["hash"]

				logger.debug("latest-jar-hash:{}".format(forge_downloads_clint_install_hash))  # log记录jar hash值

		logger.debug("下载链接获取构造: https://bmclapi2.bangbang93.com/forge/download/{}".format(max(forge_build_list)))  # log记录跳转链接获取链接

		logger.debug("请稍后,这可能需要一段时间")
		r = requests.get("https://bmclapi2.bangbang93.com/forge/download/{}".format(max(forge_build_list)), headers=header_smcl)
		logger.debug("forge-install-jar下载完毕")

		if not VT_bit:

			os.chdir(game_path)
			if not os.path.exists("forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version)):
				os.chdir(running_path)
				logger.debug("forge安装包名为:forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version))

				_downloads_file_url("https://bmclapi2.bangbang93.com/forge/download/{}".format(max(forge_build_list)), (os.path.join(game_path, "forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version))), True)

				logger.debug("forge安装目录为:{}".format((os.path.join(mc_path, "forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version)))))
			else:

				logger.info("已检测到forge安装包，正在验证是否可用")
				if _hash_get_val(("forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version)), "sha1") == forge_downloads_clint_install_hash:
					logger.info("此安装包可用")
					os.chdir(running_path)

				else:
					xhkz = True
					while xhkz:
						logger.info("此安装包不可用,正在尝试重新下载")
						_downloads_file_url("https://bmclapi2.bangbang93.com/forge/download/{}".format(max(forge_build_list)), (os.path.join(game_path, "forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version))), True)
						if _hash_get_val(("forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version)), "sha1") == forge_downloads_clint_install_hash:
							logger.info("重新下载完毕")
							os.chdir(running_path)
							xhkz = False

			if forge_install_headless_type == "FIHL_xfl03":
				logger.debug("执行的安装的命令:{}".format('java -cp "{0};{1}" me.xfl03.HeadlessInstaller -installClient {2}'.format(forge_install_headless_path, (os.path.join(game_path, "forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version))), game_path)))
				logger.info("正在进行安装,这可能需要一段时间")
				os.system('java -cp "{0};{1}" me.xfl03.HeadlessInstaller -installClient {2}'.format(forge_install_headless_path, (os.path.join(game_path, "forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version))), game_path))

			elif forge_install_headless_type == "BMCLAPI":

				logger.debug("执行的安装的命令:{}".format('java -cp "{0};{1}" com.bangbang93.ForgeInstaller {2}'.format((os.path.join(game_path, "forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version))), forge_install_headless_BMCLAPI, game_path)))
				logger.info("正在进行安装,这可能需要一段时间")
				os.system('java -cp "{0};{1}" com.bangbang93.ForgeInstaller {2}'.format((os.path.join(game_path, "forge-{0}-{1}-installer.jar".format(version_game, forge_downloads_clint_install_version))), forge_install_headless_BMCLAPI, game_path))
				return 0
		else:

			logger.error("暂不支持版本隔离模式")
			CoreForgeInstallError("暂不支持版本隔离模式")
