# Import the pygame module
import pygame
import pygame_menu
import random
import math

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_w,
    K_s,
    K_q,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)

pygame.init()

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

#Player vars
PLAYER_AND_SCORE_AREA_GAP = 50
PLAYER_SIZE = (20, 100)
PLAYER_SPEED = 6
PLAYER_COLOR = (167,74,68)

#Ball vars
BALL_SIZE = (12,12)
BALL_COLOR = (244,120,71)
BALL_MAX_VELOCITY = 15
BALL_MIN_VELOCITY = 5
BALL_BOUNCES_TO_MAX_VELOCITY = 30

#Background
BG_COLOR = (26,31,59)
#Scoring Area
SCORE_AREA_SIZE = (20, SCREEN_HEIGHT)
SCORE_AREA_COLOR = (83,54,75)

#Scores
PLAYER1_SCORE = 0
PLAYER2_SCORE = 0
PLAYER1_SCORED = pygame.USEREVENT+1
PLAYER2_SCORED = pygame.USEREVENT+2
PLAYER1_SCORE_SURFACE = None
PLAYER2_SCORE_SURFACE = None
PLAYER1_SCORE_COORD = [0,0]
PLAYER2_SCORE_COORD = [0,0]
SCORE_COLOR = (244,120,71)
SCORE_FONT_SIZE = 35
SCORE_OFFSET_FROM_TOP = 50

pygame.font.init()
font = pygame.font.SysFont(None, SCORE_FONT_SIZE)

# Initialize pygame
pygame.init()

# Set up the clock for a decent framerate
clock = pygame.time.Clock()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Define a player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(pygame.sprite.Sprite):
    defCoordinates = (0,0)
    def __init__(self, leftSide):
        super(Player, self).__init__()
        self.surf = pygame.Surface(PLAYER_SIZE)
        self.surf.fill(PLAYER_COLOR)
        self.leftSide = leftSide
        if leftSide:
            self.defCoordinates = (SCORE_AREA_SIZE[0] + PLAYER_AND_SCORE_AREA_GAP, SCREEN_HEIGHT/2 - PLAYER_SIZE[1]/2)
            self.KEY_UP = K_w
            self.KEY_DOWN = K_s
        else:
            self.defCoordinates =(SCREEN_WIDTH - SCORE_AREA_SIZE[0] - PLAYER_AND_SCORE_AREA_GAP - PLAYER_SIZE[0], SCREEN_HEIGHT/2 - PLAYER_SIZE[1]/2)
            self.KEY_UP = K_UP
            self.KEY_DOWN = K_DOWN

        self.rect = self.surf.get_rect()

    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[self.KEY_UP]:
            self.rect.move_ip(0, -PLAYER_SPEED)
        if pressed_keys[self.KEY_DOWN]:
            self.rect.move_ip(0, PLAYER_SPEED)

        self.checkWallColision()

    def checkWallColision(self):
        # Keep player on the screen
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


    def moveToDefaultCoordinates(self):
        self.rect.left = self.defCoordinates[0]
        self.rect.top = self.defCoordinates[1]

class Enemy(Player):
    def __init__(self, leftside, ballObj):
        super(Enemy, self).__init__(leftside)
        self.ballObj = ballObj
        self.leftside = leftside

    def update(self, pressed_keys):
        ballXVeloc = self.ballObj.direction[0]
        distToBall = math.fabs(self.rect.left - self.ballObj.rect.left)
        ballAproaching = (ballXVeloc < 0 and self.leftside) or (ballXVeloc > 0 and (not self.leftside))
        if(ballAproaching and distToBall < SCREEN_WIDTH/2):
            #ball center coordinate on Y axis
            point = (self.ballObj.rect.top + BALL_SIZE[1]/2)
        else:
            #screen midle
            point = SCREEN_HEIGHT/2

        #move to point on y axis
        distToBallOnY = (self.rect.top + PLAYER_SIZE[1]/2) - point
        if math.fabs(distToBallOnY) > PLAYER_SIZE[1]/3:
            if (distToBallOnY > 0):
                self.rect.move_ip(0, -PLAYER_SPEED)
            else:
                self.rect.move_ip(0, PLAYER_SPEED)

        self.checkWallColision()

# Define a ball object by extending pygame.sprite.Sprite
class Ball(pygame.sprite.Sprite):
    defCoordinates = (0,0)
    direction = [0, 0]

    def __init__(self):
        super(Ball, self).__init__()
        self.surf = pygame.Surface(BALL_SIZE)
        self.surf.fill(BALL_COLOR)

        self.defCoordinates = (SCREEN_WIDTH/2-BALL_SIZE[0]/2, SCREEN_HEIGHT/2-BALL_SIZE[1]/2)
        self.rect = self.surf.get_rect()

    # Move the sprite based on user keypresses
    def update(self):
        
        self.rect.move_ip(self.speed * self.direction[0], self.speed * self.direction[1])

        # Keep ball on the screen
        if self.rect.top <= 0:
            self.rect.top = 0
            self.direction[1] = math.fabs(self.direction[1])
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.direction[1] = -math.fabs(self.direction[1])

    def reserve(self, toPlayerSide):
        self.moveToDefaultCoordinates()
        self.bounces = 0
        self.updateSpeed()

        if(toPlayerSide):
            self.direction[0] = -1
        else:
            self.direction[0] = 1
        self.direction[1] = 0

    def moveToDefaultCoordinates(self):
        self.rect.left = self.defCoordinates[0]
        self.rect.top = self.defCoordinates[1]

    def updateSpeed(self):
        percentage = min(self.bounces/BALL_BOUNCES_TO_MAX_VELOCITY, 1)
        self.speed = BALL_MIN_VELOCITY + (BALL_MAX_VELOCITY-BALL_MIN_VELOCITY)*percentage

    def collided(self, colidedWith):
        left = self.rect.left < SCREEN_WIDTH/2
        for object in colidedWith:
            if isinstance(object, Ball):
                continue
            elif isinstance(object, Player):
                self.bounces += 1
                self.updateSpeed()
                self.direction[0] = (1 if left else -1)
                self.setRandVarticalSpeed()

                if left:
                    self.rect.left = colidedWith[0].rect.right
                else:
                    self.rect.right = colidedWith[0].rect.left
            else:
                if left:
                    pygame.event.post(pygame.event.Event(PLAYER2_SCORED))
                else:
                    pygame.event.post(pygame.event.Event(PLAYER1_SCORED))


    def setRandVarticalSpeed(self):
        self.direction[1] = random.random() * (-1 if random.random() < 0.5 else 1)

class ScoreArea(pygame.sprite.Sprite):
    def __init__(self, leftSide):
        super(ScoreArea, self).__init__()
        self.surf = pygame.Surface(SCORE_AREA_SIZE)
        self.surf.fill(SCORE_AREA_COLOR)

        self.rect = self.surf.get_rect()
        if leftSide:
            self.rect.left = 0
        else:
            self.rect.right = SCREEN_WIDTH
        self.rect.top = 0

# Variable to keep the main loop running
running = True
playing = False
pause = False

def placeAll(ballToLeft):
    for pl in players:
        pl.moveToDefaultCoordinates()
    ball.reserve(ballToLeft)

def drawScores():
    global PLAYER1_SCORE_SURFACE
    PLAYER1_SCORE_SURFACE = font.render(str(PLAYER1_SCORE), True, SCORE_COLOR)
    PLAYER1_SCORE_COORD[0] = SCREEN_WIDTH/3
    PLAYER1_SCORE_COORD[1] = SCORE_OFFSET_FROM_TOP

    global PLAYER2_SCORE_SURFACE
    PLAYER2_SCORE_SURFACE = font.render(str(PLAYER2_SCORE), True, SCORE_COLOR)
    PLAYER2_SCORE_COORD[0] = SCREEN_WIDTH/3*2
    PLAYER2_SCORE_COORD[1] = SCORE_OFFSET_FROM_TOP

def initGame(singlePlayer):
    global playing
    playing = True
    global pause
    pause = False

    # Instantiate player
    global ball
    ball = Ball()
    player = Player(True)
    if singlePlayer:
        player2 = Enemy(False, ball)
    else :
        player2 = Player(False)

    leftScoreArea = ScoreArea(True)
    rightScoreArea = ScoreArea(False)

    global players
    players = pygame.sprite.Group()
    players.add(player)
    players.add(player2)

    global all_sprites
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(player2)
    all_sprites.add(ball)
    all_sprites.add(leftScoreArea)
    all_sprites.add(rightScoreArea)

    global PLAYER1_SCORE
    global PLAYER2_SCORE
    PLAYER1_SCORE = 0
    PLAYER2_SCORE = 0
    drawScores()
    placeAll(1)
    menu.disable()

def pauseGame():
    if playing:
        global pause
        pause = not pause

def returnToMenu():
    playing = False
    menu.enable()
    menu.mainloop(screen)



menu = pygame_menu.Menu('Ping-Pong', SCREEN_WIDTH, SCREEN_HEIGHT, theme=pygame_menu.themes.THEME_DARK)
control_menu = pygame_menu.Menu('Ping-Pong', SCREEN_WIDTH, SCREEN_HEIGHT, theme=pygame_menu.themes.THEME_DARK, columns=3, rows=(2,4,3))

menu.add.button('Single player', initGame, 1)
menu.add.button('Two player', initGame, 0)
menu.add.button("Controls", control_menu)
menu.add.button('Quit', pygame_menu.events.EXIT)

control_menu.add.label("Space - pause\nq - return to menu", "pauseControl")
control_menu.add.label("Player 1\nw - up")
control_menu.add.label("s - down", margin=(5,50))
control_menu.add.button("Back", pygame_menu.events.BACK)
control_menu.add.label("Player 2\nArrowkey up - up\nArrowkey down - down", "controlMenu")


returnToMenu()

# Main loop
while running:
    # for loop through the event queue
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_q:
                returnToMenu()
            if event.key == K_SPACE:
                pauseGame()
        elif event.type == PLAYER1_SCORED:
            PLAYER1_SCORE += 1
            drawScores()
            placeAll(1)
        elif event.type == PLAYER2_SCORED:
            PLAYER2_SCORE += 1
            drawScores()
            placeAll(0)
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            running = False

    if playing:
        if not pause:
            # Get all the keys currently pressed
            pressed_keys = pygame.key.get_pressed()

            # Update
            for pl in players:
               pl.update(pressed_keys)
            ball.update()

            # Check collision
            collidedList = pygame.sprite.spritecollide(ball, all_sprites, False)
            if len(collidedList) > 0:
                ball.collided(collidedList)

        # Fill the background
        screen.fill(BG_COLOR)

        # Draw the player on the screen
        for sprite in all_sprites:
            screen.blit(sprite.surf, sprite.rect)

        #Draw score on the screen
        screen.blit(PLAYER1_SCORE_SURFACE, PLAYER1_SCORE_COORD)
        screen.blit(PLAYER2_SCORE_SURFACE, PLAYER2_SCORE_COORD)

        # Update the display
        pygame.display.flip()

    # Ensure program maintains a rate of 30 frames per second
    clock.tick(60)