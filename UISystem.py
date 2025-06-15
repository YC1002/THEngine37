import pygame as pg
from pygame.locals import *
import numpy as np
import math

from collections import deque
from config import GameManager, Transform


class Slider(pg.sprite.Sprite):
    def __init__(self, min, max, value, rect: pg.rect.Rect):
        pg.sprite.Sprite.__init__(self)
        
        self.fill_color = (255, 255, 255)
        self.background_color = (0, 0, 0)

        self.min = min
        self.max = max
        self.value = value
        self.rect = rect

        self.raito = self.value / self.max

    def update(self):
        self.raito = self.value / self.max

        if self.raito < 0.0:
            self.raito = 0.0

    def draw(self, surface: pg.surface.Surface):
        surface.fill(self.background_color, (self.rect.x+self.rect.w*self.raito, self.rect.y, self.rect.w-self.rect.w*self.raito, self.rect.height))
        surface.fill(self.fill_color, (self.rect.x, self.rect.y, self.rect.w*self.raito, self.rect.height))

class UIImage(pg.sprite.Sprite):
    def __init__(self, image: pg.surface.Surface, rect: pg.rect.Rect, angle=0, aplha: int = 0):
        pg.sprite.Sprite.__init__(self)
        self.NoneImage = (image == None)
        self.img: pg.surface.Surface = image
        self.rect: pg.rect.Rect = rect
        self.angle = angle

        self.aplha: int = aplha
        self.color = (255, 255, 255)

        if self.img is not None:
            self.img = pg.transform.scale(self.img, (self.rect.width, self.rect.height))
            # self.pixel = pg.PixelArray(self.img)
        else:
            self.img = pg.Surface((self.rect.width, self.rect.height)).convert_alpha()

    def update(self):
        pass

    def draw(self, surface: pg.surface.Surface):
        if self.NoneImage:
            self.img.fill(self.color)
            self.img_ = pg.transform.rotate(self.img, self.angle)
            self.img_.set_alpha(self.aplha)

            isizeW, isizeH = self.img_.get_size()
            newrx = self.rect.x - isizeW/2
            newry = self.rect.y - isizeH/2
            newRect = pg.Rect(newrx, newry, self.rect.width, self.rect.height)

            surface.blit(self.img_, newRect)
        else:
            self.img.set_alpha(self.aplha)
            surface.blit(self.img, self.rect)

    def draw_clip(self, surface: pg.surface.Surface, rect: pg.rect.Rect):
        self.img.set_alpha(self.aplha)
        surface.blit(self.img, (self.rect.x, self.rect.y), area=rect)

class UIText(pg.sprite.Sprite):
    def __init__(self, text, x, y, size):
        pg.sprite.Sprite.__init__(self)
        self.font = pg.font.Font("./font/DotGothic16-Regular.ttf", size)
        self.text = text
        self.pos = np.array([x, y])
        self.color = (255, 255, 255)
        self.text_obj = self.font.render(self.text, True, self.color)

    def update(self):
        self.text_obj = self.font.render(self.text, True, self.color)
    
    def draw(self, surface: pg.surface.Surface):
        surface.blit(self.text_obj, (self.pos[0]-self.text_obj.get_size()[0]/2, self.pos[1]-self.text_obj.get_size()[1]/2))

class UIButtonClassic(pg.sprite.Sprite):
    """クラシックなボタン"""
    def __init__(self, text, rect:pg.rect.Rect, text_pos, font_size, event):
        pg.sprite.Sprite.__init__(self)
        self.rect = rect
        self.text = text
        self.pos = text_pos
        self.font_size = font_size

        self.buttons_image = pg.image.load("./Images/UI/Buttons.png").convert_alpha()
        self.Image = UIImage(self.buttons_image, self.rect)
        self.Image.aplha = 255
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
    """カスタマイズなボタン"""
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