import tkinter as tk
import tkinter.filedialog

import Core.config as config
import Core.core_advanced_settings
import wx

def setting_page(advanced_settings_bit):

    def advanced_settings():
        advanced_settings_app = wx.App()  # 创建窗口对象

        frm = Core.core_advanced_settings.Advanced_Settings()  # 初始化窗口对象
        frm.Show()  # 显示界面

        advanced_settings_app.MainLoop()


    def write():
        name = name_entry.get()
        java = java_entry.get()
        dotmc = dotmc_entry.get()
        memory = memory_entry.get()
        print("name =", name)
        print("java =", java)
        print("dotmc =", dotmc)
        print("memory =", memory)
        config.write(playername=name, java=java,dotmc=dotmc, ram=memory)

    def reset():
        config.write()
        return 0


    def reset_verify():
        reset_v_ask = tk.messagebox.askyesno("配置文件重置","是否确认重置配置文件?这将丢失所有信息.",icon=tk.messagebox.WARNING)
        if reset_v_ask:
            reset_ret = reset()
            if reset_ret == 0:
                tk.messagebox.showinfo("配置文件重置", "重置完毕")
        else:
            tk.messagebox.showinfo("配置文件重置", "已取消重置")
            
            
    def choosefile():
        jpath = tk.filedialog.askopenfilenames(filetypes=[('java/javaw程序', '.exe')])
        if jpath:
            java_entry.delete(0, "end")
            java_entry.insert(0, '"' + jpath[0] + '"')

    def choosefolder():
        dpath = tk.filedialog.askdirectory()
        if dpath:
            dotmc_entry.delete(0, "end")
            dotmc_entry.insert(0, dpath)

    window = tk.Tk()
    window.geometry("640x360")
    window.title("SMCL Lite")
    window.resizable(0, 0)

    infos = config.read()

    # java路径模块
    tk.Label(window, text="java路径").place(x=0, y=5)
    java_entry = tk.Entry(window, show=None)
    java_entry.place(x=90, y=5, width=400)
    java_entry.insert(0, infos["java"])
    btn_choosejava = tk.Button(window, command=choosefile, text="View...")
    btn_choosejava.place(x=475, y=0)

    # minecraft路径模块
    tk.Label(window, text=".minecraft路径").place(x=0, y=30)
    dotmc_entry = tk.Entry(window, show=None)
    dotmc_entry.place(x=90, y=30, width=400)
    dotmc_entry.insert(0, infos[".mc"])
    btn_choosejava = tk.Button(window, command=choosefolder, text="View...")
    btn_choosejava.place(x=475, y=25)

    # 玩家名模块
    tk.Label(window, text="玩家名").place(x=0, y=55)
    name_entry = tk.Entry(window, show=None)
    name_entry.place(x=90, y=55, width=200)
    name_entry.insert(0, infos["playername"])

    # 内存分配模块
    tk.Label(window, text="内存分配").place(x=0, y=80)
    memory_entry = tk.Entry(window, show=None)
    memory_entry.place(x=90, y=80)
    memory_entry.insert(0, infos["ram"])

    # 高级设置(LJS80)兼容性设置
    if advanced_settings_bit:
        b_advanced_settings = tk.Button(window, text="高级设置", command=advanced_settings)
        b_advanced_settings.place(x=350, y=300, width=50)

    btn_ok = tk.Button(window, text="完成", command=write)
    btn_rejson = tk.Button(window, text="重置", command=reset_verify)

    btn_ok.place(x=250, y=300, width=50)
    btn_rejson.place(x=300, y=300, width=50)

    window.mainloop()
