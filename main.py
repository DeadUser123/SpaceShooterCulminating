# Name: Kevin Xia
# Date: July 18 - 23
# Purpose: To create a space shooter game in pygame

import pygame, sys, random
from pygame.locals import QUIT

# setting things up
pygame.init()
size = (640, 480)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Space Shooter')

background = pygame.Surface(size).convert()
background.fill((0, 0, 40))

# fonts
arialFont = pygame.font.Font("arialnarrow.ttf", 24)
lbFont = pygame.font.Font("PixeloidSans.ttf", 16)

# sounds
pew = pygame.mixer.Sound("pew.mp3")
boom = pygame.mixer.Sound("boom.mp3")


# screen images
start_screen1 = pygame.transform.scale(pygame.image.load("startscreen.png"), (640, 480))
start_screen2 = pygame.transform.scale(pygame.image.load("startscreenhover.png"), (640, 480))
getNameScreen = pygame.transform.scale(pygame.image.load("getNameScreen.png"), (640, 480))
gameOverScreen1 = pygame.transform.scale(pygame.image.load("gameOverScreen1.png"), (640, 480))
gameOverScreen2 = pygame.transform.scale(pygame.image.load("gameOverScreen2.png"), (640, 480))

# other images
player = pygame.transform.scale(pygame.image.load("player.png"), (40, 40))
enemy = pygame.transform.scale(pygame.image.load("enemy.png"), (30, 30))
bullet = pygame.transform.scale(pygame.image.load("playerBullet.png"), (20, 20))
enemybullet = pygame.transform.scale(pygame.image.load("enemyBullet.png"), (10, 10))

clock = pygame.time.Clock()

def setUpEnemyList():
    enemylist = []
    for _ in range(20): # setting up the enemylist (20 enemies first)
        # enemies spawn at random coordinates at the top half of the screen wtih a random direction to go to (left or right) and a firing cooldown (has a grace period of 2 seconds)
        enemylist.append([random.randint(0, 640), random.randint(0, 240), random.randint(0, 1) * 2 - 1, random.randint(60, 120)])
    return enemylist


def startLoop():
    screen.blit(background, (0, 0))
    screen.blit(start_screen1, (-1, -1)) # prevent weird white line on the left that appeared during testing
    pygame.display.flip()
    
    # Getting the highest score
    try:
        file = open("Top_Scores.txt", "r")
        topScore = file.readline().split(" - ")[0]
    except: # if the file doesn't exist, set up the top scores files in the correct format
        file = open("Top_Scores.txt", "w")
        topScore = 0
        file.write('\n'.join([r"0 - N/A"] * 10))
    file.close()
    topScoreText = arialFont.render(f"Top Score: {topScore}", False, (255, 255, 255))
    
    # Getting the highest time
    try:
        file = open("Top_Times.txt", "r")
        topTime = file.readline().split(" - ")[0]
    except: # file doesn't exist, create it
        file = open("Top_Times.txt", "w")
        topTime = "0:00"
        file.write("\n".join([r"0:00 - N/A"] * 10)) # sets up the top time file in the correct format
    file.close()
    topTimeText = arialFont.render(f"Top Time: {topTime}", False, (255, 255, 255))
    
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # if the mouse clicks the button
                if 210 < pygame.mouse.get_pos()[0] < 430 and 354 < pygame.mouse.get_pos()[1] < 454:
                    return # exits the function to move on
        screen.blit(background, (0, 0))
        # check if mouse is overing over the button
        if 210 < pygame.mouse.get_pos()[0] < 430 and 354 < pygame.mouse.get_pos()[1] < 454:
            screen.blit(start_screen2, (-1, -1))
        else:
            screen.blit(start_screen1, (-1, -1))
            
        # display the top score/time
        screen.blit(topScoreText, (0, 0))
        screen.blit(topTimeText, (0, 24))
        pygame.display.flip()


def gameLoop():
    # setting variables up
    global background
    playerTime = 0
    playerScore = 0
    playerx = 640 // 2
    playery = 380
    enemylist = setUpEnemyList()
    bulletList = []
    enemyBulletList = []
    bulletCooldown = 0
    
    # to reset the enemy bullet image each time to prevent scaling on an already scaled image
    enemybullet = pygame.transform.scale(pygame.image.load("enemyBullet.png"), (10, 10))
    
    background.fill((0, 0, 40))
    
    while True:
        clock.tick(30)
        playerTime += 1 # to gradually increase the time
        
        if playerScore % 1000 == 0: # gradually increases the size of the bullets to make it harder to dodge
            enemybullet = pygame.image.load("enemyBullet.png") # resets enemybullet to make size scaling more accurate
            enemybullet = pygame.transform.scale(enemybullet, (min(10 + playerScore // 500, 50), min(10 + playerScore // 500, 50))) # prevents bullets form being too large
        
        # to allow player to hit X button
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
        # Handling player movement
        pressed = pygame.key.get_pressed() # allows player to hold the keys down rather than rapidly pressing them
        if pressed[pygame.K_LEFT] and playerx - 5 > 0: # prevents any part of the player image from going off screen
            playerx -= 10
        elif pressed[pygame.K_RIGHT] and playerx + 5 < 600:
            playerx += 10
        elif pressed[pygame.K_UP] and playery - 5 > 0:
            playery -= 10
        elif pressed[pygame.K_DOWN] and playery + 5 < 440:
            playery += 10
        
        # shooting bullet code
        if bulletCooldown > 0: # prevents spamming bullets
            bulletCooldown -= 1
        elif pressed[pygame.K_SPACE]: # allows player to just hold space to shoot
            bulletCooldown = 15
            bulletList.append((playerx + 10, playery + 20)) # allows multiple bullets
            pew.play()
        
        # handling enemy movement
        for enemyPos in enemylist:
            enemyPos[0] += enemyPos[2] * 3 # multiply movement speed by direction
            if enemyPos[0] > 610 or enemyPos[0] < 0:
                enemyPos[2] *= -1 # reverse direction if hit the edge of the screen
                enemyPos[0] = 610 if enemyPos[0] > 610 else 0 # prevent enemies from getting stuck
            if enemyPos[3] == 0: # resetting the enemy's bullet cooldown
                enemyPos[3] = random.randint(15, 120) # no need for 2 seconds of delay
                # enemy bullets appear centered on the enemies regardless of their current size
                enemyBulletList.append([enemyPos[0] + 15 - min(10 + playerScore // 1000 * 1000 // 500, 50) // 2, enemyPos[1] + 15 - min(10 + playerScore // 1000 * 1000 // 500, 50) // 2])
            else:
                enemyPos[3] -= 1 # lower the cooldown

        # spawn new enemies at the sides
        while len(enemylist) < 20 + playerTime // 300: # gradually spawns one more enemy every 10 seconds
            enemylist.append([random.randint(0,1) * 640, random.randint(0, 240), random.randint(0, 1) * 2 - 1, random.randint(60, 120)])
            
        # handling bullet movement
        idx = 0
        while idx < len(bulletList):
            if bulletList[idx][1] < 0: # prevent unneeded calculations of off-screen bullets
                bulletList.pop(idx)
            else:
                bulletList[idx] = (bulletList[idx][0], bulletList[idx][1] - 10)
                idx += 1

        # handling enemy bullet movement
        idx = 0
        while idx < len(enemyBulletList):
            if enemyBulletList[idx][1] > 480: # prevent unneeded calculations of off-screen bullets
                enemyBulletList.pop(idx)
            else:
                enemyBulletList[idx][1] += 10 + playerScore / 5000 # gradually increases the enemy bullet speed the more score the player gets
                idx += 1

        # displaying and handling collision detection
        enemyRects = []
        bulletRects = []
        
        screen.blit(background, (0, 0))
        screen.blit(player, (playerx, playery))
        playerRect = player.get_rect(topleft = (playerx, playery))
        # creating bullet rects for collision detection
        for bulletPos in bulletList: 
            screen.blit(bullet, bulletPos)
            bulletRects.append(bullet.get_rect(topleft = bulletPos))
            
        # detecting collisions with enemies
        for idx in range(len(enemylist)):
            enemyPos = enemylist[idx]
            enemyRects.append(enemy.get_rect(topleft = (enemyPos[0], enemyPos[1])))
            if enemyRects[-1].colliderect(playerRect): # if enemy collides with the player
                boom.play() # boom sound effect
                return (playerScore, playerTime) # game over, exits function
            for rect in bulletRects: # collision with player bullets
                if enemyRects[-1].colliderect(rect): # make the enemy respawn
                    enemylist[idx] = [random.randint(0,1) * 640, random.randint(0, 240), random.randint(0, 1) * 2 - 1, random.randint(5, 120)]
                    playerScore += 100 # add 100 to the playerScore
                    break
            else:
                screen.blit(enemy, (enemyPos[0], enemyPos[1]))

        # detecting collisions with enemy bullets
        for enemyBulletPos in enemyBulletList:
            enemybulletrect = enemybullet.get_rect(topleft = enemyBulletPos)
            if playerRect.colliderect(enemybulletrect): # player collides with enemy bullet
                boom.play()
                return (playerScore, playerTime) # exits the function to transistion to game over screen
            screen.blit(enemybullet, enemyBulletPos)

        # display the player's score
        scoreTxt = arialFont.render(f"Score: {playerScore}", False, (255, 255, 255))
        screen.blit(scoreTxt, (0, 0))
        
        # displays the player's time
        timeTxt = arialFont.render(f"{playerTime // 30} seconds", False, (255, 255, 255))
        screen.blit(timeTxt, (0, 456))
        pygame.display.flip()

def getPlayerName(): # get player score if they make it on the leaderboard
    name = r""
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and len(name) > 0:
                    name = name[:-1] # delte a character if backspace si pressed
                elif event.key == pygame.K_RETURN:
                    if name == "" or name.replace(" ", "") == "":
                        return r"N/A" # puts name as N/A if nothing was entered
                    else:
                        return name.strip() # prevents trailing whitespace from confusing the program when detecting if the line is too long
                elif len(name) < 20 and (event.unicode.isalnum() or event.key == pygame.K_SPACE): # prevents name from being too long or having invalid characters
                    name += event.unicode
        screen.blit(background, (0, 0))
        screen.blit(getNameScreen, (0, 0))
        nameLabel = arialFont.render(name, False, (255, 255, 255))
        screen.blit(nameLabel, (160, 235))
        pygame.display.flip()
       
def updateTopScores(playerName, playerScore):
    # reading the top scores
    try:
        file = open("Top_Scores.txt", "r")
        topScores = file.readlines()
    except:
        file = open("Top_Times.txt", "w") # if the file got deleted, rewrite the entire thing and pass in the default version as the topScores leaderboard
        topScores = ["0 - N/A"] * 10
        file.write("\n".join(topScores))
    file.close()
    
    # updating the top scores
    unplacedScore = playerScore
    name = None
    for idx in range(len(topScores)):
        if int(topScores[idx].split(" - ")[0]) < unplacedScore:
            placedScore = topScores[idx]
            if name == None:
                if playerName == None: # if we don't know the player's name
                    playerName = getPlayerName()
                    name = playerName
                else: # if we already know it
                    name = playerName
            # updates the current place
            topScores[idx] = str(unplacedScore) + " - " + name + "\n"
            # now the placed score is unplaced, variables are updated to reflect that
            unplacedScore = int(placedScore.split(" - ")[0])
            name = placedScore.split()[-1]
            
    topScores[-1] = topScores[-1].strip() # prevents an empty line from being created at the end of the file
    
    # updating the top scores file
    file = open("Top_Scores.txt", "w")
    file.write("".join(topScores))
    file.close()
    
    return topScores, playerName

def updateTopTimes(playerName, playerTime):
    # reading the top times file
    try:
        file = open("Top_Times.txt", "r")
        topTimes = file.readlines()
    except: # if the file got deleted, rewrite the entire thing and pass in the default version as the topTimes leaderboard
        file = open("Top_Times.txt", "w")
        topTimes = ["0:00 - N/A"] * 10
        file.write("\n".join(topTimes))
    file.close()
    
    # updating the top times
    unplacedTime = playerTime
    unplacedTime //= 30 # as playerTime was stored as how many frames they lasted and not in seconds
    name = None
    for idx in range(len(topTimes)):
        placedTime = topTimes[idx].split("-") # the current place on the leaderboard that we are checking
        minutes, seconds = placedTime[0].split(":")
        if int(minutes * 60) + int(seconds) < unplacedTime:
            tempVar = topTimes[idx] # to store things
            if name == None: # if we don't have a name that coresponds with the player
                if playerName == None: # if we don't know the player's name
                    playerName = getPlayerName()
                    name = playerName
                else: # if we already know it, no need to ask again
                    name = playerName
            # updates the current place, stored as minutes:seconds - name as it looks better
            topTimes[idx] = f"{unplacedTime // 60}:{0 if unplacedTime % 60 < 10 else ''}{unplacedTime % 60} - {name}\n"
            # now the placed Time is unplaced, updates the variables to reflect that
            unplacedTime = tempVar.split(" - ")[0].split(":")
            unplacedTime = int(unplacedTime[0]) * 60 + int(unplacedTime[-1])
            name = tempVar.split(" - ")[-1].strip()
    
    topTimes[-1] = topTimes[-1].strip() # prevents an empty line at the end of the file
    
    # updating the top times file
    file = open("Top_Times.txt", "w")
    file.write("".join(topTimes))
    file.close()
    
    return topTimes

def gameOver(playerScore, playerTime):
    playerName = None
    
    topScores, playerName = updateTopScores(playerName, playerScore)
    
    topTimes = updateTopTimes(playerName, playerTime)
    
    # setting up the "Your score/time is..." text
    scoreText = arialFont.render(f"Your score is {playerScore}", False, (255, 255, 255))
    timeText = arialFont.render(f"Your time is {playerTime // (30 * 60)}:{0 if playerTime // 30 % 60 < 10 else ''}{playerTime // 30 % 60}", False, (255, 255, 255))
    
    screen.blit(background, (0, 0))
    # add TOP SCORES/TIMES: on each respective leadeboard
    topScores.insert(0, "TOP SCORES:")
    topTimes.insert(0, "TOP TIMES:")
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 210 < pygame.mouse.get_pos()[0] < 430 and 290 < pygame.mouse.get_pos()[1] < 390:
                    return # exits to start the game again
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return # allows player to hit enter or space to play again for convenience
                
        # highlights the button when mouse hovers over it
        if 210 < pygame.mouse.get_pos()[0] < 430 and 290 < pygame.mouse.get_pos()[1] < 390:
            screen.blit(gameOverScreen2, (0, 0))
        else:
            screen.blit(gameOverScreen1, (0, 0))
            
        # display the top scores
        for i in range(len(topScores)):
            # makes first gold, second silver, third bronze and the rest white
            text_color = (255, 210, 0) if i == 1 else (216, 216, 216) if i == 2 else (205, 127, 50) if i == 3 else (255, 255, 255)
            if len(topScores[i].strip()) <= 16:
                screen.blit(lbFont.render(topScores[i].strip(), False, text_color), (0, i * 24))
            else: # prevent top scores text from overflowing with minimum loss of information
                screen.blit(lbFont.render(topScores[i].strip()[:13] + "...", False, text_color), (0, i * 24))
        
        # display the top times
        for i in range(len(topTimes)):
            # makes first gold, second silver, third bronze and the rest white
            text_color = (255, 210, 0) if i == 1 else (216, 216, 216) if i == 2 else (205, 127, 50) if i == 3 else (255, 255, 255)
            if len(topTimes[i].strip()) <= 16:
                screen.blit(lbFont.render(topTimes[i].strip(), False, text_color), (480, i * 24))
            else: # prevent top times text from overflowing with minimum loss of information
                screen.blit(lbFont.render(topTimes[i].strip()[:13] + "...", False, text_color), (480, i * 24))
        
        # displays the "Your score/time is..." text
        screen.blit(scoreText, (210, 160))
        screen.blit(timeText, (210, 184))
        
        pygame.display.flip()

# MAIN LOOP
startLoop() # shows the start screen, waits until player hits play
while True:
    score, time = gameLoop() # runs the game
    gameOver(score, time) # shows the game over screen, waits until player hits play again

# https://replit.com/@KX-08WC-755849/SpaceShooterCulminating?v=1