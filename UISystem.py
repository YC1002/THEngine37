import pygame as pg
from pygame.locals import *
import numpy as np
import os

from config import GameManager, BaseCPN, Transform


class Slider(BaseCPN):
    def __init__(self, min, max, value):
        """_summary_
        これは現段階で試験的な機能です
        Slider:
            min (float): 最大値
            max (float): 最小値
            value (float): 現在の値
        """
        super().__init__()
        
        self.fill_color = (255, 255, 255)
        self.background_color = (10, 10, 10)

        self.min = min
        self.max = max
        self.value = value
        self.transform: Transform = None

        self.raito = self.value / self.max
        
        self.gm: GameManager = GameManager()

    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)

    def Update(self):
        self.raito = self.value / self.max

        if self.raito < 0.0:
            self.raito = 0.0
        self.gm.screen.fill(self.background_color, (self.transform.x+self.transform.w*self.raito, self.transform.y, self.transform.w-self.transform.w*self.raito, self.transform.h))
        self.gm.screen.fill(self.fill_color, (self.transform.x, self.transform.y, self.transform.w*self.raito, self.transform.h))

class UIImage(BaseCPN):
    def __init__(self, image, r, g, b, a):
        super().__init__()
        
        self.src = image
        self.NoneImage = (image == "")
        self.img: pg.surface.Surface = None
        self.transform: Transform = None

        self.color = (r, g, b, a)
        
        self.gm = GameManager()
            
    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)
        
        if not self.NoneImage:
            self.img = pg.image.load(os.path.join(GameManager().base_path, self.src)).convert_alpha()
            self.img = pg.transform.scale(self.img, (self.transform.w, self.transform.h))
            # self.pixel = pg.PixelArray(self.img)
        else:
            self.img = pg.Surface((self.transform.w, self.transform.h)).convert_alpha()

    def Update(self):
        if self.NoneImage:
            self.img.fill(self.color)
            self.img_ = pg.transform.rotate(self.img, self.transform.rotate)
            self.img_.set_alpha(self.color[3])

            isizeW, isizeH = self.img_.get_size()
            newrx = self.transform.x - isizeW/2
            newry = self.transform.y - isizeH/2
            newRect = pg.Rect(newrx, newry, self.transform.w, self.transform.h)

            self.gm.screen.blit(self.img_, newRect)
        else:
            self.img.set_alpha(self.color[3])
            self.gm.screen.blit(self.img, (self.transform.x, self.transform.y, self.transform.w, self.transform.h))

class UIText(BaseCPN):
    def __init__(self, text, size, r, g, b):
        super().__init__()
        self.font = pg.font.Font("./font/DotGothic16-Regular.ttf", size)
        self.text = text
        self.transform: Transform = None
        self.color = (r, g, b)
        self.text_obj = self.font.render(self.text, True, self.color)
        
        self.gm = GameManager()

    def Start(self):
        self.transform = self.gameobject.GetComponent(Transform)

    def Update(self):
        self.text_obj = self.font.render(self.text, True, self.color)
        self.draw(self.gm.screen)
    
    def draw(self, surface: pg.surface.Surface):
        surface.blit(self.text_obj, (self.transform.x-self.text_obj.get_size()[0]/2, self.transform.y-self.text_obj.get_size()[1]/2))

class UIButtonClassic(pg.sprite.Sprite):
    """使用を禁止します"""
    def __init__(self, text, rect:pg.rect.Rect, text_pos, font_size, event):
        pg.sprite.Sprite.__init__(self)
        self.rect = rect
        self.text = text
        self.pos = text_pos
        self.font_size = font_size

        self.buttons_image = pg.image.load("./Images/UI/Buttons.png").convert_alpha()
        self.Image = UIImage(self.buttons_image, self.rect)
        self.Image.color[3] = 255
        self.text_obj = UIText(text, (2*self.rect.x+self.rect.width)*self.pos[0], (2*self.rect.y+self.rect.height/3)*self.pos[1], self.font_size)
        self.text_obj.color = (0, 0, 0)
        
        self.flag = False
        self.button_index = 0
        self.on_anim = False
        
        self.event = event

    def update(self):
        if self.StayOncollide() and pg.mouse.get_pressed()[0]:      # ボタンが押されているとき
            self.button_index = 2
            self.on_anim = True
        elif self.on_anim and not pg.mouse.get_pressed()[0]:        # ボタンが離されたとき
            self.event()
            self.button_index = 0
            self.flag = 3
            self.on_anim = False
        
        if not self.on_anim:
            col, f = self.On_collide()      # マウスがボタンに触れた/離れた時
            if col:
                self.button_index = f
            
        self.Image.update()
        self.text_obj.update()
        
    def StayOncollide(self):
        self.mousepos = pg.mouse.get_pos()
        return self.mousepos[0] > self.rect.x and self.mousepos[0] < self.rect.x+self.rect.width and self.mousepos[1] > self.rect.y and self.mousepos[1] < self.rect.y + self.rect.height/3
        
    def On_collide(self):
        self.mousepos = pg.mouse.get_pos()
        c = self.StayOncollide()
        if c != self.flag:
            self.flag = c
            if c:
                return True, 1
            else:
                return True, 0
        else:
            return False, -1
    
    def draw(self, surface: pg.surface.Surface):
        self.Image.draw_clip(surface, pg.Rect(0, 65*self.button_index, 216, 65))
        self.text_obj.draw(surface)

class UIButtonCustom(pg.sprite.Sprite):
    """使用を禁止します。"""
    def __init__(self, bi, text, rect:pg.rect.Rect, one_height, text_pos, font_size, event):
        pg.sprite.Sprite.__init__(self)
        self.rect = rect
        self.text = text
        self.pos = text_pos
        self.font_size = font_size
        self.oheight = one_height

        self.buttons_image = bi
        self.Image = UIImage(self.buttons_image, self.rect)
        self.Image.aplha = 255
        self.text_obj = UIText(text, (2*self.rect.x+self.rect.width)*self.pos[0], (2*self.rect.y+self.rect.height/3)*self.pos[1], self.font_size)
        self.text_obj.color = (0, 0, 0)
        
        self.flag = False
        self.button_index = 0
        self.on_anim = False
        
        self.event = event
        self.button_collide = None
        self.button_ncollide = None

        self.t = 0
        self.ls = False

    def Move_To(self, From: list[float], To: list[float], seconds: float =1.0):
        if self.t < 1:
            self.t += (GameManager().deltaTime / seconds)
            i = Transform.LinearComplection(From, To, self.t)
            self.rect.x = i[0]
            self.rect.y = i[1]

    def update(self):
        if self.StayOncollide() and pg.mouse.get_pressed()[0]:      # ボタンが押されているとき
            self.button_index = 1
            self.on_anim = True
        elif self.on_anim and not pg.mouse.get_pressed()[0]:        # ボタンが離されたとき
            self.event()
            self.button_index = 0
            self.flag = 3
            self.on_anim = False
        
        if not self.on_anim:
            col, f = self.On_collide()      # マウスがボタンに触れた/離れた時
            if col:
                self.button_index = f

        if self.StayOncollide():
            if self.ls:
                self.t = 0
                self.ls = False

            self.button_collide()
        else:
            if not self.ls:
                self.t = 0
                self.ls = True
                
            self.button_ncollide()
            
        self.Image.rect.x = self.rect.x
        self.Image.rect.y = self.rect.y
        self.text_obj.pos = ((2*self.rect.x+self.rect.width)*self.pos[0], (2*self.rect.y+self.rect.height/3)*self.pos[1])

        self.Image.update()
        self.text_obj.update()
        
    def StayOncollide(self):
        self.mousepos = pg.mouse.get_pos()
        return self.mousepos[0] > self.rect.x and self.mousepos[0] < self.rect.x+self.rect.width and self.mousepos[1] > self.rect.y and self.mousepos[1] < self.rect.y + self.rect.height/2
        
    def On_collide(self):
        self.mousepos = pg.mouse.get_pos()
        c = self.StayOncollide()
        if c != self.flag:
            self.flag = c
            if c:
                return True, 1
            else:
                return True, 0
        else:
            return False, -1
    
    def draw(self, surface: pg.surface.Surface):
        self.Image.draw_clip(surface, pg.Rect(0, self.oheight*self.button_index, self.rect.width, self.oheight))
        self.text_obj.draw(surface)