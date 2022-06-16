import os
basic='./.minecraft'
tasks=["","/assets","/config","/libraries","/logs","/resourcepacks","/saves","/screenshots","/versions"]
def renew(dir):
    global basic
    if(os.path.exists(basic+dir)==False):
        os.makedirs(basic+dir)
count=0
length = len(tasks)-1
while True:
    renew(tasks[count])
    if(count==length):
        break
    count=count+1;
print("ok")