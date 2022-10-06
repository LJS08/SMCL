import Core.config
import View.download as download
import View.set as set
import tkinter as tk
import tkinter.messagebox
import time
import Core.core_start as core
import os
from tkinter import ttk


def main_page():
    def launch():
        start_time = time.time()
        print("We are launching for you!")
        # core.core_bootstrap_main(True, basic_info[1], version.get(), "BMCLAPI")
        config = Core.config.read()
        core.core_start_IN(config["playername"], config[".mc"], version.get(), config["java"], "0", "0", "Lite", False
                           , "20", "20", "128M", config["ram"])
        success_time = time.time()
        print("Launch success in " + str(success_time - start_time) + "seconds")

    def copyr():
        tk.messagebox.showinfo("SMCL", "SMCL Beta1.0.2 created by LJS80 and Sharll.\nCopyright SMDC Develop Bar 2022.")

    # init
    window = tk.Tk()
    bgimage1 = tk.PhotoImage(file=r"img/backdrop.png")
    bg = tk.Label(window, image=bgimage1)
    window.iconphoto(False, tk.PhotoImage(file=r"img/icon.png"))
    window.geometry("640x360")
    window.title("SMCL Lite")
    window.resizable(0, 0)
    # title
    titles_Frame = tk.Frame(window, width=640, height=60, bg="#FFFFFF")
    title = tk.Button(window, text="SMCL", bg="#FFFFFF", font=("Bahnschrift", 22), command=copyr, bd=0)
    # copyr = tk.Label(window, text="SMCL Beta1.0.0 created by LJS80 and Sharll. Copyright SMDC Develop Bar 2022.")

    # window.overrideredirect(True)
    # buttons
    img1 = tk.PhotoImage(file=r"img/launch.png")
    btn_launch = tk.Button(window, text="Launch", image=img1, bg="#FFFFFF",
                           activebackground="#CADFF2", bd=0, height=56, width=120,
                           font=("simhei", 16), command=launch, compound="top")

    img2 = tk.PhotoImage(file=r"img/Download.png")
    btn_download = tk.Button(window, text="Download", image=img2, bg="#FFFFFF",
                             activebackground="#CADFF2", bd=0, height=56, width=120,
                             font=("simhei", 14,), command=download.download_page, compound="top")

    img3 = tk.PhotoImage(file=r"img/Settings.png")
    btn_setting = tk.Button(window, text="Settings", image=img3, bg="#FFFFFF",
                            activebackground="#CADFF2", bd=0, height=56, width=120,
                            font=("simhei", 14,), command=set.setting_page, compound="top")

    version = ttk.Combobox(window)
    config = Core.config.read()
    try:
        version["values"] = os.listdir(config[".mc"] + "\\versions")
        version.insert(0, os.listdir(config[".mc"] + "\\versions")[0])
    except:
        version.insert(0, "No game found. Download one and restart the launcher.")


    # backdrop
    bg.pack()
    # title
    titles_Frame.place(x=0, y=0)
    title.place(x=520, y=0)
    # copyr.place(x=0, y=340)
    # buttons
    btn_launch.place(x=0, y=0)
    btn_download.place(x=130, y=0)
    btn_setting.place(x=260, y=0)
    version.place(x=0, y=60, width=120)
    # run
    window.mainloop()
