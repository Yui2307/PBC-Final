#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import cocos
import time
from pyglet import image
import random
from cocos.sprite import Sprite
from pyaudio import paInt16
import struct
from cocos.scenes.transitions import *
import pygame
import pyaudio
import SimpleGUICS2Pygame.simpleguics2pygame as simplegui


# In[2]:


pygame.mixer.init()
#pygame.mixer.music.load('totoro.mp3')
#pygame.mixer.music.play(-1)


# In[3]:


import pyglet
black = pyglet.image.load("block.png")
bg = pyglet.image.load("forest.png")
carrot = pyglet.image.load("carrot.png")

# In[4]:


class Rabbit(cocos.sprite.Sprite):
    def __init__(self, game):
        img = pyglet.image.load('res/R5.png')
        img_grid = pyglet.image.ImageGrid(img, 1, 8, item_width=100, item_height=107)
        Rabbitpic = pyglet.image.Animation.from_image_sequence(img_grid[0:],0.1, loop = True)
        super(Rabbit, self).__init__(Rabbitpic)

        self.game = game
        self.dead = False
        self.is_able_jump = False
        self.speed = 0
        self.position = 100, 300
        self.image_anchor = 0 , 0
        self.rush_time = 0  #
        self.velocity = 0  #
        self.schedule(self.update)
    
    
    def jump(self,h):
        if self.dead:
            return
        if self.is_able_jump:
            self.y += 1
            self.speed -= max(min(h,6),8)
            self.is_able_jump = False
    
    def land(self, y):
        if self.dead:
            return
        if self.y > y-25:
            self.is_able_jump = True
            self.speed = 0
            self.y = y
    
    def update(self, dt):
        if self.dead:
            return
        self.speed += 10*dt
        self.y -= self.speed
        if self.y < -85:
            self.die()
        if self.rush_time > 0:  #
            self.rush_time -= dt
            if self.rush_time <= 0:
                self.velocity = 0
            
    def die(self):
        time.sleep(2.7)
        self.speed = 0
        self.dead = True
        self.game.end_game()
        
    def reset(self, flag = True):
        if flag: self.parent.reset()
        self.is_able_jump = False
        self.dead = False
        self.speed = 0
        self.velocity = 0  
        self.rush_time = 0 
        self.position = 80, 280


# In[5]:


class Block(cocos.sprite.Sprite):
    def __init__(self, game):
        super(Block, self).__init__(black)
        self.game = game
        self.rabbit = game.rabbit
        self.floor = game.floor
        self.active = True
        self.image_anchor = 0 , 0
        self.reset()
        self.schedule(self.update)
        
    def update(self, dt):
        if self.active and self.x < self.rabbit.x - self.floor.x:
            self.active = False
            self.game.add_score()
        if self.x + self.width + self.game.floor.x < -10:
            self.reset()

    def reset(self):
        x, y = self.game.last_block
        if x == 0:
            self.scale_x = 10
            self.scale_y = 1
            self.position = 0, 0
            self.active = False
        else:
            self.scale_x = 0.5 + random.random() * 2.5
            self.scale_y = min(max(y - 50 + random.random() * 100, 100), 300) / 100
            self.position = x + 200 + random.random() * 100, 0
            self.active = True
            if self.x > 1000 and random.random() > 0.6:
                self.floor.add(Carrot(self))
        self.game.last_block = self.x + self.width, self.height


# In[6]:


class Game_BG(cocos.layer.Layer):
    def __init__(self):
        super(Game_BG,self).__init__()
        d_width, d_height = cocos.director.director.get_window_size()
        background = cocos.sprite.Sprite(bg)
        background.position = d_width // 2, d_height // 2
        self.add(background)


# In[7]:


class RabbitJump(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        super(RabbitJump, self).__init__(255,255,255,255,800,600)
        pygame.mixer.init()

        font = ['SimHei', 'STHeiti', 'SimHei', 'SimSun']
        WHITE = (255, 255, 255, 255) 
        
        self.score = 0 
        self.txt_score = cocos.text.Label(u'score：0',
                                          font_name=font,
                                          font_size=24,
                                          bold = True,
                                          color=WHITE)
        self.txt_score.position = 450, 440
        self.add(self.txt_score, 99999)
        
        self.num_samples = 1000
        self.Game_BG = Game_BG()
        self.add(self.Game_BG)       
        
        self.vbar = Sprite(black)
        self.vbar.position = 20, 450
        self.vbar.scale_y = 0.1
        self.vbar.image_anchor = 0,0
        self.add(self.vbar)

        self.rabbit = Rabbit(self)
        self.add(self.rabbit)

        
        self.floor = cocos.cocosnode.CocosNode()
        self.add(self.floor)
        self.last_block = 0,100
        for i in range(120):
            b= Block(self)
            self.floor.add(b)
            position = b.x+b.width, b.height
        
        audio = pyaudio.PyAudio()
        self.stream = audio.open(format = paInt16, channels=1, rate = int(audio.get_device_info_by_index(0)["defaultSampleRate"]),input= True,frames_per_buffer=self.num_samples)
        pygame.mixer.music.load('totoro.mp3')
        pygame.mixer.music.play(-1)
        self.schedule(self.update)
    
    def on_mouse_press(self, x, y, buttons, modifiers):
        pass
    
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
        cocos.director.director.run(test_scene2)
        self.floor.x = 0
        self.last_block = 0,100
        for b in self.floor.get_children():
            b.reset()
        self.score = 0
        self.txt_score.element.text = u'score：0'
        self.rabbit.reset()
        if self.gameover:
            self.remove(self.gameover)
            self.gameover = None
    
    def end_game(self):
        self.stream.stop_stream()
        self.pause_scheduler()
        self.gameover = Gameover(self)
        #self.gameover = GameOverMenu()
        self.add(self.gameover, 100000)
        pygame.mixer.music.stop()
    
    def add_score(self):
        self.score += 1
        self.txt_score.element.text = u'score：%d' % self.score


class Carrot(cocos.sprite.Sprite):
    def __init__(self, block):
        super(Carrot, self).__init__(carrot)
        self.game = block.game
        self.rabbit = block.game.rabbit
        self.floor = block.floor
        self.position = block.x + block.width / 2, block.height + 150

        self.schedule(self.update)

    def update(self, dt):
        px = self.rabbit.x + self.rabbit.width / 2 - self.floor.x
        py = self.rabbit.y + self.rabbit.height / 2

        if abs(px - self.x) < 50 and abs(py - self.y) < 50:
            self.parent.remove(self)
            self.rabbit.rush()

    def reset(self):
        self.parent.remove(self)

# In[8]:


class Gameover(cocos.layer.ColorLayer):
    def __init__(self, game):
        super(Gameover, self).__init__(0, 0, 0, 255, 640, 480)
        self.game = game
        font = ['SimHei', 'STHeiti', 'SimHei', 'SimSun']
        self.score = cocos.text.Label(u'Your Score：%d' % self.game.score,
                                      font_name=font,
                                      font_size=36)
        self.score.position = 170, 340
        self.add(self.score)
        menu = cocos.menu.Menu(u'Game Over')
        menu.font_title['font_name'] = font
        menu.font_item['font_name'] = font
        menu.font_item_selected['font_name'] = font
        replay = cocos.menu.MenuItem(u'Click Here', self.replay)
        replay.y = -100
        menu.create_menu([replay])
        self.add(menu)
        
    def replay(self):
        self.game.reset()


# In[9]:


class MainMenu(cocos.menu.Menu):
    def __init__(self):
        super().__init__("My Game")
        items = []
        items.append(cocos.menu.MenuItem("New Game:RabbitJump", self.rabbit_new_game))
        items.append(cocos.menu.MenuItem("New Game:2048", self.s2048_new_game))
        items.append(cocos.menu.MenuItem("Quit", self.on_quit))
        self.create_menu(items, cocos.menu.shake(), cocos.menu.shake_back())
    def rabbit_new_game(self):
        cocos.director.director.run(cocos.scene.Scene(RabbitJump())) 
    def s2048_new_game(self):
        frame = simplegui.create_frame('2048', 420, 460)
        frame.set_canvas_background("White")
        frame.set_draw_handler(draw)
        frame.set_keydown_handler(keydown)
        init()
        frame.start() 
    def on_quit(self):
        cocos.director.director.window.close()
        
class GameOverMenu(cocos.menu.Menu):
    def __init__(self):
        super().__init__("GameOver")
        items2 = []
        items2.append(cocos.menu.MenuItem("Try agin", self.try_agin))
        items2.append(cocos.menu.MenuItem("New Game:2048", self.t2048_new_game))
        items2.append(cocos.menu.MenuItem("Quit", self.aquit))
        
        self.create_menu(items2, cocos.menu.shake(), cocos.menu.shake_back())
    def try_agin(self):
        cocos.director.director.run(cocos.scene.Scene(RabbitJump()))  
    def aquit(self):
        cocos.director.director.window.close()
    def t2048_new_game(self):
        frame = simplegui.create_frame('2048', 420, 460)
        frame.set_canvas_background("White")
        frame.set_draw_handler(draw)
        frame.set_keydown_handler(keydown)
        init()
        frame.start() 
        
LINEWIDTH=10
BLOCKWIDTH=90
REFPOS=(10,10)
judgedir=[0,0,0,0]

class Nmatrix:
    """
    2048 2D matrix
    """
    def __init__(self):
        """
        assign matrix value
        """
        global TILE2TIMES
        self.matrix=[]
        for i in range(4):
            self.matrix.append([])
            for j in range(4):
                self.matrix[i].append(sBlock(0))

    def __str__(self):
        """
        get matrix value
        """
        output=""
        for ival in range(4):
            for jval in range(4):
                output+=" "+str(self.matrix[ival][jval])
            output+="\n"
        return output
        
    def get_element(self,x,y):
        """
        give x,y cord and get element value
        """
        return self.matrix[x][y]
    def modify(self,x,y,inputval):
        """
        change matrix[x][y] value
        """
        self.matrix[x][y].changeval(inputval)
    
    def draw(self,canvas,pos):
        for ival in range(4):
            for jval in range(4):
                self.matrix[ival][jval].draw(canvas,(pos[0]+jval*(BLOCKWIDTH+10),pos[1]+ival*(BLOCKWIDTH+10))) 
        
class sBlock:
    """
    2048 block element    
    """    
    def __init__(self,value):
        self._value=value
        
    def changeval(self,value):
        self._value=value
    def getval(self):
        return self._value
    def __str__(self):
        #output=str(self._value)
        return str(self._value)
    def draw(self,canvas,pos):
        if self._value == 0:
            canvas.draw_line( pos,(pos[0]+BLOCKWIDTH+10,pos[1]), BLOCKWIDTH, 'Gray')
        else:
            if self._value<10:
                canvas.draw_line( pos,(pos[0]+BLOCKWIDTH+10,pos[1]), BLOCKWIDTH, 'Orange')
                canvas.draw_text(str(self._value), (pos[0]+32,pos[1]+20), 50, 'Black')
            elif self._value<100:
                canvas.draw_line( pos,(pos[0]+BLOCKWIDTH+10,pos[1]), BLOCKWIDTH, 'red')
                canvas.draw_text(str(self._value), (pos[0]+20,pos[1]+20), 50, 'white')
            elif self._value<1000:
                canvas.draw_line( pos,(pos[0]+BLOCKWIDTH+10,pos[1]), BLOCKWIDTH, 'Green')
                canvas.draw_text(str(self._value), (pos[0]+15,pos[1]+20), 40, 'white')     
            elif self._value<3000:
                canvas.draw_line( pos,(pos[0]+BLOCKWIDTH+10,pos[1]), BLOCKWIDTH, 'Blue')
                canvas.draw_text(str(self._value), (pos[0]+5,pos[1]+20), 40, 'white')        
def merge(line):
    """
    Function that merges a single row or column in 2048.
    """
    templine=[]

    #non-zero element put to the leftest side
    for element in line:
        if(element != 0):
            templine.append(element)
    
    #0 pending
    zeronumber=len(line)-len(templine)
    while(zeronumber>0):
        templine.append(0)
        zeronumber-=1

    #element appear twice merge together
    counter=0
    while(counter<len(templine)-1):
        if (templine[counter] != 0):
            if templine[counter] == templine[counter+1]:
                templine[counter]=templine[counter]*2
                templine[counter+1]=0
        counter+=1
    
    #0 element move to rightside
    counter=0
    while(counter<len(templine)):
        if(templine[counter] == 0):
            templine.pop(counter)
            templine.append(0)
        counter+=1
    return templine 


def addnewtile():
    """
    Function that add new tile "randomly" after move_tile/merge
    90% add 2,10% add 4
    """
    randnumber=random.randrange(0, 10)
    if randnumber==9:
        return 4
    else:
        return 2
  
    
def init():
    global board
    board=Nmatrix()
    times=0
    while(times<2):
        rand_x=random.randrange(0, 4)
        rand_y=random.randrange(0, 4)
        if (board.get_element(rand_x,rand_y).getval() == 0):
            board.modify(rand_x,rand_y,addnewtile())
            times+=1
def draw(canvas):
    global board,REFPOS
    board.draw(canvas,(REFPOS[0]+5,REFPOS[1]+50))
    for num in range (5):
        canvas.draw_polygon([(REFPOS[0]+num*100,REFPOS[1]),(REFPOS[0]+num*100,REFPOS[1]+4*100)], 10, 'black')
        canvas.draw_polygon([(REFPOS[0],REFPOS[1]+num*100),(REFPOS[0]+4*100,REFPOS[1]+num*100)],10, 'black')
    if judgedir[0] and judgedir[1] and judgedir[2] and judgedir[3]:
         canvas.draw_text("You loose!", [200,450],50,"Red")
def keydown(key):
    global board,judgedir
    tmp=Nmatrix()
    """
    tmp for comparison
    """
    for ival in range(4):
        for jval in range (4):
            tmp.modify(ival,jval,board.get_element(ival,jval).getval())
    
    if key==simplegui.KEY_MAP['left']:
        count=0
        for ival in range(4):
            line=[]
            for jval in range (4):
                line.append(board.get_element(ival,jval).getval())
            line=merge(line)
            for kval in range (4):
                board.modify(ival,kval,line[kval])

        for ival in range(4):
            for jval in range (4):
                if tmp.get_element(ival,jval).getval() is not board.get_element(ival,jval).getval():
                    count+=1

        if count != 0:
            times=0
            judgedir[0]=0   
            while(times<1):
                rand_x=random.randrange(0, 4)
                rand_y=random.randrange(0, 4)
                if (board.get_element(rand_x,rand_y).getval() == 0):
                    board.modify(rand_x,rand_y,addnewtile())
                    times+=1
        else:
            sum=0
            for ival in range(4):
                for jval in range (4): 
                     if board.get_element(ival,jval).getval() != 0:
                            sum+=1
            if sum == 16:
                judgedir[0]=1
            

    elif key==simplegui.KEY_MAP['right']:
        count=0
        for ival in range(4):
            line=[]
            for jval in range (4):
                line.append(board.get_element(ival,3-jval).getval())
            line=merge(line)
            line=line[::-1]
            for kval in range (4):
                board.modify(ival,kval,line[kval])

        for ival in range(4):
            for jval in range (4):
                if tmp.get_element(ival,jval).getval() is not board.get_element(ival,jval).getval():
                    count+=1

        if count != 0:
            times=0
            judgedir[1]=0   
            while(times<1):
                rand_x=random.randrange(0, 4)
                rand_y=random.randrange(0, 4)
                if (board.get_element(rand_x,rand_y).getval() == 0):
                    board.modify(rand_x,rand_y,addnewtile())
                    times+=1
        else:
            sum=0
            for ival in range(4):
                for jval in range (4): 
                     if board.get_element(ival,jval).getval() != 0:
                            sum+=1
            if sum == 16:
                judgedir[1]=1           
      
    elif key==simplegui.KEY_MAP['up']:
        count=0
        for ival in range(4):
            line=[]
            for jval in range (4):
                line.append(board.get_element(jval,ival).getval())
            line=merge(line)
            for kval in range (4):
                board.modify(kval,ival,line[kval])

        for ival in range(4):
            for jval in range (4):
                if tmp.get_element(ival,jval).getval() is not board.get_element(ival,jval).getval():
                    count+=1

        if count != 0:
            times=0
            judgedir[2]=0   
            while(times<1):
                rand_x=random.randrange(0, 4)
                rand_y=random.randrange(0, 4)
                if (board.get_element(rand_x,rand_y).getval() == 0):
                    board.modify(rand_x,rand_y,addnewtile())
                    times+=1
        else:
            sum=0
            for ival in range(4):
                for jval in range (4): 
                     if board.get_element(ival,jval).getval() != 0:
                            sum+=1
            if sum == 16:
                judgedir[2]=1
    elif key==simplegui.KEY_MAP['down']:
        count=0
        for ival in range(4):
            line=[]
            for jval in range (4):
                line.append(board.get_element(3-jval,ival).getval())
            line=merge(line)
            line=line[::-1]
            for kval in range (4):
                board.modify(kval,ival,line[kval])

        for ival in range(4):
            for jval in range (4):
                if tmp.get_element(ival,jval).getval() is not board.get_element(ival,jval).getval():
                    count+=1

        if count != 0:
            times=0
            judgedir[3]=0   
            while(times<1):
                rand_x=random.randrange(0, 4)
                rand_y=random.randrange(0, 4)
                if (board.get_element(rand_x,rand_y).getval() == 0):
                    board.modify(rand_x,rand_y,addnewtile())
                    times+=1
        else:
            sum=0
            for ival in range(4):
                for jval in range (4): 
                     if board.get_element(ival,jval).getval() != 0:
                            sum+=1
            if sum == 16:
                judgedir[3]=1 

# In[ ]:


if __name__ == "__main__":
    cocos.director.director.init(caption="Rabbit Jump")
    menu = MainMenu()
    try_agin = GameOverMenu()
    test_scene = cocos.scene.Scene()
    test_scene2 = cocos.scene.Scene()
    test_scene.add(menu)
    test_scene2.add(try_agin)
    cocos.director.director.run(test_scene)


# In[2]:


get_ipython().system('pip install SimpleGUICS2Pygame')


# In[ ]:




