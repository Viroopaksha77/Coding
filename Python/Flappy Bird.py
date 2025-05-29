import pygame
import sys
import random
import os

# initialize pygame
pygame.init()

# high score file 
highscorepath = "Repositories/highscore2.txt"

# function to load high score
def load_high_score():
    try:
        if os.path.exists(highscorepath):
            with open(highscorepath, 'r') as file:
                return int(file.read().strip())
        return 0
    except:
        return 0

# function to save high score
def save_high_score(score):
    # ensure directory exists
    directory = os.path.dirname(highscorepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(highscorepath, 'w') as file:
        file.write(str(score))

# game constants
width = 400
height = 600
gravity = 0.25
jumpforce = -5
pipegap = 160
pipefrequency = 1000  # milliseconds
groundheight = 100
initialspeed = 4  # initial game speed
speedincrease = 0.2  # how much to increase speed per point
maxspeed = 10  # maximum game speed

# colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 128, 0)
skyblue = (135, 206, 235)
yellow = (255, 255, 0)
red = (255, 0, 0)

# set up the display
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 30)
big_font = pygame.font.SysFont('Arial', 50)

# bird class
class Bird:
    def __init__(self):
        self.x = 100
        self.y = height // 2
        self.velocity = 0
        self.width = 40
        self.height = 30
        self.alive = True
    
    def jump(self):
        self.velocity = jumpforce
    
    def move(self):
        # apply gravity
        self.velocity += gravity
        self.y += self.velocity
        
        # check boundaries
        if self.y <= 0:
            self.y = 0
            self.velocity = 0
        if self.y >= height - groundheight - self.height:
            self.y = height - groundheight - self.height
            self.velocity = 0
            self.alive = False
    
    def draw(self):
        # draw the bird (a simple yellow circle)
        pygame.draw.circle(screen, yellow, (self.x, int(self.y) + self.height // 2), self.height // 2)
        # add a small triangle for the beak
        pygame.draw.polygon(screen, red, [(self.x + self.height // 2, self.y + self.height // 2), 
                                         (self.x + self.height // 2 + 10, self.y + self.height // 2 - 5),
                                         (self.x + self.height // 2 + 10, self.y + self.height // 2 + 5)])
    
    def get_mask(self):
        # return a rectangle for collision detection
        return pygame.Rect(self.x - self.height // 2, int(self.y), self.height, self.height)

# pipe class
class Pipe:
    def __init__(self, game_speed):
        self.x = width
        self.height = random.randint(100, 300)
        self.top_pipe = pygame.Rect(self.x, 0, 60, self.height)
        self.bottom_pipe = pygame.Rect(self.x, self.height + pipegap, 60, height - self.height - pipegap - groundheight)
        self.passed = False
        self.game_speed = game_speed
    
    def move(self):
        self.x -= self.game_speed
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x
    
    def draw(self):
        pygame.draw.rect(screen, green, self.top_pipe)
        pygame.draw.rect(screen, green, self.bottom_pipe)
    
    def collide(self, bird):
        bird_mask = bird.get_mask()
        return bird_mask.colliderect(self.top_pipe) or bird_mask.colliderect(self.bottom_pipe)
    
    def is_off_screen(self):
        return self.x + 60 < 0

# game functions
def draw_floor():
    pygame.draw.rect(screen, green, (0, height - groundheight, width, groundheight))

def draw_background():
    screen.fill(skyblue)
    # draw some clouds
    for i in range(3):
        pygame.draw.circle(screen, white, (100 + i * 150, 100), 30)
        pygame.draw.circle(screen, white, (130 + i * 150, 100), 30)
        pygame.draw.circle(screen, white, (115 + i * 150, 80), 30)

def display_score(score, high_score, current_speed=None):
    score_text = font.render(f'Score: {score}', True, black)
    high_score_text = font.render(f'High Score: {high_score}', True, black)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 50))
    
    # display current speed if provided
    if current_speed is not None:
        speed_text = font.render(f'Speed: {current_speed:.1f}x', True, black)
        screen.blit(speed_text, (10, 90))

def display_game_over(score, high_score):
    game_over_text = big_font.render('Game Over', True, black)
    score_text = font.render(f'Final Score: {score}', True, black)
    high_score_text = font.render(f'High Score: {high_score}', True, black)
    restart_text = font.render('Press SPACE to restart', True, black)
    
    screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 3))
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2 - 20))
    screen.blit(high_score_text, (width // 2 - high_score_text.get_width() // 2, height // 2 + 20))
    screen.blit(restart_text, (width // 2 - restart_text.get_width() // 2, height // 2 + 70))

def welcome_screen():
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False
        
        # draw welcome screen
        draw_background()
        draw_floor()
        
        # title
        title_text = big_font.render('FLAPPY BIRD', True, black)
        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 3))
        
        # instructions
        instruction_text = font.render('Press SPACE to start', True, black)
        screen.blit(instruction_text, (width // 2 - instruction_text.get_width() // 2, height // 2))
        
        # Draw a sample bird
        pygame.draw.circle(screen, yellow, (width // 2, height // 2 - 80), 15)
        pygame.draw.polygon(screen, red, [(width // 2 + 15, height // 2 - 80), 
                                         (width // 2 + 25, height // 2 - 85),
                                         (width // 2 + 25, height // 2 - 75)])
        
        pygame.display.update()
        clock.tick(60)

def main_game():
    bird = Bird()
    pipes = []
    score = 0
    high_score = load_high_score()
    last_pipe = pygame.time.get_ticks()
    game_active = True
    jump_cooldown = 0  # Cooldown timer for jumps
    jump_cooldown_time = 200  # Milliseconds between jumps when holding space
    current_game_speed = initialspeed  # Start with initial speed
    
    while True:
        current_time = pygame.time.get_ticks()
        
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_active:
                    # Reset game
                    return
        
        # check for space key being held down
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and game_active:
            # only jump if cooldown has expired
            if current_time - jump_cooldown >= jump_cooldown_time:
                bird.jump()
                jump_cooldown = current_time

        # draw background
        draw_background()
        
        if game_active:
            # bird movement
            bird.move()

            # generate pipes
            if current_time - last_pipe > pipefrequency:
                pipes.append(Pipe(current_game_speed))
                last_pipe = current_time

            # move and draw pipes
            for pipe in pipes:
                pipe.move()
                pipe.draw()
                
                # check collision
                if pipe.collide(bird):
                    game_active = False
                    # update high score if needed
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)

                # check if pipe is passed
                if not pipe.passed and pipe.x + 60 < bird.x:
                    pipe.passed = True
                    score += 1

                    # increase game speed based on score
                    new_speed = min(initialspeed + (score * speedincrease), maxspeed)

                    # update game speed for new pipes (existing pipes keep their original speed)
                    current_game_speed = new_speed
            
            # remove off-screen pipes
            pipes = [pipe for pipe in pipes if not pipe.is_off_screen()]

            # draw bird
            bird.draw()

            # check if bird hit the ground
            if not bird.alive:
                game_active = False
                # update high score if needed
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
        else:
            # draw bird and pipes in their last position
            for pipe in pipes:
                pipe.draw()
            bird.draw()
            
            # display game over screen
            display_game_over(score, high_score)

        # draw floor
        draw_floor()
        
        # display score and current speed
        display_score(score, high_score, current_game_speed)
        
        pygame.display.update()
        clock.tick(60)

# main game loop
def main():
    while True:
        welcome_screen()
        main_game()

if __name__ == "__main__":
    main()
