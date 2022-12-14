import View.main
from Core.mkdir import *
from loguru import logger
import Core.config

logger.add('log/smcl_{time}.log', rotation="50 MB", compression='zip', encoding='utf-8')

if __name__ == "__main__":
    f = Files()
    f.make_mc_dir(".")
    game_dir = os.getcwd()
    game_dir = os.path.join(game_dir, ".minecraft")
    Core.config.write(dotmc = game_dir)
    View.main.main_page(os.path.dirname(__file__))
    
