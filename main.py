import pygame as pg
from pygame.locals import *
import numpy as np
import math
import copy
import sys, os, time

# DB
import json

# ゲーム用モジュール
from config import GameManager, Animation, Camera
import UISystem as UI

# アプリケーションコンフィグ
import configparser

# 高速化
from concurrent.futures import ThreadPoolExecutor, Future


class MapTile(pg.sprite.Sprite):
    def __init__(self, cam, rect, image):
        pg.sprite.Sprite.__init__(self)
        self.cam: Camera = cam
        self.transform: pg.Rect = rect      #位置演算用
        self.rect: pg.Rect = copy.deepcopy(rect)           #描画位置用
        self.angle = 0

        self.image = image

        self.gm = GameManager()
        self.isizeW, self.isizeH = image.get_size()
        
        self.screen_center = (self.gm.screen.get_width()/2, self.gm.screen.get_height()/2)
        
    def draw(self, surface):
        self.rect.x = (self.transform.x - self.isizeW/2 - self.cam.x) + self.screen_center[0]
        self.rect.y = (self.transform.y - self.isizeH/2 - self.cam.y) + self.screen_center[1]
        if self.rect.x > -self.isizeW and self.rect.x < self.screen_center[0]*2 and self.rect.y > -self.isizeH and self.rect.y < self.screen_center[1]*2:
            surface.blit(self.image, self.rect)
        # if self.rect.x > 100 and self.rect.x < self.screen_center[0]*2-100 and self.rect.y > 100 and self.rect.y < self.screen_center[1]*2-100:
        #     surface.blit(self.image, self.rect)

""" ゲームループ """
def main():
    config = configparser.ConfigParser()

    dir_path = os.path.join(__file__)
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    config.read(os.path.join(base_path, "./configs/settings.ini"), encoding="utf-8")

    pg.init()
    screen = pg.display.set_mode((config["WINDOW"].getint("WIDTH"), config["WINDOW"].getint("HEIGHT")))
    pg.display.set_caption(config["WINDOW"].get("CAPTION"))

    gm = GameManager()
    gm.base_path = base_path
    gm.screen = screen

    gm.scenes = []
    # gm.scene = 1
    # gm.LoadScene()
    
    fps = config["WINDOW"].getint("FPS")

    clock = pg.time.Clock()

    while True:
        st = time.perf_counter() #pg.time.get_ticks()

        screen.fill(gm.fillColor)

        # gm.sceneObj.update()
        # gm.sceneObj.draw()
        
        pg.display.flip()
        
        #イベント処理
        for event in pg.event.get():
            if event.type == QUIT:
                del gm
                pg.quit()
                sys.exit()

        clock.tick(fps)

        et = time.perf_counter() #pg.time.get_ticks()
        delta = et - st
        # print(1 / (delta / 1000))
        gm.deltaTime = delta

if __name__ == "__main__":
    main()