import pygame
import os

class GameItem:
    def __init__(self, x, item_type):
        self.x = x
        self.y = 0
        self.type = item_type
        self.radius = 150
        self.img = None

    def Move(self, score):
        speed = 10 + (score / 25)
        self.y += speed

    def draw(self, surface):
        if self.img :
            imgRect = self.img.get_rect(center=(self.x, int(self.y)))
            surface.blit(self.img, imgRect)
        else :
            pygame.draw.circle(surface, (128,128,128), (self.x, int(self.y)), self.radius)

class Enemy(GameItem):
    def __init__(self, x):
        super().__init__(x, 'enemy')
        imgPath = "pic/enemy.png"
        if os.path.exists(imgPath):
            RAWimg = pygame.image.load(imgPath).convert_alpha()
            self.img = pygame.transform.smoothscale(RAWimg, (self.radius * 2, self.radius * 2))

    def draw(self, surface):
        if self.img :
            super().draw(surface)
        else:
            pygame.draw.circle(surface, (255, 0, 0), (self.x, int(self.y)), self.radius)

class Obstacle(GameItem):
    def __init__(self, x):
        imgPath = "pic/obstacle.png"
        super().__init__(x, 'obstacle')
        if os.path.exists(imgPath) :
            RAWimg = pygame.image.load(imgPath).convert_alpha()
            self.img = pygame.transform.smoothscale(RAWimg, (self.radius * 2, self.radius * 2))

    def draw(self, surface):
        if self.img :
            super().draw(surface)
        else :
            pygame.draw.circle(surface, (255, 165, 0), (self.x, int(self.y)), self.radius)