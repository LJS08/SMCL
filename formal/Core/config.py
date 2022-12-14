import json
import os
config = os.path.abspath("config.json")


def read():
    return json.load(open(config, "r+"))


def write(playername: str = "player", dotmc: str = "None", java: str = "java", ram: str = "512M"):
    #debug print(os.getcwd())
    con = {"playername": playername, ".mc": dotmc, "java": java, "ram": ram}
    open(config, "w+").write(json.dumps(con))
    return 0
