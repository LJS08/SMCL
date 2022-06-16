# coding:utf-8
# Hello, world!
import tkinter as tk
import os
window = tk.Tk()
window.title('SMCL')  # 更改标题名字
window.geometry('854x480') #窗口大小
window.iconphoto(False, tk.PhotoImage(file='stoneicon.png'))
maintitle=tk.Label(text="SMCL 启动器 dev .1",fg="black",font=('Bahnschrift', 16,)).place(x=0,y=0) #画出主标题
version=tk.Label(text="Dev .1",fg="black",font=('Bahnschrift', 9,)).place(x=0,y=460) #画版本

window.mainloop() #循环绘画
if(os.path.exists('./.smcl')==False):
    os.makedirs('./.smcl')     #创建游戏目录
