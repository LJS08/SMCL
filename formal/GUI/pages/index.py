# coding:utf-8
# 主页
import tkinter as tk
from webbrowser import open
from PIL import Image, ImageTk

def index(root: tk.Tk):
    def open_community():
        open("https://kook.top/9ccRg6")

    def download_page():
        return 0 #Nothing now#

    def launch():
        return 0 #Nothing now#

    pixel = tk.PhotoImage(width=1, height=1)
    root.iconphoto(False, tk.PhotoImage(file='./image/icon.png'))
    # 背景
    image = ImageTk.PhotoImage(Image.open("./image/bg.png"))
    bg = tk.Label(root, image=image)
    # 标题区域
    titles_Frame = tk.Frame(root, width=800, height=60, bg="#FFFFFF")
    title = tk.Label(titles_Frame, text="SMCL", bg="#FFFFFF", font=("Bahnschrift", 30,))
    # 官方论坛按钮
    community_Button = tk.Button(root, text="官方论坛", image=pixel, bg="#A2C7E8",
                                 activebackground="#CADFF2",
                                 width=120, height=57., bd=0,
                                 font=("simhei", 14,), command=open_community, compound="c")

    download_page_Button = tk.Button(root, text="下载游戏", image=pixel, bg="#A2C7E8",
                                     activebackground="#CADFF2",
                                     width=120, height=57., bd=0,
                                     font=("simhei", 14,), command=download_page, compound="c")

    launch_Button = tk.Button(root, text="启动游戏", image=pixel, bg="#A2C7E8",
                                     activebackground="#CADFF2",
                                     width=150, height=57., bd=0,
                                     font=("simhei", 14,), command=launch, compound="c")

    # 渲染背景
    bg.pack()
    # 渲染标题区域
    titles_Frame.place(x=0, y=0)
    title.place(x=10, y=5)
    # 渲染官方论坛按钮
    community_Button.place(x=680, y=0)
    # 渲染下载页面跳转按钮
    download_page_Button.place(x=0, y=60)
    # 渲染启动按钮
    launch_Button.place(x=650, y=390)
    root.mainloop()
    return "okay."
