import Core.core_start as core
import Core.config as config
import tkinter as tk
import requests


def download_page():
    def download():
        dotmc = config.read()[".mc"]
        core.core_bootstrap_main(True, dotmc, versions.get(versions.curselection()), "BMCLAPI")
        print("Ok")

    window = tk.Tk()
    window.geometry("640x360")
    window.title("SMCL Lite")
    window.resizable(0, 0)

    versions = tk.Listbox(window, selectmode=tk.SINGLE)
    btn_ok = tk.Button(window, text="下载", command=download)

    for i in requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()["versions"]:
        versions.insert("end", i['id'])

    versions.place(x=0, y=0, height=360)
    btn_ok.place(x=185, y=200)

    window.mainloop()
