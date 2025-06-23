import pymunk
import pymunk.pygame_util
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
    fillColor = (0, 0, 0)
    scene = None

    gravity = (0, 980)
    space: pymunk.Space = None

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

    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)

class BoxPhysics(BaseCPN):
    def __init__(self, static, mass, moi, e, w, h):
        super().__init__()
        self.transform: Transform = None
        self.body: pymunk.Body = None
        self.static: bool = static
        self.mass: float = mass
        self.moi: float = moi
        self.elasticity: float = e
        self.rect = (w, h)

    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)
        
        if self.static:
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            self.body = pymunk.Body(self.mass, float("inf"))
        
        self.body.position = (self.transform.x, self.transform.y)
        print(self.gameobject.name)
        print(self.transform.x, self.transform.y)
        self.body_shape = pymunk.Poly.create_box(self.body, self.rect)
        self.body_shape.elasticity = self.elasticity
        GameManager().space.add(self.body, self.body_shape)
        print(self.transform.x, self.transform.y)

    def Update(self):
        self.pos = self.body.position
        self.transform.x = self.pos[0]
        self.transform.y = self.pos[1]

class Sprite(BaseCPN):
    def __init__(self, img):
        super().__init__()
        self.img = pg.image.load(os.path.join(GameManager().base_path, img))
        self.transform: Transform = None
        self.cam: Transform = None
        self.gm = GameManager()
        self.screen_center = (self.gm.screen.get_width()/2, self.gm.screen.get_height()/2)

    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)
        self.cam = GameManager().scene.GetObjectRequest(id=0).GetComponent(Transform)

    def Update(self):
        rx = (self.transform.x - self.transform.w/2 - self.cam.x) + self.screen_center[0]
        ry = (self.transform.y - self.transform.h/2 - self.cam.y) + self.screen_center[1]
        GameManager().screen.blit(self.img, pg.rect.Rect(rx, ry, self.transform.w, self.transform.h))

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

class Scene:
    def __init__(self):
        self.gameObjects = []

    def update(self) -> None:
        for obj in self.gameObjects: 
            obj.Update()

    def GetObjectRequest(self, id) -> GameObject:
        """
        シーンオブジェクトにオブジェクト情報のGetリクエストをする
        """
        for obj in self.gameObjects:
            if obj.id == id:
                return obj
        raise ValueError(f"There is not Object {id} in scene {self} !")

    def OnLoad(self):
        for obj in self.gameObjects:
            obj.OnLoad(self)

    def Start(self):
        for obj in self.gameObjects: 
            obj.Start()

    def draw(self):
        for obj in self.gameObjects: 
            obj.draw()

class SceneLoader:
    instance = None

    Scenes = {}

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(SceneLoader, cls).__new__(cls)
            print("Create new instance, SceneLoader")
        return cls.instance

    def load_scene(self, name) -> Scene:
        f = open(os.path.join(GameManager().base_path, f"./Scenes/{self.Scenes[name]}"), "r")
        sc = json.load(f)
        objects = []
        for key, value in sc.items():
            obj = GameObject()
            obj.name = key
            obj.tag = value["tag"]
            obj.layer = value["layer"]
            obj.id = value["id"]
            
            for v in value["components"].values():
                cmp = self.object_hook(v["_type"], v["value"])
                obj.components.append(cmp)
            objects.append(obj)
        
        scene = Scene()
        scene.gameObjects = objects

        print(f"Now scene is {name}")

        return scene

    def object_hook(self, cls: str, values: dict) -> any:
        if cls == "Transform":
            t = Transform()
            t.x = values["x"]
            t.y = values["y"]
            t.w = values["width"]
            t.h = values["height"]
            return t
        elif cls == "Camera":
            return Camera()
        elif cls == "Sprite":
            return Sprite("./Images/Squere.png")
        elif cls == "BoxPhysics":
            return BoxPhysics(values["static"], values["mass"], values["MoI"], values["e"], values["w"], values["h"])

    def register(self) -> None:
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
    GameManager().scene = SceneLoader().load_scene("SampleScene")