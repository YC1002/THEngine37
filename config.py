import pygame as pg
import numpy as np
import math

import json
import os, sys

class GameManager:
    instance = None

    deltaTime: float = 0.0
    base_path = None
    screen = None
    scene = 2
    scenes = []
    sceneObj = None
    score = 0
    fillColor = (0, 0, 0)

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(GameManager, cls).__new__(cls)
            print("Create new instance, GameManager")
        return cls.instance

    def MoveScene(self, n):
        self.scene = n

    def LoadScene(self):        # シーンオブジェクトを読み込む
        self.sceneObj = self.scenes[self.scene]
        self.sceneObj.Load()

class Transform:
    def __init__(self, pos_x=0, pos_y=0, rotate=0, sclX=1, sclY=1):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rotate = rotate
        self.sclX = sclX
        self.sclY = sclY

    def LinearInterpolation(a: np.ndarray[float, float], b: np.ndarray[float, float], t: float):
        """
        aからbへ線形補間を行う
        t: 補完を行う割合
        """
        if t > 1:
            t = 1
        elif t < 0:
            t = 0
        return a + (b - a)*t
    
    def cross2d(self, v, w):
        return v[0]*w[1] - v[1]*w[0]
    
    def check_intersection(self, p1, p2, q1, q2):
        """
        線分 p1→p2 と q1→q2 の交差判定と交点算出
        :param p1: ベクトル1の始点
        :param p2: ベクトル1の終点
        :param q1: ベクトル2の始点
        :param q2: ベクトル2の終点
        :return: (bool:交差するか, np.array:交点座標 or None)
        """
        r = p2 - p1
        s = q2 - q1
        r_cross_s = self.cross2d(r, s)
        q_minus_p = q1 - p1
        qmp_cross_r = self.cross2d(q_minus_p, r)

        if r_cross_s == 0:
            # 平行（同一直線上 or 非交差
            return False, None

        t = self.cross2d(q_minus_p, s) / r_cross_s
        u = self.cross2d(q_minus_p, r) / r_cross_s

        if 0 <= t <= 1 and 0 <= u <= 1:
            intersection_point = p1 + t * r
            return True, intersection_point
        else:
            return False, None
    
    def SphereLinearComplection(Start: list[float, float], To: list[float, float], t: float):
        """
        aからbへ球面上線形補完を行う
        t: 補完を行う割合
        """
        p = np.array([To[0] - Start[0], To[1] - Start[1]])

        s = np.array([Start[0], Start[1]])
        e = np.array([To[0], To[1]])

        s_ = s / np.linalg.norm(s)
        e_ = e / np.linalg.norm(e)
        
        angle = math.acos(np.dot(s_, e_))
        sinTh = math.sin(angle)

        ps = math.sin(angle * (1 - t))
        pe = math.sin(angle * t)

        i = (ps * s + pe * e) / sinTh

        return i
    
    def LinearComplection(Start: list[float, float], To: list[float, float], t: float):
        s = np.array([Start[0], Start[1]])
        e = np.array([To[0], To[1]])

        i = s + (e - s) * t

        return i

        
class Animation:
    def __init__(self, srcs: list, scale: tuple, animation_interval: float):
        self.srcs = srcs
        self.imgs = []
        self.scale = scale
        
        self.gm = GameManager()
        
        self.time = 0.0
        self.anim_interval = animation_interval
        
        self.state = False
        
        self.index: int = 0
        
    def load_all(self):
        for src in self.srcs:
            self.imgs.append(pg.transform.scale(pg.image.load(src).convert_alpha(), (self.scale[0], self.scale[1])))
            
    def reset(self):
        self.time = 0.0
        self.index = 0
            
    def animate(self):
        self.time += self.gm.deltaTime
        if self.time > self.anim_interval:
            if self.index < len(self.imgs) - 1:
                self.index += 1
                self.time = 0.0
                self.state = False
            else:
                self.time = 0.0
                self.index = 0
                self.state = True
                
    def get_image(self):
        return self.imgs[self.index]
    
class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SceneLoader:
    instance = None

    Scenes = {}

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(SceneLoader, cls).__new__(cls)
            print("Create new instance, SceneLoader")
        return cls.instance

    def load_scene(self, name):
        pass

    def object_hook(self, o):
        pass

    def register(self):
        dir_path = os.path.join(GameManager().base_path, "./Scenes")
        files_file = [
            f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))
        ]
        files_name = [
            f.replace(".json", "") for f in files_file 
        ]

        self.Scenes.update(zip(files_name, files_file))

if __name__ == "__main__":
    dir_path = os.path.join(__file__)
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    GameManager().base_path = base_path
    SceneLoader().register()
    print(SceneLoader().Scenes)