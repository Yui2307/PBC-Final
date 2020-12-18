#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cocos
import struct
import pyaudio
from cocos.sprite import Sprite
from pyaudio import paInt16
import random
from cocos.scenes.transitions import *



# In[2]:


import pyglet
black = pyglet.image.load("block.png")
bg = pyglet.image.load("forest.png")


# In[3]:


class Rabbit(cocos.sprite.Sprite):
    def __init__(self):
        img = pyglet.image.load('res/R5.png')
        img_grid = pyglet.image.ImageGrid(img, 1, 8, item_width=100, item_height=107)
        Rabbitpic = pyglet.image.Animation.from_image_sequence(img_grid[0:],0.1, loop = True)
        super(Rabbit, self).__init__(Rabbitpic)
        self.image_anchor = 0 , 0
        self.reset(False)
        self.schedule(self.update)
    
    def jump(self,h):
        if self.is_able_jump:
            self.y += 1
            self.speed -= max(min(h,6),8)
            self.is_able_jump = False
    
    def land(self, y):
        if self.y > y-25:
            self.is_able_jump = True
            self.speed = 0
            self.y = y
    
    def update(self, dt):
        self.speed += 10*dt
        self.y -= self.speed
        if self.y < -85:
            self.reset()
    
    def reset(self, flag = True):
        if flag: self.parent.reset()
        self.is_able_jump = False
        self.speed = 0
        self.position = 80, 280


# In[4]:


class Block(cocos.sprite.Sprite):
    def __init__(self,position):
        super(Block,self).__init__(black)
        self.image_anchor = 0 , 0
        x, y = position
        if x == 0:
            self.scale_x = 8
            self.scale_y = 1
        else:
            self.scale_x = 0.5 + random.random()*2.5
            self.scale_y = min(max(y-50+random.random()*100,100),300)/100
            self.position = x + 200+ random.random()*100,0

class Game_BG(cocos.layer.Layer):
    def __init__(self):
        super(Game_BG,self).__init__()
        d_width, d_height = cocos.director.director.get_window_size()
        background = cocos.sprite.Sprite(bg)
        background.position = d_width // 2, d_height // 2
        self.add(background)



# In[5]:


#import cfg  ## 不知道這個的模組是什麼～～～無法import


# In[6]:


#import configparser


# In[7]:


#config = configparser.ConfigParser()


# In[8]:


class VoiceControlGame(cocos.layer.ColorLayer):
    def __init__(self):
        super(VoiceControlGame, self).__init__(255,255,255,255,800,600)
        self.num_samples = 1000
        self.Game_BG = Game_BG()
        self.add(self.Game_BG)       
        
        self.vbar = Sprite(black)
        self.vbar.position = 20, 450
        self.vbar.scale_y = 0.1
        self.vbar.image_anchor = 0,0
        self.add(self.vbar)

        self.rabbit = Rabbit()
        self.add(self.rabbit)

        
        
        self.floor = cocos.cocosnode.CocosNode()
        self.add(self.floor)
        position = 0,100
        for i in range(120):
            b= Block(position)
            self.floor.add(b)
            position = b.x+b.width, b.height
        
        audio = pyaudio.PyAudio()
        self.stream = audio.open(format = paInt16, channels=1, rate = int(audio.get_device_info_by_index(0)["defaultSampleRate"]),input= True,frames_per_buffer=self.num_samples)
        self.schedule(self.update)
    
    def collide(self):
        diffx = self.rabbit.x - self.floor.x
        for b in self.floor.get_children():
            if(b.x <= diffx + self.rabbit.width*0.8) and (diffx + self.rabbit.width*0.2 <= b.x + b.width):
                if self.rabbit.y < b.height:
                    self.rabbit.land(b.height)
                    break
    
    def update(self, dt):
        audio_data = self.stream.read(self.num_samples, exception_on_overflow = False)
        k = max(struct.unpack("1000h",audio_data))
        self.vbar.scale_x = k/10000
        self.floor.x -= 200*dt
        if k > 2000:
            self.rabbit.jump((k-1000)/1000)
        self.collide()
    
    def reset(self):
        self.floor.x = 0  


# In[]:


if __name__ == "__main__":
    cocos.director.director.init(caption="rabbit jump")
    cocos.director.director.run(cocos.scene.Scene(VoiceControlGame()))  


# In[ ]:




