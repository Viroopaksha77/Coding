import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()

# Set up the display
width = 600
height = 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Carrom Game")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
brown = (139, 69, 19)
darkbrown = (101, 67, 33)
lightbrown = (205, 133, 63)
beige = (245, 245, 220)
cream = (255, 253, 208)
yellow = (255, 255, 0)
pink = (255, 192, 203)

# Fonts
title_font = pygame.font.Font("Repositories/Wood.ttf", 64)
button_font = pygame.font.Font("Repositories/Wood.ttf", 32)
score_font = pygame.font.Font("Repositories/Wood.ttf", 24)

# Game states
WELCOME_SCREEN = 0
INSTRUCTIONS = 1
VS_FRIEND = 2
VS_COMPUTER = 3
GAME_OVER = 4

# Current game state
game_state = WELCOME_SCREEN

# Button class for interactive buttons
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, black, self.rect, 2, border_radius=10)
        
        text_surface = button_font.render(self.text, True, black)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Create buttons for welcome screen
vs_friend_button = Button(width//2 - 150, height//2 - 40, 300, 60, "vs Friend", lightbrown, beige)
vs_computer_button = Button(width//2 - 150, height//2 + 40, 300, 60, "vs Computer", lightbrown, beige)
instructions_button = Button(width//2 - 150, height//2 + 120, 300, 60, "Instructions", lightbrown, beige)

# Coin class for carrom men
class Coin:
    def __init__(self, x, y, color, radius=15, is_queen=False):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.is_queen = is_queen
        self.velocity_x = 0
        self.velocity_y = 0
        self.friction = 0.98
        self.pocketed = False
        
    def draw(self, surface):
        if not self.pocketed:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            if self.is_queen:
                pygame.draw.circle(surface, red, (int(self.x), int(self.y)), self.radius - 5)
            else:
                pygame.draw.circle(surface, black, (int(self.x), int(self.y)), self.radius, 1)
                
    def update(self):
        if not self.pocketed:
            self.x += self.velocity_x
            self.y += self.velocity_y
            
            # Apply friction
            self.velocity_x *= self.friction
            self.velocity_y *= self.friction
            
            # Stop if velocity is very small
            if abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
                self.velocity_x = 0
                self.velocity_y = 0

# Striker class
class Striker(Coin):
    def __init__(self, x, y):
        super().__init__(x, y, white, radius=20)
        self.is_selected = False
        self.power = 0
        self.max_power = 30  # Increased max power
        self.angle = 0
        self.valid_position = True  # Flag to indicate if position is valid
        
    def draw(self, surface):
        if not self.pocketed:
            # Draw the striker with color based on position validity
            if self.valid_position:
                pygame.draw.circle(surface, white, (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(surface, black, (int(self.x), int(self.y)), self.radius, 2)
            else:
                # Red tint for invalid position
                pygame.draw.circle(surface, (255, 200, 200), (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(surface, red, (int(self.x), int(self.y)), self.radius, 2)
            
            # Draw power indicator when selected
            if self.is_selected and self.power > 0:
                end_x = self.x + math.cos(self.angle) * self.power * 5
                end_y = self.y + math.sin(self.angle) * self.power * 5
                pygame.draw.line(surface, red, (self.x, self.y), (end_x, end_y), 2)
                
    def position_on_baseline(self, board, mouse_x, player_turn=0):
        # Position based on player turn (0 for bottom, 1 for top)
        if player_turn == 0:  # Player 1 (bottom)
            baseline_y = board.board_y + board.board_size - 50
        else:  # Player 2 (top)
            baseline_y = board.board_y + 50
        
        # Calculate bounds for striker movement
        left_bound = board.board_x + 50
        right_bound = board.board_x + board.board_size - 50
        
        # Clamp the x position to the bounds
        new_x = max(left_bound, min(mouse_x, right_bound))
        
        # Store original position to restore if new position overlaps with coins
        original_x, original_y = self.x, self.y
        
        # Try the new position
        self.x = new_x
        self.y = baseline_y
        
        # Check if this position overlaps with any coins
        if board.striker_overlaps_coins():
            # Mark position as invalid but don't restore original position
            # This allows visual feedback while still showing where the mouse is
            self.valid_position = False
        else:
            self.valid_position = True
        
    def aim(self, mouse_pos):
        # Calculate angle between striker and mouse position
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.angle = math.atan2(dy, dx)
        
        # Calculate power based on distance (capped at max_power)
        distance = math.sqrt(dx**2 + dy**2)
        self.power = min(distance / 15, self.max_power)  # Increased power factor
        
    def shoot(self):
        # Apply velocity based on power and angle with a power multiplier
        power_multiplier = 1.5  # Increase the power
        self.velocity_x = math.cos(self.angle) * self.power * power_multiplier
        self.velocity_y = math.sin(self.angle) * self.power * power_multiplier
        self.power = 0
        self.is_selected = False

# Carrom board class
class CarromBoard:
    def __init__(self):
        self.board_size = min(width, height) - 100
        self.board_x = (width - self.board_size) // 2
        self.board_y = (height - self.board_size) // 2
        self.hole_radius = self.board_size // 20
        self.coins = []
        self.striker = Striker(width // 2, self.board_y + self.board_size - 50)
        self.setup_coins()
        self.turn = 0  # 0 for player 1, 1 for player 2
        self.scores = [0, 0]
        self.game_phase = "positioning"  # positioning, aiming, shooting, waiting
        
    def setup_coins(self):
        # Clear existing coins
        self.coins = []
        
        # Center of the board
        center_x = self.board_x + self.board_size // 2
        center_y = self.board_y + self.board_size // 2
        
        # Queen (red coin) at the center
        self.coins.append(Coin(center_x, center_y, red, is_queen=True))
        
        # Arrange other coins in a circle around the queen
        coin_radius = 15
        arrangement_radius = 40
        
        # Black coins
        for i in range(9):
            angle = 2 * math.pi * i / 9
            x = center_x + math.cos(angle) * arrangement_radius
            y = center_y + math.sin(angle) * arrangement_radius
            self.coins.append(Coin(x, y, black))
            
        # White coins
        arrangement_radius = 70
        for i in range(9):
            angle = 2 * math.pi * i / 9 + math.pi/9  # Offset to stagger
            x = center_x + math.cos(angle) * arrangement_radius
            y = center_y + math.sin(angle) * arrangement_radius
            self.coins.append(Coin(x, y, white))
            
        # Reset striker - Player 1 starts at the bottom
        self.striker = Striker(width // 2, 0)  # Y will be set by position_on_baseline
        self.striker.position_on_baseline(self, width // 2, 0)  # 0 for bottom position (Player 1)
        
    def draw(self, surface):
        # Draw the outer board (frame)
        pygame.draw.rect(surface, darkbrown, 
                         (self.board_x - 30, self.board_y - 30, 
                          self.board_size + 60, self.board_size + 60))
        
        pygame.draw.rect(surface, brown, 
                         (self.board_x - 20, self.board_y - 20, 
                          self.board_size + 40, self.board_size + 40))
        
        # Draw the inner board
        pygame.draw.rect(surface, cream, 
                         (self.board_x, self.board_y, 
                          self.board_size, self.board_size))
        
        # Draw decorative lines
        line_color = (180, 140, 100)
        # Outer rectangle
        pygame.draw.rect(surface, line_color, 
                        (self.board_x + 30, self.board_y + 30, 
                         self.board_size - 60, self.board_size - 60), 2)
        
        # Inner rectangle
        pygame.draw.rect(surface, line_color, 
                        (self.board_x + 60, self.board_y + 60, 
                         self.board_size - 120, self.board_size - 120), 2)
        
        # Draw corner pockets
        corners = [
            (self.board_x, self.board_y),  # Top-left
            (self.board_x + self.board_size, self.board_y),  # Top-right
            (self.board_x, self.board_y + self.board_size),  # Bottom-left
            (self.board_x + self.board_size, self.board_y + self.board_size)  # Bottom-right
        ]
        
        for corner in corners:
            # Draw pocket hole
            pygame.draw.circle(surface, black, corner, self.hole_radius)
            # Draw decorative ring around pocket
            pygame.draw.circle(surface, darkbrown, corner, self.hole_radius + 5, 3)
        
        # Draw center circle
        center_x = self.board_x + self.board_size // 2
        center_y = self.board_y + self.board_size // 2
        pygame.draw.circle(surface, red, (center_x, center_y), self.board_size // 8, 2)
        
        # Draw diagonal arrows from corners to center
        for corner in corners:
            dx = center_x - corner[0]
            dy = center_y - corner[1]
            length = math.sqrt(dx**2 + dy**2)
            unit_x = dx / length
            unit_y = dy / length
            
            # Draw line from near corner to near center
            start_x = corner[0] + unit_x * (self.hole_radius + 10)
            start_y = corner[1] + unit_y * (self.hole_radius + 10)
            end_x = center_x - unit_x * (self.board_size // 8 + 10)
            end_y = center_y - unit_y * (self.board_size // 8 + 10)
            
            pygame.draw.line(surface, line_color, (start_x, start_y), (end_x, end_y), 2)
        
        # Draw baselines for both players
        # Player 1 (bottom)
        bottom_baseline_y = self.board_y + self.board_size - 50
        pygame.draw.line(surface, black, 
                         (self.board_x + 50, bottom_baseline_y), 
                         (self.board_x + self.board_size - 50, bottom_baseline_y), 2)
        
        # Player 2 (top)
        top_baseline_y = self.board_y + 50
        pygame.draw.line(surface, black, 
                         (self.board_x + 50, top_baseline_y), 
                         (self.board_x + self.board_size - 50, top_baseline_y), 2)
        
        # Draw small circles at the edges of the baselines
        # Bottom baseline markers
        pygame.draw.circle(surface, black, (self.board_x + 50, bottom_baseline_y), 5)
        pygame.draw.circle(surface, black, (self.board_x + self.board_size - 50, bottom_baseline_y), 5)
        
        # Top baseline markers
        pygame.draw.circle(surface, black, (self.board_x + 50, top_baseline_y), 5)
        pygame.draw.circle(surface, black, (self.board_x + self.board_size - 50, top_baseline_y), 5)
        
        # Draw player indicators
        p1_text = score_font.render("P1", True, black)
        p2_text = score_font.render("P2", True, black)
        surface.blit(p1_text, (self.board_x + self.board_size // 2 - 15, bottom_baseline_y + 15))
        surface.blit(p2_text, (self.board_x + self.board_size // 2 - 15, top_baseline_y - 30))
        
        # Draw coins
        for coin in self.coins:
            coin.draw(surface)
            
        # Draw striker
        self.striker.draw(surface)
        
        # Draw scores and turn indicator
        player1_text = f"Player 1: {self.scores[0]}"
        player2_text = f"Player 2: {self.scores[1]}"
        
        player1_surface = score_font.render(player1_text, True, black)
        player2_surface = score_font.render(player2_text, True, black)
        
        surface.blit(player1_surface, (self.board_x, self.board_y - 30))
        surface.blit(player2_surface, (self.board_x + self.board_size - 150, self.board_y - 30))
        
        # Turn indicator
        turn_text = f"Player {self.turn + 1}'s Turn"
        turn_surface = score_font.render(turn_text, True, black)
        surface.blit(turn_surface, (width // 2 - 60, self.board_y - 30))
        
        # Game phase indicator
        phase_text = f"Phase: {self.game_phase.capitalize()}"
        phase_surface = score_font.render(phase_text, True, black)
        surface.blit(phase_surface, (width // 2 - 60, height - 30))
        
    def update(self):
        # Only update coins and check collisions when not in positioning phase
        if self.game_phase == "positioning":
            # In positioning phase, only check if striker overlaps with coins
            # but don't update coins or check for collisions
            pass
        else:
            # Update striker
            self.striker.update()
            
            # Update all coins
            for coin in self.coins:
                coin.update()
                
            # Check for collisions
            self.check_collisions()
        
        # Check if all pieces have stopped moving
        all_stopped = (self.striker.velocity_x == 0 and self.striker.velocity_y == 0)
        for coin in self.coins:
            if not coin.pocketed and (coin.velocity_x != 0 or coin.velocity_y != 0):
                all_stopped = False
                break
                
        # If all pieces have stopped after shooting, switch to positioning phase
        if all_stopped and self.game_phase == "waiting":
            # Switch turns
            self.turn = 1 - self.turn
            self.game_phase = "positioning"
            
            # Reset striker if it was pocketed
            if self.striker.pocketed:
                # Create new striker at the appropriate position based on whose turn it is
                self.striker = Striker(width // 2, 0)  # Y will be set by position_on_baseline
                self.striker.position_on_baseline(self, width // 2, self.turn)
            else:
                # Make sure striker velocity is reset
                self.striker.velocity_x = 0
                self.striker.velocity_y = 0
                
    def striker_overlaps_coins(self):
        """Check if the striker overlaps with any coins on the board."""
        if self.striker.pocketed:
            return False
            
        for coin in self.coins:
            if not coin.pocketed:
                # Calculate distance between striker and coin centers
                distance = math.sqrt((self.striker.x - coin.x)**2 + (self.striker.y - coin.y)**2)
                # Check if they overlap
                if distance < (self.striker.radius + coin.radius):
                    return True
        return False
        
    def check_winner(self):
        # Check if any player has reached 21 points or more
        if self.scores[0] >= 21:
            return 1  # Player 1 wins
        elif self.scores[1] >= 21:
            return 2  # Player 2 wins
            
        # Check if all coins are pocketed
        all_pocketed = True
        for coin in self.coins:
            if not coin.pocketed:
                all_pocketed = False
                break
                
        if all_pocketed:
            # Determine winner based on score
            if self.scores[0] > self.scores[1]:
                return 1  # Player 1 wins
            elif self.scores[1] > self.scores[0]:
                return 2  # Player 2 wins
            else:
                return 3  # Tie
                
        return 0  # No winner yet
                
    def check_collisions(self):
        # Check for coin-coin collisions
        for i in range(len(self.coins)):
            if self.coins[i].pocketed:
                continue
                
            # Check collision with striker
            if not self.striker.pocketed:
                self.handle_collision(self.striker, self.coins[i])
                
            # Check collision with other coins
            for j in range(i + 1, len(self.coins)):
                if not self.coins[j].pocketed:
                    self.handle_collision(self.coins[i], self.coins[j])
                    
        # Check for wall collisions
        self.check_wall_collisions()
        
        # Check for pocket collisions
        self.check_pocket_collisions()
        
    def handle_collision(self, coin1, coin2):
        # Calculate distance between centers
        dx = coin2.x - coin1.x
        dy = coin2.y - coin1.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check if coins are colliding
        if distance < coin1.radius + coin2.radius:
            # Calculate collision normal
            if distance == 0:  # Avoid division by zero
                nx, ny = 1, 0
            else:
                nx, ny = dx/distance, dy/distance
                
            # Calculate relative velocity
            dvx = coin2.velocity_x - coin1.velocity_x
            dvy = coin2.velocity_y - coin1.velocity_y
            
            # Calculate velocity along normal
            velocity_normal = dvx * nx + dvy * ny
            
            # If coins are moving away from each other, no collision response
            if velocity_normal > 0:
                return
                
            # Calculate impulse
            impulse = 2 * velocity_normal / 2  # Assuming equal mass
            
            # Apply impulse
            coin1.velocity_x += impulse * nx
            coin1.velocity_y += impulse * ny
            coin2.velocity_x -= impulse * nx
            coin2.velocity_y -= impulse * ny
            
            # Separate coins to avoid sticking
            overlap = (coin1.radius + coin2.radius - distance) / 2
            coin1.x -= overlap * nx
            coin1.y -= overlap * ny
            coin2.x += overlap * nx
            coin2.y += overlap * ny
            
    def check_wall_collisions(self):
        # Check striker wall collisions
        if not self.striker.pocketed:
            if self.striker.x - self.striker.radius < self.board_x:
                self.striker.x = self.board_x + self.striker.radius
                self.striker.velocity_x = -self.striker.velocity_x * 0.8
            elif self.striker.x + self.striker.radius > self.board_x + self.board_size:
                self.striker.x = self.board_x + self.board_size - self.striker.radius
                self.striker.velocity_x = -self.striker.velocity_x * 0.8
                
            if self.striker.y - self.striker.radius < self.board_y:
                self.striker.y = self.board_y + self.striker.radius
                self.striker.velocity_y = -self.striker.velocity_y * 0.8
            elif self.striker.y + self.striker.radius > self.board_y + self.board_size:
                self.striker.y = self.board_y + self.board_size - self.striker.radius
                self.striker.velocity_y = -self.striker.velocity_y * 0.8
                
        # Check coin wall collisions
        for coin in self.coins:
            if not coin.pocketed:
                if coin.x - coin.radius < self.board_x:
                    coin.x = self.board_x + coin.radius
                    coin.velocity_x = -coin.velocity_x * 0.8
                elif coin.x + coin.radius > self.board_x + self.board_size:
                    coin.x = self.board_x + self.board_size - coin.radius
                    coin.velocity_x = -coin.velocity_x * 0.8
                    
                if coin.y - coin.radius < self.board_y:
                    coin.y = self.board_y + coin.radius
                    coin.velocity_y = -coin.velocity_y * 0.8
                elif coin.y + coin.radius > self.board_y + self.board_size:
                    coin.y = self.board_y + self.board_size - coin.radius
                    coin.velocity_y = -coin.velocity_y * 0.8
                    
    def check_pocket_collisions(self):
        # Define pocket positions
        pockets = [
            (self.board_x, self.board_y),  # Top-left
            (self.board_x + self.board_size, self.board_y),  # Top-right
            (self.board_x, self.board_y + self.board_size),  # Bottom-left
            (self.board_x + self.board_size, self.board_y + self.board_size)  # Bottom-right
        ]
        
        # Check striker
        if not self.striker.pocketed:
            for pocket in pockets:
                distance = math.sqrt((self.striker.x - pocket[0])**2 + (self.striker.y - pocket[1])**2)
                if distance < self.hole_radius:
                    self.striker.pocketed = True
                    self.striker.velocity_x = 0
                    self.striker.velocity_y = 0
                    break
                    
        # Check coins
        for coin in self.coins:
            if not coin.pocketed:
                for pocket in pockets:
                    distance = math.sqrt((coin.x - pocket[0])**2 + (coin.y - pocket[1])**2)
                    if distance < self.hole_radius:
                        coin.pocketed = True
                        coin.velocity_x = 0
                        coin.velocity_y = 0
                        
                        # Award points
                        if coin.is_queen:
                            self.scores[self.turn] += 5
                        elif coin.color == black:
                            self.scores[self.turn] += 1
                        elif coin.color == white:
                            self.scores[self.turn] += 2
                        break
                        
    def handle_input(self, mouse_pos, mouse_clicked, is_computer_turn=False):
        if is_computer_turn:
            # Computer AI logic
            if self.game_phase == "positioning":
                # Position the striker randomly along the baseline based on turn
                left_bound = self.board_x + 50
                right_bound = self.board_x + self.board_size - 50
                
                # Try to find a position that doesn't overlap with coins
                max_attempts = 20
                attempts = 0
                valid_position_found = False
                
                while attempts < max_attempts and not valid_position_found:
                    # Random position with some strategy
                    self.striker.x = random.uniform(left_bound, right_bound)
                    # Position based on turn (Player 2/Computer is at the top)
                    self.striker.position_on_baseline(self, self.striker.x, 1)  # 1 for top position
                    
                    # Check if this position is valid (doesn't overlap with coins)
                    if not self.striker_overlaps_coins():
                        valid_position_found = True
                    
                    attempts += 1
                
                # Move to aiming phase
                self.game_phase = "aiming"
                self.striker.is_selected = True
                
            elif self.game_phase == "aiming":
                # Find a target (prioritize queen, then closest coin)
                target_x, target_y = self.board_x + self.board_size // 2, self.board_y + self.board_size // 2
                
                # Look for non-pocketed coins
                available_coins = [coin for coin in self.coins if not coin.pocketed]
                
                if available_coins:
                    # Prioritize the queen if it's still on the board
                    queen_coins = [coin for coin in available_coins if coin.is_queen]
                    if queen_coins:
                        target = queen_coins[0]
                    else:
                        # Otherwise aim for a random coin
                        target = random.choice(available_coins)
                    
                    target_x, target_y = target.x, target.y
                
                # Calculate angle and add some randomness for imperfect AI
                dx = target_x - self.striker.x
                dy = target_y - self.striker.y
                angle = math.atan2(dy, dx)
                
                # Add some randomness to the angle
                angle += random.uniform(-0.2, 0.2)
                
                # Set the striker's angle and power
                self.striker.angle = angle
                self.striker.power = random.uniform(10, 20)  # Increased random power
                
                # Shoot after a short delay
                self.striker.shoot()
                self.game_phase = "waiting"
        else:
            # Human player input
            if self.game_phase == "positioning":
                # Position the striker on the baseline based on turn
                self.striker.position_on_baseline(self, mouse_pos[0], self.turn)
                
                # Only allow clicking if the striker position is valid (not overlapping with coins)
                if mouse_clicked and self.striker.valid_position:
                    self.game_phase = "aiming"
                    self.striker.is_selected = True
                    
            elif self.game_phase == "aiming":
                # Aim the striker
                self.striker.aim(mouse_pos)
                
                if mouse_clicked:
                    self.striker.shoot()
                    self.game_phase = "waiting"

# Create carrom board
carrom_board = CarromBoard()

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_clicked = True
    
    # Fill the background
    window.fill(white)
    
    # Handle different game states
    if game_state == WELCOME_SCREEN:
        # Draw title
        title_text = title_font.render("Carrom Game", True, black)
        title_rect = title_text.get_rect(center=(width//2, height//4))
        window.blit(title_text, title_rect)
        
        # Draw and check buttons
        vs_friend_button.check_hover(mouse_pos)
        vs_computer_button.check_hover(mouse_pos)
        instructions_button.check_hover(mouse_pos)
        
        vs_friend_button.draw(window)
        vs_computer_button.draw(window)
        instructions_button.draw(window)
        
        if vs_friend_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = VS_FRIEND
            carrom_board = CarromBoard()  # Reset the board
        
        if vs_computer_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = VS_COMPUTER
            carrom_board = CarromBoard()  # Reset the board
            
        if instructions_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = INSTRUCTIONS
    
    elif game_state == INSTRUCTIONS:
        # Draw title
        title_text = button_font.render("How to Play", True, black)
        title_rect = title_text.get_rect(center=(width//2, 50))
        window.blit(title_text, title_rect)
        
        # Instructions text
        instructions = [
            "OBJECTIVE:",
            "- Pocket all your coins and the queen to win",
            "- Black coins: 1 point each",
            "- White coins: 2 points each",
            "- Queen (red): 5 points",
            "",
            "HOW TO PLAY:",
            "1. Player 1 plays from the bottom, Player 2 from the top",
            "2. Position the striker by moving your mouse along your baseline",
            "3. Click to select the striker",
            "4. Move the mouse to aim (red line shows direction and power)",
            "5. Click again to shoot",
            "6. Players take turns after each shot",
            "",
            "CONTROLS:",
            "- Mouse movement: Position/aim striker",
            "- Left click: Select/shoot striker",
            "- First to 21 points wins!"
        ]
        
        # Draw instructions text
        y_offset = 100
        for line in instructions:
            if line.startswith("-") or line.startswith("•"):
                # Indent bullet points
                text = score_font.render(line, True, black)
                window.blit(text, (width//2 - 180, y_offset))
            elif line.startswith("1") or line.startswith("2") or line.startswith("3") or line.startswith("4") or line.startswith("5"):
                # Indent numbered points
                text = score_font.render(line, True, black)
                window.blit(text, (width//2 - 180, y_offset))
            elif line == "":
                # Empty line for spacing
                pass
            else:
                # Section headers
                text = score_font.render(line, True, black)
                text_rect = text.get_rect(center=(width//2, y_offset))
                window.blit(text, text_rect)
            
            y_offset += 30
        
        # Back button
        back_text = button_font.render("Back to Menu", True, black)
        back_rect = back_text.get_rect(center=(width//2, height - 50))
        pygame.draw.rect(window, lightbrown, 
                        (back_rect.x - 10, back_rect.y - 10, 
                         back_rect.width + 20, back_rect.height + 20),
                        border_radius=10)
        pygame.draw.rect(window, black, 
                        (back_rect.x - 10, back_rect.y - 10, 
                         back_rect.width + 20, back_rect.height + 20),
                        2, border_radius=10)
        window.blit(back_text, back_rect)
        
        # Check if back button is clicked
        if mouse_clicked and back_rect.collidepoint(mouse_pos):
            game_state = WELCOME_SCREEN
    
    elif game_state == VS_FRIEND or game_state == VS_COMPUTER:
        # Update game logic
        carrom_board.update()
        
        # Handle input based on game mode and turn
        is_computer_turn = (game_state == VS_COMPUTER and carrom_board.turn == 1)
        carrom_board.handle_input(mouse_pos, mouse_clicked, is_computer_turn)
        
        # Check for winner
        winner = carrom_board.check_winner()
        if winner > 0:
            game_state = GAME_OVER
        
        # Draw the carrom board
        carrom_board.draw(window)
        
    elif game_state == GAME_OVER:
        # Draw the carrom board in the background
        carrom_board.draw(window)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 200))  # White with alpha
        window.blit(overlay, (0, 0))
        
        # Determine winner message
        winner = carrom_board.check_winner()
        if winner == 1:
            winner_text = "Player 1 Wins!"
        elif winner == 2:
            if game_state == VS_COMPUTER:
                winner_text = "Computer Wins!"
            else:
                winner_text = "Player 2 Wins!"
        else:
            winner_text = "It's a Tie!"
            
        # Draw winner text
        game_over_text = title_font.render("Game Over", True, black)
        winner_surface = button_font.render(winner_text, True, black)
        score_text = button_font.render(f"Score: {carrom_board.scores[0]} - {carrom_board.scores[1]}", True, black)
        
        game_over_rect = game_over_text.get_rect(center=(width//2, height//2 - 80))
        winner_rect = winner_surface.get_rect(center=(width//2, height//2))
        score_rect = score_text.get_rect(center=(width//2, height//2 + 60))
        
        window.blit(game_over_text, game_over_rect)
        window.blit(winner_surface, winner_rect)
        window.blit(score_text, score_rect)
        
        # Play again button
        play_again_button = Button(width//2 - 150, height//2 + 120, 300, 60, "Play Again", lightbrown, beige)
        play_again_button.check_hover(mouse_pos)
        play_again_button.draw(window)
        
        if play_again_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = WELCOME_SCREEN
        
        # Draw game mode text
        mode_text = "Friend Mode" if game_state == VS_FRIEND else "Computer Mode"
        mode_surface = button_font.render(mode_text, True, black)
        window.blit(mode_surface, (20, 20))
        
        # Game instructions based on current phase
        instruction_text = ""
        if carrom_board.game_phase == "positioning":
            instruction_text = "Move mouse to position striker, then click to select"
        elif carrom_board.game_phase == "aiming":
            instruction_text = "Move mouse to aim, click to shoot"
        elif carrom_board.game_phase == "waiting":
            instruction_text = "Wait for pieces to stop moving..."
            
        if instruction_text:
            instruction_surface = score_font.render(instruction_text, True, black)
            instruction_rect = instruction_surface.get_rect(center=(width//2, 20))
            window.blit(instruction_surface, instruction_rect)
        
        # Back button
        back_text = button_font.render("Back to Menu", True, black)
        back_rect = back_text.get_rect(topleft=(20, height - 50))
        pygame.draw.rect(window, lightbrown, 
                        (back_rect.x - 5, back_rect.y - 5, 
                         back_rect.width + 10, back_rect.height + 10),
                        border_radius=5)
        pygame.draw.rect(window, black, 
                        (back_rect.x - 5, back_rect.y - 5, 
                         back_rect.width + 10, back_rect.height + 10),
                        2, border_radius=5)
        window.blit(back_text, back_rect)
        
        # Help button
        help_text = button_font.render("?", True, black)
        help_rect = help_text.get_rect(topright=(width - 20, 20))
        pygame.draw.circle(window, lightbrown, help_rect.center, 20)
        pygame.draw.circle(window, black, help_rect.center, 20, 2)
        window.blit(help_text, help_rect)
        
        # Check if back button is clicked
        if mouse_clicked and back_rect.collidepoint(mouse_pos):
            game_state = WELCOME_SCREEN
            
        # Check if help button is clicked
        if mouse_clicked and (help_rect.x - 20 <= mouse_pos[0] <= help_rect.x + 20) and (help_rect.y - 20 <= mouse_pos[1] <= help_rect.y + 20):
            game_state = INSTRUCTIONS
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()