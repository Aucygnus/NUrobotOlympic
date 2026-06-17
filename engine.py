import pygame
import random
import math
import cv2
import os

from detector import PoseDetector
from items import Enemy, Obstacle
from leaderboard import LeaderboardManager

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("NU Olympic GAME")
        
        self.clock = pygame.time.Clock()
        self.detector = PoseDetector()
        self.leaderboard = LeaderboardManager()

        self.LoadAssets()
        
        laneWidth = self.width // 3
        self.lanes = [laneWidth // 2, laneWidth + (laneWidth // 2), (laneWidth * 2) + (laneWidth // 2)]
        
        self.gameState = "STARTSCREEN"
        self.running = True
        
        self.name = ""
        self.rank = 0
        self.ResetGameData()

    def LoadAssets(self) :
        fontPath = 'font/Gameboy.ttf'
        if os.path.exists(fontPath) :
            self.font = pygame.font.Font(fontPath, 48)
            self.Titlefont = pygame.font.Font(fontPath, 80)
            self.countdownFont = pygame.font.Font(fontPath, 300)
        else :
            self.font = pygame.font.SysFont("Arial", 48)

        self.imgBGstart = pygame.image.load('pic/bg_home.png').convert_alpha() if os.path.exists('pic/bg_home.png') else None
        self.imgBGname = pygame.image.load('pic/bg_name.png').convert_alpha() if os.path.exists('pic/bg_name.png') else None

        if self.imgBGstart: self.imgBGstart = pygame.transform.scale(self.imgBGstart, (self.width, self.height))
        if self.imgBGname: self.imgBGname = pygame.transform.scale(self.imgBGname, (self.width, self.height))

        self.imgHead = pygame.image.load('pic/head.png').convert_alpha() if os.path.exists('pic/head.png') else None
        self.imgLHand = pygame.image.load('pic/LHand.png').convert_alpha() if os.path.exists('pic/LHand.png') else None
        self.imgRHand = pygame.image.load('pic/RHand.png').convert_alpha() if os.path.exists('pic/RHand.png') else None
        self.imgLive = pygame.image.load('pic/live.png').convert_alpha() if os.path.exists('pic/live.png') else None
        self.imgLogo = pygame.image.load('pic/logo.png').convert_alpha() if os.path.exists('pic/logo.png') else None
        self.imgHit = pygame.image.load('pic/Hit.png').convert_alpha() if os.path.exists('pic/Hit.png') else None
        self.imgRHit = pygame.image.load('pic/RHit.png').convert_alpha() if os.path.exists('pic/RHit.png') else None

        if self.imgHead: self.imgHead = pygame.transform.smoothscale(self.imgHead, (220,220))
        if self.imgLHand: self.imgLHand = pygame.transform.smoothscale(self.imgLHand, (160,160))
        if self.imgRHand: self.imgRHand = pygame.transform.smoothscale(self.imgRHand, (160,160))
        if self.imgLive: self.imgLive = pygame.transform.smoothscale(self.imgLive, (60,60))
        if self.imgLogo: self.imgLogo = pygame.transform.smoothscale(self.imgLogo, (300,300))
        if self.imgHit: self.imgHit = pygame.transform.smoothscale(self.imgHit, (200,200))
        if self.imgRHit: self.imgRHit = pygame.transform.smoothscale(self.imgRHit, (160,160))

    def ResetGameData(self):
        self.items = []
        self.score = 0
        self.comboCount = 0
        self.live = 3
        self.invincibleTime = 0
        self.countdownFrame = 0
        self.hitEffects = []

    def TextCenter(self, text, color, center_coords, font=None):
        activeFont = font if font else self.font
        textSurface = activeFont.render(text, True, color)
        textRect = textSurface.get_rect(center=center_coords)
        self.screen.blit(textSurface, textRect)

    def TextPos(self, text, color, pos, align="topleft"):
        textSurface = self.font.render(text, True, color)
        if align == "topright":
            textRect = textSurface.get_rect(topright=pos)
        else:
            textRect = textSurface.get_rect(topleft=pos)
        self.screen.blit(textSurface, textRect)

    def HandleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if self.gameState == "INPUTNAME":
                    if event.key == pygame.K_RETURN and len(self.name) > 0:
                        self.gameState = "COUNTDOWN"
                        self.countdownFrame = 90
                    elif event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                else:
                    if event.key == pygame.K_x:
                        self.running = False
                    elif event.key == pygame.K_h:
                        self.ResetGameData()
                        self.gameState = "STARTSCREEN"
                    elif event.key == pygame.K_SPACE and self.gameState == "STARTSCREEN":
                        self.gameState = "INPUTNAME"
                        self.name = ""

            elif event.type == pygame.TEXTINPUT and self.gameState == "INPUTNAME":
                self.name += event.text

    def SpawnItems(self):
        enemyLaneTop = sum(1 for i in self.items if i.type == 'enemy' and i.y < 350)
        
        for lane in self.lanes:
            if random.randint(1, 40) == 1:
                itemType = random.choice(['enemy', 'obstacle'])
                if itemType == 'enemy':
                    if enemyLaneTop >= 2 :
                        itemType = 'obstacle'
                    else :
                        enemyLaneTop += 1
                        
                    targetX = random.randint(150, self.width - 150)
                else:
                    targetX = lane

                isOverlapping = any(abs(i.x - targetX) < 280 and i.y < 300 for i in self.items)

                if not isOverlapping:
                    if itemType == 'enemy':
                        self.items.append(Enemy(targetX))
                    else:
                        self.items.append(Obstacle(lane))

    def UpdatePlaying(self, nose, LHand, RHand):
        if self.invincibleTime > 0:
            self.invincibleTime -= 1

        for effect in self.hitEffects[:] :
            effect['life'] -= 1
            if effect['life'] <= 0:
                self.hitEffects.remove(effect)

        for item in self.items[:]:
            item.Move(self.score)
            
            if item.type == 'obstacle':
                distL = math.hypot(LHand[0] - item.x, LHand[1] - item.y)
                distR = math.hypot(RHand[0] - item.x, RHand[1] - item.y)
                if distL < 100 or distR < 100:
                    if item in self.items: self.items.remove(item)
                    self.comboCount += 1
                    self.score += 10 * self.comboCount

                    self.hitEffects.append({
                        'x': item.x,
                        'y': item.y,
                        'life': 10
                    })
                    
            elif item.type == 'enemy':
                distH = math.hypot(nose[0] - item.x, nose[1] - item.y)
                if distH < 150 and self.invincibleTime <= 0:
                    self.live -= 1
                    self.invincibleTime = 60
                    self.comboCount = 0
                    if self.live <= 0:
                        self.rank = self.leaderboard.Update(self.name, self.score)
                        self.gameState = "GAMEOVER"

            if item.y >= self.height:
                if item.type == 'obstacle':
                    self.comboCount = 0
                if item in self.items: self.items.remove(item)

        self.SpawnItems()

    def render(self, bg_surface, nose, LHand, RHand):
        if self.gameState == "STARTSCREEN":
            if self.imgBGstart:
                self.screen.blit(self.imgBGstart, (0,0))
            else :
                self.screen.fill((0, 0, 0))
            
            if self.imgLogo :
                logoRect = self.imgLogo.get_rect(center=(self.width//2, self.height//3 - 100))
                self.screen.blit(self.imgLogo, logoRect)

            textPos = (self.width//2, self.height//2)
            shadow = pygame.Surface((1280, 110))
            shadow.set_alpha(150)
            shadow.fill((0,0,0))
            shadowRect = shadow.get_rect(center=textPos)
            self.screen.blit(shadow, shadowRect)
            
            self.TextCenter("Press SPACE to Start", (255, 255, 0), (self.width // 2, self.height // 2), font=self.Titlefont)

        elif self.gameState == "INPUTNAME":
            if self.imgBGname:
                self.screen.blit(self.imgBGname, (0,0))
            else :
                self.screen.fill((0, 0, 0))
            
            if self.imgLogo :
                self.imgLogo = pygame.transform.smoothscale(self.imgLogo, (200,200))
                logoRect = self.imgLogo.get_rect(center=(self.width//2, self.height//3 - 150))
                self.screen.blit(self.imgLogo, logoRect)

            textPos = (self.width//2, self.height//2 - 10)
            shadow = pygame.Surface((1280, 300))
            shadow.set_alpha(100)
            shadow.fill((0,0,0))
            shadowRect = shadow.get_rect(center=textPos)
            self.screen.blit(shadow, shadowRect)

            shadow1 = pygame.Surface((1080, 110))
            shadow1.set_alpha(150)
            shadow1.fill((0,0,0))
            shadow1Rect = shadow1.get_rect(center=textPos)
            self.screen.blit(shadow1, shadow1Rect)

            self.TextCenter("Enter Your Name:", (255, 255, 255), (self.width // 2, self.height // 2 - 120), font=self.Titlefont)
            self.TextCenter(self.name + "_", (255, 255, 0), (self.width // 2, self.height // 2 - 10))
            self.TextCenter("Press ENTER to Ready", (255, 255, 255), (self.width // 2, self.height // 2 + 90))

        elif self.gameState == "COUNTDOWN":
            self.screen.fill((0, 0, 0))
            self.countdownFrame -= 1
            seconds = str(int(math.ceil(self.countdownFrame / 30)))
            if self.countdownFrame > 0:
                self.TextCenter(seconds, (255, 0, 0), (self.width // 2, self.height // 2), font=self.countdownFont)
            else:
                self.gameState = "PLAYING"

        elif self.gameState == "PLAYING":
            if bg_surface: self.screen.blit(bg_surface, (0, 0))
            
            if nose != (-1000, -1000):
                if self.imgHead :
                    if self.invincibleTime <= 0 or (self.invincibleTime //4) % 2 == 0:
                        headPos = (nose[0], nose[1] - 50)
                        headRect = self.imgHead.get_rect(center=headPos)
                        self.screen.blit(self.imgHead, headRect)
                else :
                    nose_color = (0, 255, 0) if self.invincibleTime <= 0 else (255, 255, 0)
                    pygame.draw.circle(self.screen, nose_color, nose, 100)

                if self.imgLHand or self.imgRHand :
                    LHandRect = self.imgLHand.get_rect(center=LHand)
                    RHandRect = self.imgRHand.get_rect(center=RHand)

                    self.screen.blit(self.imgLHand, LHandRect)
                    self.screen.blit(self.imgRHand, RHandRect)
                else :
                    pygame.draw.circle(self.screen, (0, 0, 255), LHand, 40)
                    pygame.draw.circle(self.screen, (0, 0, 255), RHand, 40)

            for item in self.items:
                item.draw(self.screen)

            for effect in self.hitEffects :
                if self.imgHit:
                    effectRect = self.imgHit.get_rect(center=(effect['x'], effect['y']))
                    self.screen.blit(self.imgHit,effectRect)
            
            self.TextPos(f'Score : {self.score}', (255, 255, 255), (20, 20))
            self.TextPos(f'High Score : {self.leaderboard.get_high_score()}', (255, 255, 255), (20, 70))
            if self.comboCount > 1:
                self.TextPos(f'COMBO x{self.comboCount}', (255, 255, 255), (20, 120))
            if self.live > 0:
                if self.imgLive :
                    for i in range(self.live):
                        liveX = self.width - 75 - (i * 75)
                        self.screen.blit(self.imgLive, (liveX, 20))
                else :
                    self.TextPos(f'Lives x{self.live}', (255, 100, 100), (self.width - 20, 20), align="topright")

        elif self.gameState == "GAMEOVER":
            if self.imgBGname :
                self.screen.blit(self.imgBGname, (0,0))
            else :
                self.screen.fill((0, 0, 0))
            
            textPos = (self.width//2, 220)
            shadow = pygame.Surface((1280, 110))
            shadow.set_alpha(100)
            shadow.fill((0,0,0))
            shadowRect = shadow.get_rect(center=textPos)
            self.screen.blit(shadow, shadowRect)

            shadow1 = pygame.Surface((0,0))
            shadow1.set_alpha(150)
            shadow1.fill((0,0,0))
            shadow1Rect = shadow1.get_rect(center=textPos)
            self.screen.blit(shadow1, shadow1Rect)

            self.TextCenter("GAME OVER", (255, 0, 0), (self.width // 2, 120), font=self.Titlefont)
            self.TextCenter(f"You are Rank : #{self.rank} SCORE : {self.score}", (255, 255, 0), (self.width // 2, 220))
            self.TextCenter("--- TOP 5 PLAYERS ---", (255, 255, 255), (self.width // 2, 320))
            
            for i, p in enumerate(self.leaderboard.get_top_scores(5)):
                txt = f"{i+1}. {p['name']} : {p['score']}"
                self.TextCenter(txt, (204, 255, 255), (self.width // 2, 380 + (i * 50)))

            self.TextCenter("Press 'H' to Home", (255, 255, 255), (self.width // 2, self.height - 150))
            self.TextCenter("Press 'X' to Exit", (255, 255, 255), (self.width // 2, self.height - 80))

    def run(self):
        while self.running:
            self.HandleEvents()
            bg_surface, nose, LHand, RHand = self.detector.ProcessFrame(self.width, self.height)
            
            if self.gameState == "PLAYING":
                self.UpdatePlaying(nose, LHand, RHand)
                
            self.render(bg_surface, nose, LHand, RHand)
            
            pygame.display.flip()
            self.clock.tick(30)
            
        self.detector.release()
        cv2.destroyAllWindows()
        pygame.quit()