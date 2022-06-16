# coding:utf-8
# 主页
import tkinter as tk
from webbrowser import open
from PIL import Image, ImageTk


def index(root: tk.Tk):
    def open_community():
        open("https://kaihei.co/JsoIvP")

    pixel = tk.PhotoImage(width=1, height=1)
    root.iconphoto(False, tk.PhotoImage(file='./image/icon.png'))
    # 背景
    image = ImageTk.PhotoImage(Image.open("./image/bg.png"))
    bg = tk.Label(root, image=image)
    # 标题区域
    titles_Frame = tk.Frame(root, width=640, height=100, bg="#00AFF0")
    title = tk.Label(titles_Frame, text="SMCL", bg="#00AFF0", font=("Bahnschrift", 30,))
    version = tk.Label(titles_Frame, text="Dev 0.2", bg="#00AFF0", font=("Bahnschrift", 15,))
    # 官方论坛按钮
    community_Button = tk.Button(root, text="Community\n----\n官方论坛", image=pixel, bg="#A2C7E8",
                                 activebackground="#CADFF2",
                                 width=160, height=96, bd=0,
                                 font=("simhei", 12,), command=open_community, compound="c")
    # 渲染背景
    bg.pack()
    # 渲染标题区域
    titles_Frame.place(x=0, y=0)
    title.place(x=20, y=10)
    version.place(x=20, y=55)
    # 渲染官方论坛按钮
    community_Button.place(x=640, y=0)

    root.mainloop()
    return "okay."
