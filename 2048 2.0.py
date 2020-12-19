# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 19:59:12 2020

@author: YUI
"""

"""
2048 game.
"""
import random
import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import numpy

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
                self.matrix[i].append(Block(0))

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
        
class Block:
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
    #print str(board)
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
        #print "left\n"
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
        #print "right\n"
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
        #print "up\n"
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
        #print "down\n"
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
    #print str(board) 
    #print "\n"+str(judgedir[0])+" "+str(judgedir[1])+" "+str(judgedir[2])+" "+str(judgedir[3])

    
frame = simplegui.create_frame('2048', 420, 460)
frame.set_canvas_background("White")
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
init()
frame.start()