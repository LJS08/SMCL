import Core.core_start as core
import Core.config as config
import tkinter as tk
import tkinter.messagebox
import requests
import threading


def download_page():
    def download():
        dotmc = config.read()[".mc"]
        thread = threading.Thread(target=core.core_bootstrap_main, args=(True, dotmc, versions.get(versions.curselection()), "BMCLAPI"))
        thread.start()
        tk.messagebox.showinfo("SMCL", "正在下载，这可能需要一段时间")
        # core.core_bootstrap_main(True, dotmc, versions.get(versions.curselection()), "BMCLAPI")
        print("Ok")
        # tk.messagebox.showinfo("SMCL", "下载完毕")

    window = tk.Tk()
    window.geometry("640x360")
    window.title("SMCL Lite")
    window.resizable(0, 0)

    versions = tk.Listbox(window, selectmode=tk.SINGLE)
    btn_ok = tk.Button(window, text="下载", command=download)

    for i in core.core_Get_Version_list("release", "BMCLAPI"):
        versions.insert("end", i['id'])

    versions.place(x=0, y=0, height=360)
    btn_ok.place(x=185, y=200)

    window.mainloop()
