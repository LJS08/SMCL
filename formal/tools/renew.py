import os

basic_dir='./.minecraft'
tasks=["","/assets","/config","/libraries","/logs","/resourcepacks","/saves","/screenshots","/versions"] # 要创建文件夹的列表
def renew(dir):
    global basic_dir
    if(os.path.exists(basic_dir+dir)==False):
        os.makedirs(basic_dir+dir)
count=0
length = len(tasks)-1
while True:
    renew(tasks[count])
    if(count==length):
        break
    count=count+1;
print("ok")