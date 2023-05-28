import pygame as pg
from pygame.locals import *
from math import *
import os
import random as rng
run = False
pg.init()
def clamp(n, smallest, largest): 
    return max(smallest, min(n, largest))
class ParticleType:
    def __init__(self, name, desc, color, liquid, powder, weight):
        self.name = name
        self.desc = desc
        self.color = color
        self.liquid = liquid
        self.powder = powder
        self.weight = weight
def raw2element(raw):
    f = open(raw,'r').read()
    a = f.split("\n")
    print(a)
    return ParticleType(a[0],a[1],int(a[2],16),a[3]=='True',a[4]=='True',int(a[5]))
particleTypes = [raw2element("elements/"+i) for i in os.listdir("elements")]
resolution = (320,240)
dsp = pg.display.set_mode(resolution,pg.SCALED)
title = "Powder"
pg.display.set_caption(title)
clock = pg.time.Clock()
pixc = resolution[0]*resolution[1]
particle_sheet = [None]*pixc
font = pg.font.SysFont(None, 16)
spawnedParticles = 0
def pos2index(x,y):
    return y * resolution[0] + x
def findpart(x,y):
    return particle_sheet[pos2index(x,y)]
class Particle:
    def __init__(self, x : int, y : int, ptype : ParticleType):
        self.x = x
        self.y = y
        self.type = ptype
        self.index = spawnedParticles
    def move(self,ax,ay):
        cond = not findpart(self.x+ax,self.y+ay) and self.y+ay > 1 and self.y+ay < resolution[1]-1 and self.x+ax > 1 and self.x+ax < resolution[0]-1
        success = False
        if cond:
            particle_sheet[pos2index(self.x,self.y)] = None
            self.x += ax
            self.y += ay
            particle_sheet[pos2index(self.x,self.y)] = self
            success = True
        else:
            if self.type.liquid:
                part = findpart(self.x+ax,self.y+ay)
                if part != None:
                    if part.type.weight < self.type.weight and (part.type.powder or part.type.liquid):
                        particle_sheet[pos2index(self.x,self.y)] = part
                        self.x += ax
                        self.y += ay
                        particle_sheet[pos2index(self.x,self.y)] = self
                        success = True
        return success
        
    def step(self):
        if self.type.liquid:
            if not self.move(0,-1):
                if not findpart(self.x-1,self.y):
                    self.move(-1,0)
                if not findpart(self.x+1,self.y):
                    self.move(1,0)
                self.move(rng.randint(-1,0)*2+1,0)
        else:
            if self.type.powder:
                self.move(0,-1)
        
run = True

def draw():
    dsp.fill(0)
    pixel_array = pg.PixelArray(dsp)
    for i in particle_sheet:
        if i != None:
            pixel_array[i.x,resolution[1]-i.y] = i.type.color
    pixel_array.close()

def part_step():
    for i in particle_sheet:
        if i != None:
            i.step()
        
currentElement = 0

while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN:
            keys = pg.key.get_pressed()
            if keys[pg.K_q]:
                currentElement = (currentElement + 1)%len(particleTypes)
            if keys[pg.K_w]:
                currentElement = (currentElement - 1)%len(particleTypes)
    click = pg.mouse.get_pressed()
    if click[0]:
        pos = pg.mouse.get_pos()
        newpos = (clamp(pos[0],1,resolution[0]-1),clamp(resolution[1]-pos[1],1,resolution[1]-1))
        newpart = Particle(newpos[0],newpos[1],particleTypes[currentElement])
        particle_sheet[pos2index(newpos[0],newpos[1])] = newpart
        spawnedParticles += 1
    part_step()
    draw()
    elem = particleTypes[currentElement]
    name = font.render(f"{''.join(i.upper() for i in elem.name)}", True, pg.Color('white'))
    dsp.blit(name, (10, 10))
    fps = clock.get_fps()
    pg.display.set_caption(f"{title} - {int(fps)} FPS")
    clock.tick(9999)
    pg.display.flip()

