# coding:utf-8
# Hello, world!
import tkinter as tk
import os
smcl_version="Dev .1"

window = tk.Tk()
window.title('SMCL Launcher')  # 更改标题名字
window.geometry('854x480') #窗口大小
window.iconphoto(False, tk.PhotoImage(file='stoneicon.png'))#使用icon
maintitle=tk.Label(text="SMCL "+smcl_version,fg="black",font=('Bahnschrift', 16,)).place(x=0,y=0) #画出主标题
version=tk.Label(text=smcl_version,fg="black",font=('Bahnschrift', 9,)).place(x=0,y=460) #画版本
photo = tk.PhotoImage(file="background.png")#设置背景图片
theLabel = tk.Label(image=photo,compound = tk.CENTER,fg = "white")#设置背景图片
theLabel.pack()
window.mainloop() #循环绘画
if(os.path.exists('./.smcl')==False):
    os.makedirs('./.smcl')     #创建游戏目录