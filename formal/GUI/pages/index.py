# coding:utf-8
# 主页
import tkinter as tk


def index(root: tk.Tk):
    root.iconphoto(False, tk.PhotoImage(file='./image/icon.png'))
    # 画出主标题
    main_title = tk.Label(root, text="SMCL 启动器 dev .1", fg="black", font=('Bahnschrift', 16,))
    main_title.place(x=0, y=0)
    # 画出版本号
    version = tk.Label(root, text="Dev .1", fg="black", font=('Bahnschrift', 9,))
    version.place(x=0, y=460)
    root.mainloop()
    return "okay."
