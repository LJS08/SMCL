# SMCL

### 介绍
 _**SMCL开发中**_ 
 
SMCL 是一款 Minecraft 启动器.

## Depencies

| Depency                | Usage                              | Source                                                                    |  
|------------------------|------------------------------------|---------------------------------------------------------------------------|  
| alive_progress         | Show progress                      | Python 3.9                                                                |  
| platform, sys          | Geting system informations         | Python 3.9                                                                |  
| subprocess             | Executing commands                 | Python 3.9                                                                |  
| concurrent, threading  | Multi-threading capabilities       | Python 3.9                                                                |  
| requests               | Downloading files & Executing APIs | Python 3.9                                                                |
| sqlite3                | Feature                            | Python 3.9                                                                |
| selenium               | Login Account                      | Python 3.9                                                                |
| tempfile               | Enhancement Download               | Python 3.9                                                                |
| time                   | Get Local Time&&Sleep Theard       | Python 3.9                                                                |
| uuid                   | New a uuid                         | Python 3.9                                                                |
| winreg                 | Get the browser src                | Python 3.9                                                                |
| xml,xmlrpc             | Parse xml                          | Python 3.9                                                                |
| zipfile                | Decompression zip flies            | Python 3.9                                                                |
| hashlib                | Check Hash                         | Python 3.9                                                                |
| loguru                 | logging                            | Python 3.9                                                                |
| json                   | JSON dumping&writing               | Python 3.9                                                                |  
| Core                   | Core                               | SMCL                                                                      |  
| tkinter,wxPython       | GUI                                | Python 3.9                                                                |  

### 平台支持

|CPU 架构\操作系统|视窗|Linux|MacOS（X）|
|-|-|-|-|
|x64|✔|📌|📌|
|x86|📌|📌|❌|
|ARM64|📌|📌|📌|
|ARM32|❌|❌|❌|

✔ - 完全支持（已验证）

❔ - 已完成但未经验证（某些功能可能不可用）

📌 - 计划做

❌ - 不支持

目前SMCL仍在开发中, 敬请期待。

### 项目结构

#### 文件夹

formal : 由于历史原因, 该目录中存放源代码文件

(注意, 以下以 formal 为根文件夹进行说明)

/Console : CUI(命令行UI相关)

/Core : 核心包, 大部分功能的实现在其中

/Update : 与自动更新有关, 目前未完成

/View : SMCL 的 UI

/image : 绝大多数UI的图片和依赖的背景图

/tools : 由于历史原因, 有少量的功能实现在该包中

#### 文件

main.py : 程序运行的起点, 入口点.

/Console/console_main.py : 整个CUI

/Core/core_start.py : 大部分的功能实现, Core 的始与终.

/Core/constant.py : "常量"的实现

### 语言
  _Python_ 

**使用建议：建议使用Python3.9及以上的64位版本**
