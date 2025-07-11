import json
import os, sys

from config import *
from UISystem import *

class SceneLoader:
    instance = None

    Scenes = {}

    #this is the singleton-type class
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(SceneLoader, cls).__new__(cls)
            print("Create new instance, SceneLoader")
        return cls.instance

    # Load the scene
    def load_scene(self, name) -> Scene:
        f = open(os.path.join(GameManager().base_path, f"./Scenes/{self.Scenes[name]}"), "r")
        sc = json.load(f)
        objects = []
        hbs = []
        for key, value in sc.items():
            obj = GameObject()
            obj.name = key
            obj.tag = value["tag"]
            obj.layer = value["layer"]
            obj.id = value["id"]
            
            for v in value["components"].values():
                cmp = self.object_hook(v["_type"], v["value"])
                obj.components.append(cmp)
                if type(cmp) == HitBox: hbs.append(obj)
            objects.append(obj)
        
        scene = Scene()
        scene.gameObjects = objects
        scene.hitboxes = hbs

        print(f"This scene is {name}")

        return scene

    # resitering components <--- edit here when you add your custom components !
    def object_hook(self, cls: str, values: dict) -> any:
        if cls == "Transform":
            t = Transform()
            t.x = values["x"]
            t.y = values["y"]
            t.w = values["width"]
            t.h = values["height"]
            t.rotate = values["rotate"]
            return t
        elif cls == "Camera":
            return Camera()
        elif cls == "Sprite":
            return Sprite("./Images/Squere.png")
        elif cls == "HitBox":
            return HitBox(values["w"], values["h"])
        elif cls == "Tester":
            return Tester()
        elif cls == "Image":
            return UIImage(values["src"], values["r"], values["g"], values["b"], values["a"])
        elif cls == "Slider":
            return Slider(values["min"], values["max"], values["value"])
        elif cls == "Text":
            return UIText(values["text"], values["size"], values["r"], values["g"], values["b"])

    # registering the scene
    def register(self) -> None:
        dir_path = os.path.join(GameManager().base_path, "./Scenes")
        files_file = [
            f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))
        ]
        files_name = [
            f.replace(".json", "") for f in files_file 
        ]

        self.Scenes.update(zip(files_name, files_file))