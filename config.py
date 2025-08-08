
import pygame as pg
import numpy as np
import math

import json
import os, sys

class GameManager:
    instance = None

    deltaTime: float = 0.0
    base_path: str = None
    screen: pg.surface.Surface = None
    temporarySurface: pg.surface.Surface = None
    fillColor = (0, 0, 0)
    scene = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(GameManager, cls).__new__(cls)
            print("Create new instance, GameManager")
        return cls.instance

class BaseCPN:
    def __init__(self):
        self.active: bool = True
        self.gameobject: GameObject = None

    def OnLoad(self, GameObject):
        self.gameobject = GameObject

    def Start(self):
        pass    

    def Update(self):
        pass

class Transform(BaseCPN):
    def __init__(self):
        super().__init__()
        self.x: float = 0
        self.y: float = 0
        self.rotate: float = 0
        self.w: float = 0
        self.h: float = 0

    def LinearInterpolation(self, a: np.ndarray, b: np.ndarray, t: float):
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
    
    def SphereLinearComplection(self, Start: list[float, float], To: list[float, float], t: float):
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
    
    def LinearComplection(self, Start: list[float, float], To: list[float, float], t: float):
        s = np.array([Start[0], Start[1]])
        e = np.array([To[0], To[1]])

        i = s + (e - s) * t

        return i

class Animation(BaseCPN):
    def __init__(self, srcs: list, scale: tuple, animation_interval: float):
        super().__init__()

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
    
class Camera(BaseCPN):
    def __init__(self):
        super().__init__()
        self.transform: Transform = None
        self.gm = GameManager()

    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)

class HitBox(BaseCPN):
    def __init__(self, w, h):
        super().__init__()
        self.transform: Transform = None
        self.rect: pg.Rect = None
        self.w = w
        self.h = h

    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)
        self.rect = pg.Rect(self.transform.x, self.transform.y, self.w, self.h)

    def Update(self):
        self.rect = pg.Rect(self.transform.x, self.transform.y, self.w, self.h)
        
    def isCollide(self, box) -> bool:
        """
        与えられたbox(HitBox型)と衝突しているかを判定する
        """
        return self.rect.colliderect(box.rect)

    def isCollideVector(self, box, vx, vy) -> bool:
        """
        与えられたbox(HitBox型)と自身の(vx, vy)進行後が衝突しているかを判定する
        """
        nr = pg.Rect(self.rect.x + vx, self.rect.y + vy, self.rect.w, self.rect.h)
        return nr.colliderect(box)

class Sprite(BaseCPN):
    def __init__(self, img_s):
        super().__init__()
        self.src =img_s
        self.img = None
        self.rimg = None
        self.transform: Transform = None
        self.cam: Transform = None
        self.gm = GameManager()
        self.screen_center = (self.gm.temporarySurface.get_width()/2, self.gm.temporarySurface.get_height()/2)
        
    def OnLoad(self, GameObject):
        super().OnLoad(GameObject)
        if self.img == None:
            self.img = pg.image.load(os.path.join(GameManager().base_path, self.src)).convert_alpha()

    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)
        self.cam = GameManager().scene.GetObjectRequest(id=0).GetComponent(Transform)

    def Update(self):
        rx = (self.transform.x - self.transform.w/2 - self.cam.x) + self.screen_center[0]
        ry = (self.transform.y - self.transform.h/2 - self.cam.y) + self.screen_center[1]
        if (rx > -self.transform.w and rx < self.gm.temporarySurface.get_width()+self.transform.w) and (ry > -self.transform.h and ry < self.gm.temporarySurface.get_height()+self.transform.h):
            self.rimg = pg.transform.rotate(pg.transform.scale(self.img, (self.transform.w, self.transform.h)), self.transform.rotate)
            GameManager().temporarySurface.blit(self.img, (rx, ry, self.transform.w, self.transform.h))

class GameObject:
    def __init__(self) -> None:
        self.scene: Scene = None
        self.name: str = ""
        self.tag: str = ""
        self.layer: int = 0
        self.id: int = 0
        self.components: list = []

    def OnLoad(self, scene) -> None:
        self.scene = scene
        for c in self.components: c.OnLoad(self)

    def Start(self) -> None:
        for c in self.components:
            if c.active:
                c.Start()

    def Update(self) -> None:
        for c in self.components:
            if c.active:
                c.Update()

    def GetComponent(self, type_: type) -> any:
        for c in self.components:
            if type(c) == type_:
                return c
        raise ValueError(f"There is not Component {type_} in Object {self.id}")

class Tester(BaseCPN):
    def __init__(self):
        """
        need:
            BoxPhysics,
            Sprite
        """
        super().__init__()
        self.transform: Transform = None
        self.speed: float = 120
        
    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)
        
    def Update(self):
        key = pg.key.get_pressed()
        
        if key[pg.K_RIGHT]:
            self.transform.x += self.speed*GameManager().deltaTime
        if key[pg.K_LEFT]:
            self.transform.x -= self.speed*GameManager().deltaTime
        if key[pg.K_UP]:
            self.transform.y -= self.speed*GameManager().deltaTime
        if key[pg.K_DOWN]:
            self.transform.y += self.speed*GameManager().deltaTime
            
        #self.t.rotate += 10

class Scene:
    def __init__(self):
        self.__layer_idx = None
        self.__sorted_layer = None
        self.gameObjects = []
        self.hitboxes = []
        
    def Update_layer(self):
        self.__layer_idx = np.fromiter((obj.layer for obj in self.gameObjects), dtype=np.int32)
        self.__sorted_layer = np.argsort(self.__layer_idx)

    def update(self) -> None:
        for idx in self.__sorted_layer: 
            self.gameObjects[idx].Update()
            
    def RegisterToObjectList(self, obj):
        self.gameObjects.append(obj)
        for cmp in obj.components:
            if type(cmp) == HitBox:
                self.hitboxes.append(cmp)

    def GetObjectRequest(self, id) -> GameObject:
        """
        シーンオブジェクトにオブジェクト情報のGetリクエストをする
        """
        for obj in self.gameObjects:
            if obj.id == id:
                return obj
        raise ValueError(f"There is not Object {id} in scene {self} !")
    
    def GetObjectsWithTag(self, name) -> list[GameObject]:
        """
        nameに該当するすべてのシーンオブジェクトを取得する
        """
        l = []
        for obj in self.gameObjects:
            if obj.tag == name: l.append(obj)
        return l
    
    def GetMaxID(self) -> int:
        """
        現在のシーン内のゲームオブジェクトの最大のIDを取得する
        """
        objs = [obj.id for obj in self.gameObjects]
        return max(objs)

    def OnLoad(self):
        self.Update_layer()
        for obj in self.gameObjects:
            obj.OnLoad(self)

    def Start(self):
        for obj in self.gameObjects: 
            obj.Start()
            
    def free(self):
        del self.gameObjects, self.hitboxes
