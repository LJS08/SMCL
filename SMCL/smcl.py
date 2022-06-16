# coding:utf-8
# Hello, world!
import tkinter as tk
import os
window = tk.Tk()
window.title('SMCL')  # 更改标题名字
window.geometry('960x540')  
window.iconphoto(False, tk.PhotoImage(file='stone.png'))
window.mainloop()
if(os.path.exists('./.smcl')==False):
    os.makedirs('./.smcl')     #创建游戏目录
