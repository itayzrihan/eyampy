import pygame, os
pygame.init()
winSize = (640,480)
win = pygame.display.set_mode(winSize)
pygame.display.set_caption('Game of Thrones: Into the New World')

def loadImageListInDict(path):
    '''
        Create a list for every sub_dir, and load the files(only images) under the sub_dir into the the list.
        Store the lists into a dictionary and return.
        Directory is needed as argument.
    '''
    listsDict = {}
    for folder in os.listdir(path):
        subPath = os.path.join(path, folder)
        if os.path.isdir(subPath):
            listsDict[folder] = []
            for image in os.listdir(subPath):
                if os.path.isfile(os.path.join(subPath,image)):
                    listsDict[folder].append(pygame.image.load(os.path.join(subPath,image)))
    return listsDict


def loadImageDict(path):
    '''
        Load all the files(only images) under the directory into a dictionary and return.
        Directory is needed as argument.
    '''
    imageDict = {}
    for image in os.listdir(path):
        subPath = os.path.join(path, image)
        if os.path.isfile(subPath):
            imageDict[os.path.splitext(image)[0]] = pygame.image.load(subPath)
    return imageDict


class mainPlayer(object):
    '''
        This object class defines attributes of a player. 
        Allow the entering of up, down, left, right and space keys to control the movement of the object.
        Shooting is only allowed outside the safezone(self.x > 100). 
        Character sprites (left and right) and a bullet image is needed as initial data.
    '''
    def __init__(self, x, y, width, height, vel, lifeLeft, walkLeft,walkRight,bulletImage):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = vel
        self.standing = True
        self.jumpPow = 10
        self.isJumping = False
        self.left = False
        self.right = False
        self.facing = 1
        self.collision = False
        self.walkCount = 0
        self.hitbox = (round(self.x + self.width * 0.02), round(self.y + self.width * 0.02), round(self.width * 0.96), round(self.height*0.96))
        self.bullets = []
        self.lifeLeft = lifeLeft
        self.fullHealth = lifeLeft
        self.walkLeft = walkLeft
        self.walkRight = walkRight
        self.shootLoop = 0
        self.bulletImage = bulletImage
        self.rebornLoc = (x,y)

    def keysPressed(self,isLeftPressed,isRightPressed,isUpPressed,isSpacePressed):
        if isLeftPressed and self.x >= self.vel:
            self.standing = False
            self.left = True
            self.right = False
            self.x -= self.vel
            self.facing = -1

        elif isRightPressed and self.x < winSize[0]:
            self.standing = False
            self.left = False
            self.right = True
            self.x += self.vel
            self.facing = 1 
                
        else:
            self.standing = True
            self.walkCount = 0

        '''Jumping activation'''
        if not self.isJumping:
            if isUpPressed :
                self.isJumping = True
                self.walkCount = 0

        else:
            if self.jumpPow >= -10:
                neg = 1
                if self.jumpPow < 0:
                    neg = -1
                    
                self.y -= (self.jumpPow ** 2) * 0.5 * neg 
                self.jumpPow -= 1
            
            else:
                self.isJumping = False
                self.jumpPow = 10

        '''Shooting activation'''
        if self.shootLoop >= 1 and self.shootLoop <= 8:
            self.shootLoop += 1
        else:
            self.shootLoop = 0
    
        if isSpacePressed and self.shootLoop == 0 and self.x >= 100:
            bulletSound.play()
            self.bullets.append(projectile(round(self.x + self.width // 2),round(self.y + self.height//2),5,8 * self.facing, self.bulletImage))
            self.shootLoop = 1

        for bullet in self.bullets:
            if not(bullet.x <= winSize[0] - 8 and bullet.x >= 8):
                self.bullets.pop(self.bullets.index(bullet))        
                           
    def draw(self,win):

        if self.lifeLeft >= 1:
            keys = pygame.key.get_pressed()
            self.keysPressed(keys[pygame.K_LEFT],keys[pygame.K_RIGHT],keys[pygame.K_UP],keys[pygame.K_SPACE])
            for bullet in self.bullets:
                bullet.draw(win)
            if self.collision == True:
                self.lifeLeft -= 1
                self.isJumping = False
                self.jumpPow = 10
                self.x = self.rebornLoc[0]
                self.y = self.rebornLoc[1]
                self.walkCount = 0
                self.Right = True
                i = 0
                while i < 60:
                    pygame.time.delay(10)
                    i += 1
    
                self.collision = False
                
            if self.walkCount >= len(self.walkLeft) * 3:
                self.walkCount = 0

            if self.standing:
                if self.left:
                    win.blit(self.walkLeft[0],(self.x,self.y))
                else:
                    win.blit(self.walkRight[0],(self.x,self.y))
            else:
                if self.left:
                    win.blit(self.walkLeft[self.walkCount//3],(self.x,self.y))
                    self.walkCount += 1           
                else:
                    win.blit(self.walkRight[self.walkCount//3],(self.x,self.y))
                    self.walkCount += 1
            
            self.hitbox = (round(self.x + self.width * 0.02), round(self.y + self.width * 0.02), round(self.width * 0.96), round(self.height * 0.96))
##            pygame.draw.rect(win,(255,0,0),self.hitbox,2)


class projectile(object):
    '''
        This object class defines attributes of a bullet. 
        The x instance always change in accordance to the velocity instance.    
    '''
    def __init__(self,x,y,radius,vel,bulletImage):
        self.x = x 
        self.y = y 
        self.radius = radius
        self.vel = vel
        self.bulletImage = bulletImage
        
    def draw(self,win):
        self.x += self.vel
        win.blit(self.bulletImage,(self.x - self.radius, self.y - self.radius))         


class enemy1(object):
    '''
        This object represents an enemy. 
        It moves in x direction, and it will only be moving back and fore in a given boundary.
        Whenever it collides with player's hitbox, player's health point minus 1.
        Whenever its hitbox collides with player's bullet, its health point minus 1.
        When its healthpoint < 1, all of its functions terminate.
        Enemy sprites is needed as argument.
    '''

    def __init__(self,x,y,width,height,leftEnd,rightEnd,facing,vel,health,walkLeft,walkRight):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.leftEnd = leftEnd
        self.rightEnd = rightEnd
        self.walkCount = 0
        self.vel = vel
        '''facing = 1 or -1, determines the walking direction of the object'''
        self.facing = facing
        self.hitbox = (round(self.x + self.width * 0.1), round(self.y + self.width * 0.1), round(self.width * 0.8), round(self.height * 0.8))
        self.health = health
        self.fullHealth = health
        self.isDefeated = False
        self.walkLeft = walkLeft
        self.walkRight = walkRight        

    def move(self):
        if self.x + self.width + self.vel >= self.rightEnd:
            self.facing = -1
            self.walkCount = 0
            
        elif self.x - self.vel <= self.leftEnd:
            self.facing = 1
            self.walkCount = 0

        self.x += self.vel * self.facing
    
    def hit(self):
        if self.health >= 1 and player.lifeLeft >= 1:
            for bullet in player.bullets:
                '''When the edge of the bullet is perfectly within the hitbox of the enemy ''' 
                
                if bullet.y - bullet.radius < self.hitbox[1] + self.hitbox[3] and bullet.y + bullet.radius > self.hitbox[1]:
                    if bullet.x + bullet.radius > self.hitbox[0] and bullet.x - bullet.radius < self.hitbox [0] + self.hitbox[2]:
                        hitSound.play()
                        player.bullets.pop(player.bullets.index(bullet))
                        self.health -= 1                                         

    def ifCollide(self):
        if player.hitbox[1] < self.hitbox[1] + self.hitbox[3] and player.hitbox[1] + player.hitbox[3] > self.hitbox[1]:
            if player.hitbox[0] + player.hitbox[2] > self.hitbox[0] and player.hitbox[0] < self.hitbox[0] + self.hitbox[2]:
                player.collision = True
                
    def draw(self,win):

        if self.health >= 1:
            self.ifCollide()
            self.move()
            self.hit()
                              
            if self.walkCount >= len(self.walkLeft) * 3:
                self.walkCount = 0
                
            if self.facing == 1:
                win.blit(self.walkRight[self.walkCount //3],(self.x,self.y))
                self.walkCount += 1
            else:
                win.blit(self.walkLeft[self.walkCount //3],(self.x,self.y))
                self.walkCount += 1

            self.hitbox =(round(self.x + self.width * 0.1), round(self.y + self.width * 0.1), round(self.width * 0.8), round(self.height * 0.8))
            pygame.draw.rect(win,(250,0,0),(self.hitbox[0] - 10,self.hitbox[1]-10,self.hitbox[2] + 20,8)) 
            pygame.draw.rect(win,(0,128,0),(self.hitbox[0] - 10,self.hitbox[1]-10,round(self.health / self.fullHealth * (self.hitbox[2]+ 20)) ,8))    
##            pygame.draw.rect(win,(255,0,0),(self.hitbox),2)


class enemy2(object):
    '''
        This object class defines attributes of an enemy. 
        It moves in y direction, and it will only be moving up and down in a given boundary.
        Whenever it collides with player's hitbox, player's health point minus 1.
        Whenever its hitbox collides with player's bullet, its health point minus 1.
        When its healthpoint < 1, all of its functions terminate.
        Enemy sprites(L & R) is needed as initial data.
    '''

    def __init__(self,x,y,width,height,topEnd,bottomEnd,facing,vel,health,walkLeft,walkRight):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.topEnd = topEnd
        self.bottomEnd = bottomEnd
        self.walkCount = 0
        self.vel = vel
        '''facing = 1 or -1, determines the walking direction of the object'''
        self.facing = facing
        self.hitbox = (round(self.x + self.width * 0.1), round(self.y + self.width * 0.1), round(self.width * 0.8), round(self.height * 0.8))
        self.health = health
        self.isDefeated = False
        self.walkUp = walkLeft
        self.walkDown = walkRight

    def move(self):
        if self.y - self.vel <= self.topEnd:
            self.facing = 1
            self.walkCount = 0
            
        elif self.y + self.height + self.vel >= self.bottomEnd:
            self.facing = -1
            self.walkCount = 0
          
        self.y += self.vel * self.facing
    
    def hit(self):
        if self.health >= 1 and player.lifeLeft >= 1:
            for bullet in player.bullets:
                '''When the edge of the bullet is perfectly within the hitbox of the enemy '''                  
                if bullet.y - bullet.radius < self.hitbox[1] + self.hitbox[3] and bullet.y + bullet.radius > self.hitbox[1]:
                    if bullet.x + bullet.radius > self.hitbox[0] and bullet.x - bullet.radius < self.hitbox [0] + self.hitbox[2]:
                        hitSound.play()
                        player.bullets.pop(player.bullets.index(bullet))                                                                                   

    def ifCollide(self):
        if player.hitbox[0] + player.hitbox[2] > self.hitbox[0] and player.hitbox[0] < self.hitbox[0] + self.hitbox[2]:
            if player.hitbox[1] < self.hitbox[1] + self.hitbox[3] and player.hitbox[1] + player.hitbox[3] > self.hitbox[1]:
                player.collision = True
        
    def draw(self,win):
        if self.health >= 1:
            self.ifCollide()
            self.move()
            self.hit()
                              
            if self.walkCount >= len(self.walkUp) * 3:
                self.walkCount = 0
                
            if self.facing == 1:
                win.blit(self.walkDown[self.walkCount //3],(self.x,self.y))
                self.walkCount += 1
            else:
                win.blit(self.walkUp[self.walkCount //3],(self.x,self.y))
                self.walkCount += 1

            self.hitbox = (round(self.x + self.width * 0.1), round(self.y + self.width * 0.1), round(self.width * 0.8), round(self.height * 0.8))
##                pygame.draw.rect(win,(255,0,0),(self.hitbox),2)
        

class boss1(object):
    '''
        This object class defines attributes of an enemy (a boss). 
        It is at a stationary position, and is shooting in only one direction.
        Whenever it collides with player's hitbox, player's health point minus 1.
        Whenever its bullet collides with player's hitboxs, player's healthpoint minus 1.
        Whenever its hitbox collides with player's bullet, its health point minus 1.
        When its healthpoint < 1, all of its functions terminate.
        Enemy sprites and a image of bullet are needed as initial data.
    '''
    def __init__(self,x,y,width,height,facing,health,walkLeft,walkRight,bulletVel,bulletImage):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.walkCount = 0
        '''facing = 1 or -1, determines the facing direction of the object'''
        self.facing = facing
        self.hitbox =(round(self.x + self.width * 0.05), round(self.y + self.width * 0.05), round(self.width * 0.9), round(self.height * 0.9))
        self.health = health
        self.fullHealth = health
        self.bullets = []
        self.isDefeated = False
        self.shootLoop = 0
        self.walkLeft = walkLeft
        self.walkRight = walkRight
        self.bulletVel = bulletVel
        self.bulletImage = bulletImage
        
    def ifShot(self):
        for bullet in player.bullets:
            '''When the edge of the bullet is perfectly within the hitbox of the enemy '''                 
            if bullet.y - bullet.radius < self.hitbox[1] + self.hitbox[3] and bullet.y + bullet.radius > self.hitbox[1]:
                if bullet.x + bullet.radius > self.hitbox[0] and bullet.x - bullet.radius < self.hitbox [0] + self.hitbox[2]:
                    hitSound.play()
                    player.bullets.pop(player.bullets.index(bullet))
                    self.health -= 1                                                

    def ifCollide(self):
        if player.hitbox[1] < self.hitbox[1] + self.hitbox[3] and player.hitbox[1] + player.hitbox[3] > self.hitbox[1]:
            if player.hitbox[0] + player.hitbox[2] > self.hitbox[0] and player.hitbox[0] < self.hitbox[0] + self.hitbox[2]:
                player.collision = True

    def shoot(self):
        if self.shootLoop >= 1 and self.shootLoop < 30:
            self.shootLoop += 1
        else:
            self.shootLoop = 0
        
        if self.shootLoop == 0:
            self.bullets.append(projectile(round(self.x + self.width // 2),round(self.y + self.height - player.height//2),10,self.bulletVel * self.facing, self.bulletImage))
            self.shootLoop = 1

        for bullet in self.bullets:
            if (bullet.y - bullet.radius < player.hitbox[1] + player.hitbox[3] and bullet.y + bullet.radius > player.hitbox[1]) and (bullet.x + bullet.radius > player.hitbox[0] and bullet.x - bullet.radius < player.hitbox [0] + player.hitbox[2]):
                hitSound.play()
                player.collision = True
                self.bullets.pop(self.bullets.index(bullet))
                
            elif not (bullet.x <= winSize[0] - bullet.vel and bullet.x >= bullet.vel + 100):
                self.bullets.pop(self.bullets.index(bullet))                              
                
    def draw(self,win):
        if self.health >= 1:
            self.ifCollide()
            self.shoot()
            self.ifShot()
                                      
            if self.walkCount >= len(self.walkLeft) * 3:
                self.walkCount = 0
                
            if self.facing == 1:
                win.blit(self.walkRight[self.walkCount //3],(self.x,self.y))
                self.walkCount += 1
            else:
                win.blit(self.walkLeft[self.walkCount //3],(self.x,self.y))
                self.walkCount += 1
                

            for bullet in self.bullets:
                bullet.draw(win)
                
            self.hitbox =(round(self.x + self.width * 0.05), round(self.y + self.width * 0.05), round(self.width * 0.9), round(self.height * 0.9))
            pygame.draw.rect(win,(250,0,0),(self.hitbox[0] - 10,self.hitbox[1]-10,self.hitbox[2] + 20,8)) 
            pygame.draw.rect(win,(0,128,0),(self.hitbox[0] - 10,self.hitbox[1]-10,round(self.health / self.fullHealth * (self.hitbox[2]+ 20)) ,8))    
##            pygame.draw.rect(win,(255,0,0),(self.hitbox),2)

            
class boss2(object):
    '''
        This object class defines attributes of (a boss). 
        It accelerates from velocity zero to a given vel instance in x direction. 
        It will only be moving back and fore in a given boundary.
        Whenever it collides with player's hitbox, player's health point minus 1.
        Whenever its hitbox collides with player's bullet, its health point minus 1.
        When its healthpoint < 1, all of its functions terminate.
        Enemy sprites (L & R) are needed as intial data.
    '''
    def __init__(self,x,y,width,height,leftEnd,rightEnd,facing,health, acceleration, walkLeft,walkRight):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.leftEnd = leftEnd
        self.rightEnd = rightEnd
        self.walkCount = 0
        self.vel = 0
        '''facing = 1 or -1, determines the walking direction of the object'''
        self.facing = facing
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.health = health
        self.fullHealth = health
        self.acceleration = acceleration
        self.isDefeated = False
        self.walkLeft = walkLeft
        self.walkRight = walkRight        
        
    def move(self):
        if self.x + self.width + self.vel >= self.rightEnd:
            self.vel = 0
            self.facing = -1
            self.walkCount = 0
            
        elif self.x - self.vel <= self.leftEnd:
            self.facing = 1
            self.walkCount = 0
            self.vel = 0
            
        if self.vel < 14:
            self.vel += 1 * self.acceleration

        self.x += self.vel * self.facing

    def ifShot(self):
        for bullet in player.bullets:
            '''When the edge of the bullet is perfectly within the hitbox of the enemy '''                 
            if bullet.y - bullet.radius < self.hitbox[1] + self.hitbox[3] and bullet.y + bullet.radius > self.hitbox[1]:
                if bullet.x + bullet.radius > self.hitbox[0] and bullet.x - bullet.radius < self.hitbox [0] + self.hitbox[2]:
                    hitSound.play()
                    player.bullets.pop(player.bullets.index(bullet))
                    self.health -= 1
                                                


    def ifCollide(self):
        if player.hitbox[1] < self.hitbox[1] + self.hitbox[3] and player.hitbox[1] + player.hitbox[3] > self.hitbox[1]:
            if player.hitbox[0] + player.hitbox[2] > self.hitbox[0] and player.hitbox[0] < self.hitbox[0] + self.hitbox[2]:
                player.collision = True
        
    def draw(self,win):
        if self.health >= 1:
            self.ifCollide()
            self.move()
            self.ifShot()
                              
            if self.walkCount >= len(self.walkLeft) * 3:
                self.walkCount = 0
                
            if self.facing == 1:
                win.blit(self.walkRight[self.walkCount //3],(self.x,self.y))
                self.walkCount += 1
            else:
                win.blit(self.walkLeft[self.walkCount //3],(self.x,self.y))
                self.walkCount += 1

            self.hitbox =(round(self.x + self.width * 0.05), round(self.y + self.width * 0.05), round(self.width * 0.9), round(self.height * 0.9))
            pygame.draw.rect(win,(250,0,0),(self.hitbox[0] - 10,self.hitbox[1]-10,self.hitbox[2] + 20,8)) 
            pygame.draw.rect(win,(0,128,0),(self.hitbox[0] - 10,self.hitbox[1]-10,round(self.health / self.fullHealth * (self.hitbox[2]+ 20)) ,8))    
##            pygame.draw.rect(win,(255,0,0),(self.hitbox),2)

            
def setModeEasy():
    global player_health, enemy1_vel, enemy2A_vel,enemy2B_vel,enemy2C_vel,enemy2D_vel, bossA_bulletVel,bossB_health, bossB_acceleration
    player_health = 5
    enemy1_vel = 4
    enemy2A_vel = 10
    enemy2B_vel = 5
    enemy2C_vel = 12
    enemy2D_vel = 10
    bossA_bulletVel = 4
    bossB_health = 15
    bossB_acceleration = 1

def setModeHard():
    global player_health, enemy1_vel, enemy2A_vel,enemy2B_vel,enemy2C_vel, enemy2D_vel, bossA_bulletVel,bossB_health
    player_health = 3
    enemy1_vel = 8
    enemy2A_vel = 12
    enemy2B_vel = 6
    enemy2C_vel = 14
    enemy2D_vel = 14
    bossA_bulletVel = 6
    bossB_health = 30
    bossB_acceleration = 3

def defineFigures():
    '''Create objects (player and enemies) '''
    setModeEasy()
    global player, enemyA, enemyB, enemyC, enemyD, enemyE, enemyF, enemyG, enemyH, enemyI, bossA, bossB 
    player = mainPlayer(20, 400 -48, 25, 48, 5, player_health, spriteLists['PlayerL'], spriteLists['PlayerR'], featureDict['BulletA'])
    enemyA = enemy1(500, 400 - 52, 30 , 52, 100, 400, -1, enemy1_vel, 3, spriteLists['GlobinL'], spriteLists['GlobinR'])
    enemyB = enemy1(300 ,400 - 52, 30,52,100,590,1,enemy1_vel,3, spriteLists['GlobinL'], spriteLists['GlobinR'])
    enemyC = enemy2(350 ,200,57,86,60,400,-1,enemy2A_vel,10, spriteLists['MonsterL'], spriteLists['MonsterRotate'])
    enemyD = enemy2(450 ,200,57,86,60,400,1,enemy2A_vel,10, spriteLists['MonsterL'], spriteLists['MonsterRotate'])
    enemyE = enemy2(150 ,200,87,110,60,400,-1,enemy2B_vel,10, spriteLists['GhostL'], spriteLists['GhostR'])
    enemyF = enemy2(250 ,200,57,86,60,400,1,enemy2C_vel,10, spriteLists['MonsterL'], spriteLists['MonsterRotate'])
    enemyG = enemy2(350 ,200,87,110,60,400,-1,enemy2B_vel,10, spriteLists['GhostL'], spriteLists['GhostR'])
    enemyH = enemy2(450 ,200,57,86,60,400,1,enemy2C_vel,10, spriteLists['MonsterL'], spriteLists['MonsterRotate'])
    enemyI = enemy2(550 ,200,87,110,60,400,-1,enemy2D_vel,10, spriteLists['GhostL'], spriteLists['GhostR'])
    bossA = boss1(630 - 180, 400 - 200, 180, 200, -1, 20, spriteLists['BossAL'], spriteLists['BossAR'], bossA_bulletVel, featureDict['BulletB'])
    bossB = boss2(630 - 72,400 - 80, 72, 80, 100, 630 - 72, -1, bossB_health, bossB_acceleration, spriteLists['BossBL'], spriteLists['BossBR'])

def __init__figures():
    '''Initialise objects (player and enemies)'''
    player.__init__(20, 400 -48, 25, 48, 5, player_health, spriteLists['PlayerL'], spriteLists['PlayerR'], featureDict['BulletA'])
    enemyA.__init__(500, 400 - 52, 30, 52, 100, 400, -1, enemy1_vel, 3,spriteLists['GlobinL'], spriteLists['GlobinR'])
    enemyB.__init__(300 ,400 - 52, 30, 52,100,590,1,enemy1_vel,3, spriteLists['GlobinL'], spriteLists['GlobinR'])
    enemyC.__init__(350 , 200, 57, 86, 60, 400,-1,enemy2A_vel,10, spriteLists['MonsterL'], spriteLists['MonsterRotate'])
    enemyD.__init__(450 , 200, 57, 86, 60, 400,1,enemy2A_vel,10, spriteLists['MonsterL'], spriteLists['MonsterRotate'])
    enemyE.__init__(150 , 200, 87, 110, 60, 400,-1,enemy2B_vel,10, spriteLists['GhostL'], spriteLists['GhostR'])
    enemyF.__init__(250 , 200, 57, 86, 60, 400,1,enemy2C_vel,10, spriteLists['MonsterL'], spriteLists['MonsterRotate'])
    enemyG.__init__(350 , 200, 87, 110, 60, 400,-1,enemy2B_vel,10, spriteLists['GhostL'], spriteLists['GhostR'])
    enemyH.__init__(450 , 200, 57, 86, 60, 400,1,enemy2C_vel,10, spriteLists['MonsterL'], spriteLists['MonsterRotate'])
    enemyI.__init__(550 , 200, 87, 110, 60, 400,-1,enemy2D_vel,10, spriteLists['GhostL'], spriteLists['GhostR'])
    bossA.__init__(630 - 180, 400 - 200, 180, 200, -1, 20, spriteLists['BossAL'], spriteLists['BossAR'],bossA_bulletVel, featureDict['BulletB'])
    bossB.__init__(630 - 72,400 - 80, 72, 80, 100, 630 - 72, -1, bossB_health, bossB_acceleration, spriteLists['BossBL'], spriteLists['BossBR'])
  
def drawGameWindow():
    ''' Excecute all draw procedures of the objects(player, enemies & bullets)'''
    global roundNo,mode,isLost,isWin,isWisdomWin,isPerfectWin,isPeaceWin
                        
    '''Allow player to choose modes (easy or hard) at the beginning of the game.'''
    if mode == 0:
        win.blit(bgDict['ModeChoose'],(0,0))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            mode = 1
            setModeEasy()
            __init__figures()
        elif keys[pygame.K_h]:
            mode = 2
            setModeHard()
            __init__figures()
    
    elif not isWin and not isLost:
        '''Check the round number to consider which enemies and background image to draw.'''
        if roundNo == 1:
            win.blit(bgDict['BgRound1'],(0,0))
            player.draw(win)
            enemyA.draw(win)
            enemyB.draw(win)
            enemyC.draw(win)
            enemyD.draw(win)

        elif roundNo == 2:
            win.blit(bgDict['BgRound2'],(0,0))
            player.draw(win)
            enemyE.draw(win)
            enemyF.draw(win)
            enemyG.draw(win)
            enemyH.draw(win)
            enemyI.draw(win)

        elif roundNo == 3:
            win.blit(bgDict['BgRound3'],(0,0))
            player.draw(win)
            bossA.draw(win)
            if bossA.health < 1:
                bossB.draw(win)

        elif roundNo == 4:
            if enemyA.health > 0 and enemyB.health > 0:
                isPeaceWin = True

            if bossB.health > 0: 
                isWisdomWin = True
                
            if player.lifeLeft == player.fullHealth:
                isPerfectWin = True

            if not (isPeaceWin or isWisdomWin or isPerfectWin):
                isWin = True

        if isPeaceWin or isWisdomWin or isPerfectWin:
            if roundNo == 4:
                if isPeaceWin:
                    win.blit(bgDict['PeaceWinPath'],(0,0))
                    player.draw(win)
                else:
                    if isWisdomWin:
                        roundNo += 1
                    else:
                        roundNo += 2

            if roundNo == 5:
                if isWisdomWin:
                    if mode == 1:
                        win.blit(bgDict['WisdomWinPath'],(0,0))
                    else:
                        win.blit(bgDict['WisdomWinPathHard'],(0,0))
                    player.draw(win)
                else:
                    if isPerfectWin:
                        roundNo += 1
                    else:
                        isWin = True

            if roundNo == 6:
                if isPerfectWin:
                    if mode == 1:
                        win.blit(bgDict['PerfectWinPath'],(0,0))
                    else:
                        win.blit(bgDict['PerfectWinPathHard'],(0,0))
                    player.draw(win)
                else:
                    isWin = True

            if roundNo == 7:
                isWin = True

        if player.x + player.vel > winSize[0]:
            roundNo += 1
            player.x = player.rebornLoc[0]
            player.bullets = []

        if player.lifeLeft < 1:
            isLost = True

        win.blit(featureDict['heart'],(25,35))
        lifeLeftText = font1.render(' X '+ str(player.lifeLeft),1,(255,250,250))
        win.blit(lifeLeftText,(45,35))

    else:
        if isLost:
            if roundNo == 1:
                win.blit(bgDict['BgRound1Lost'],(0,0))
            if roundNo == 2:
                win.blit(bgDict['BgRound2Lost'],(0,0))
            if roundNo == 3:
                win.blit(bgDict['BgRound3Lost'],(0,0))
        else:
            if mode == 1:
                if isPerfectWin:
                    win.blit(bgDict['PerfectWin'],(0,0))
                elif isWisdomWin:
                    win.blit(bgDict['WisdomWin'],(0,0))
                elif isPeaceWin:
                    win.blit(bgDict['PeaceWin'],(0,0))
                else:
                    win.blit(bgDict['Win'],(0,0))
                    
            else:
                if isPerfectWin:
                    win.blit(bgDict['PerfectWinHard'],(0,0))
                elif isWisdomWin:
                    win.blit(bgDict['WisdomWinHard'],(0,0))
                elif isPeaceWin:
                    win.blit(bgDict['PeaceWin'],(0,0))
                else:
                    win.blit(bgDict['WinHard'],(0,0))
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            '''Initalise all global variables to restart the game (Back to the mode choosing stage.).'''
            mode = 0
            roundNo = 1
            isLost = False
            isWin = False
            isWisdomWin = False
            isPerfectWin = False
            isPeaceWin = False


##mainloop
'''Load all the images needed'''
bgDict = loadImageDict('image/backgrounds')
featureDict = loadImageDict('image/features')
spriteLists = loadImageListInDict('image/sprites')

'''Load all the sound tracks needed'''
bulletSound = pygame.mixer.Sound(os.path.join('audios','bullet.wav'))
hitSound = pygame.mixer.Sound(os.path.join('audios','hit.wav'))
music = pygame.mixer.music.load(os.path.join('audios','music.mp3'))
pygame.mixer.music.play(-1)
font1 = pygame.font.SysFont('comicsans',32,True,True)

clock = pygame.time.Clock()
roundNo = 1
mode = 0
isLost = False
isWin = False
isWisdomWin = False
isPerfectWin = False
isPeaceWin = False
run = True
defineFigures()

while run:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    drawGameWindow()
    pygame.display.update()
    
pygame.quit()
