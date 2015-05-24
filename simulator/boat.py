__author__ = 'will'
import pygame
from loader import load_image
from math import *
from settings import *
from pid import PID
from plotter import AnalogData, AnalogPlot

rotate = pygame.transform.rotate
scale = pygame.transform.scale

class Boat(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('boat.png', -1)
        self.image = scale(self.image, (50, 100))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.original = self.image
        self.direction = 0 # 0 - 360
        self.speed = 1
        self.rudder = 0
        self.motor = 0.3

        self.dirPID = PID(0.3,0,0)
        self.speedPID = PID(-0.001,0,0)

        # self.analogData = AnalogData(10000)
        # self.analogPlot = AnalogPlot(self.analogData)


    def acelerate(self,power):
        """

        :param power: 0-100
        :return:
        """
        self.motor = min(power / 100.0,5)

    def turn(self, direction):
        self.rudder = max(min(direction, MAXTURN), -MAXTURN)


    def calculate_data(self):
        x, y = self.rect.center
        targetx, targety = pygame.mouse.get_pos()
        targetdir = degrees(atan2(y-targety, targetx-x))
        self.dirPID.set_point = targetdir

        y,x = targetdir,self.direction
        self.rudder = self.dirPID.update(error=min(y-x, y-x+360, y-x-360, key=abs))

        distance = sqrt((targetx-x)**2 + (targety -y)**2)
        self.motor = min(self.speedPID.update(distance),2)

        # self.analogData.add(self.direction)
        # self.analogPlot.update(self.analogData)

    def update(self):
        "walk or spin, depending on the monkeys state"
        self.calculate_data()

        self.move(self.rudder, self.motor)

        self.image = rotate(self.original, self.direction + 90)

        # self.rect = self.image.get_rect(center=center)

    def move(self,rudder,motor):
        current_direction = self.direction + self.speed * rudder * 0.01
        self.direction = current_direction
        self.speed+= motor
        self.speed *= DRAG
        newpos = self.rect.move((cos(radians(current_direction))*self.speed,-sin(radians(current_direction))*self.speed))
        self.rect = newpos