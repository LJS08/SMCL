import tkinter as tk
import tkinter.filedialog

import Core.config as config


def setting_page():
    def write():
        config.write(playername=name, dotmc=dotmc, java=java, ram=memory)

    def choosefile():
        jpath = tk.filedialog.askopenfilenames(filetypes=[('java/javaw程序', '.exe')])
        if jpath:
            java.delete(0, "end")
            java.insert(0, '"' + jpath[0] + '"')

    def choosefolder():
        dpath = tk.filedialog.askdirectory()
        if dpath:
            dotmc.delete(0, "end")
            dotmc.insert(0, dpath)

    window = tk.Tk()
    window.geometry("640x360")
    window.title("SMCL Lite")
    window.resizable(0, 0)

    infos = config.read()

    # java路径模块
    tk.Label(window, text="java路径").place(x=0, y=5)
    java = tk.Entry(window, show=None)
    java.place(x=90, y=5, width=400)
    java.insert(0, infos["java"])
    btn_choosejava = tk.Button(window, command=choosefile, text="View...")
    btn_choosejava.place(x=475, y=0)

    # minecraft路径模块
    tk.Label(window, text=".minecraft路径").place(x=0, y=30)
    dotmc = tk.Entry(window, show=None)
    dotmc.place(x=90, y=30, width=400)
    dotmc.insert(0, infos[".mc"])
    btn_choosejava = tk.Button(window, command=choosefolder, text="View...")
    btn_choosejava.place(x=475, y=25)

    # 玩家名模块
    tk.Label(window, text="玩家名").place(x=0, y=55)
    name = tk.Entry(window, show=None)
    name.place(x=90, y=55, width=200)
    name.insert(0, infos["playername"])

    # 内存分配模块
    tk.Label(window, text="内存分配").place(x=0, y=80)
    memory = tk.Entry(window, show=None)
    memory.place(x=90, y=80)
    memory.insert(0, infos["ram"])

    btn_ok = tk.Button(window, text="OK", command=write)

    btn_ok.place(x=300, y=180, width=40)

    window.mainloop()
