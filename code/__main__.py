import View.main
from Core.mkdir import *
from loguru import logger

logger.add('log/smcl_{time}.log', rotation="50 MB", compression='zip', encoding='utf-8')

if __name__ == "__main__":
    f = Files()
    f.make_mc_dir(".")
    View.main.main_page()