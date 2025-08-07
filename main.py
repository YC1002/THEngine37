import pygame as pg
import sys, os

# ゲーム用モジュール
from config import GameManager
from SceneLoader import SceneLoader

# アプリケーションコンフィグ
import configparser


""" ゲームループ """
def main():
    config = configparser.ConfigParser()

    # パスの取得とコンフィグデータの取得
    #dir_path = os.path.join(__file__)
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    config.read(os.path.join(base_path, "./configs/settings.ini"), encoding="utf-8")

    pg.init()
    screen = pg.display.set_mode((config["WINDOW"].getint("WIDTH"), config["WINDOW"].getint("HEIGHT")))
    pg.display.set_icon(pg.image.load(os.path.join(base_path, "./Images/icon/THENGINE37_icon.png")))

    gm = GameManager()
    gm.base_path = base_path
    gm.screen = screen
    
    # テンポラリサーフェイスの設定
    gm.temporarySurface = pg.surface.Surface((config["GRAPHICS"].getint("REWIDTH"), config["GRAPHICS"].getint("REHEIGHT"))).convert_alpha()

    # シーンデータの読み取り
    sc = SceneLoader()
    sc.register()
    sc.load_scene(config["WINDOW"].get("SCENE"))
    
    fps = config["WINDOW"].getint("FPS")

    clock = pg.time.Clock()

    while True:
        screen.fill(gm.fillColor)
        gm.temporarySurface.fill(gm.fillColor)

        gm.scene.update()
        
        # テンポラリサーフェイスの解像度処理
        deformedSurface = pg.transform.scale(gm.temporarySurface, (gm.screen.get_width(), gm.screen.get_height()))
        screen.blit(deformedSurface, (0, 0))
        
        pg.display.flip()
        
        #イベント処理
        for event in pg.event.get():
            if event.type == pg.QUIT:
                del gm
                pg.quit()
                sys.exit()

        pg.display.set_caption(f"[FPS={clock.get_fps()}] {config["WINDOW"].get("CAPTION")}")
        gm.deltaTime = clock.tick(fps) / 1000

if __name__ == "__main__":
    main()
