import asyncio
import pygame
import sys
import random
import math
import os

def paused():
    global game_state
    
    # Dim the screen
    dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 128))  # Black with 50% transparency
    screen.blit(dim_surface, (0, 0))
    
    # Draw pause menu
    pause_text = font.render("PAUSED", True, WHITE)
    resume_text = small_font.render("Press P to Resume", True, WHITE)
    restart_text = small_font.render("Press R to Restart", True, WHITE)
    
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 3))
    screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Resume
                game_state = "gameplay"
            elif event.key == pygame.K_r:  # Restart
                game_state = "gameplay"
                reset_game()

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BRIGHT_RED = (255, 50, 50)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
DARK_RED = (150, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (165, 42, 42)
SILVER = (192, 192, 192)
PURPLE = (128, 0, 128)
NEON_CYAN = (0, 255, 255)  # Bright neon color for sniper bullets

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Font for text
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)
tiny_font = pygame.font.SysFont('Arial', 16)

# Load sounds if available
sounds_loaded = False
try:
    shoot_sound = pygame.mixer.Sound(os.path.join('sounds', 'shoot.wav'))
    zombie_hit_sound = pygame.mixer.Sound(os.path.join('sounds', 'zombie_hit.wav'))
    zombie_death_sound = pygame.mixer.Sound(os.path.join('sounds', 'zombie_death.wav'))
    player_hit_sound = pygame.mixer.Sound(os.path.join('sounds', 'player_hit.wav'))
    game_over_sound = pygame.mixer.Sound(os.path.join('sounds', 'game_over.wav'))
    pickup_sound = pygame.mixer.Sound(os.path.join('sounds', 'pickup.wav'))
    overheat_sound = pygame.mixer.Sound(os.path.join('sounds', 'overheat.wav'))
    sounds_loaded = True
except:
    print("Sound files not found. Game will run without sound.")

# Weapon definitions
WEAPONS = {
    'pistol': {
        'name': 'Pistol',
        'cooldown': 0.33 * FPS,  # 0.33 seconds between shots
        'damage': 10,
        'bullet_speed': 10,
        'bullet_range': float('inf'),  # Infinite range
        'spread': 0,  # No spread
        'bullet_count': 1,  # Single bullet
        'auto_fire': False,
        'color': BLACK,
        'can_overheat': False,  # Pistol never overheats
        'heat_per_shot': 0,
        'max_heat': 100,
        'cool_rate': 1,
        'penetration': 1  # Can hit one zombie
    },
    'shotgun': {
        'name': 'Shotgun',
        'cooldown': 0.5 * FPS,  # 0.5 seconds between shots
        'damage': 10,
        'bullet_speed': 10,
        'bullet_range': WIDTH // 3.7,  # 1/4 of screen width
        'spread': 0.25,  # Bullet spread in radians
        'bullet_count': 3,  # Three bullets
        'auto_fire': False,
        'color': BROWN,
        'can_overheat': False,  # No overheat for shotgun
        'heat_per_shot': 0,
        'max_heat': 100,
        'cool_rate': 1,
        'penetration': 1  # Can hit one zombie
    },
    'machine_gun': {
        'name': 'Machine Gun',
        'cooldown': 0.1 * FPS,  # 0.1 seconds between shots
        'damage': 5,
        'bullet_speed': 12,
        'bullet_range': WIDTH // 2.5,  # 1/3 of screen width
        'spread': 0.05,  # Small spread
        'bullet_count': 1,
        'auto_fire': True,
        'color': SILVER,
        'can_overheat': True,  # Only machine gun can overheat
        'heat_per_shot': 4,     # Half as much heat per shot (was 8)
        'max_heat': 100,
        'cool_rate': 0.35,      # Half the cooling rate (was 0.5)
        'penetration': 1  # Can hit one zombie
    },
    'sniper': {
        'name': 'Sniper Rifle',
        'cooldown': 1.0 * FPS,  # 1 second between shots
        'damage': 50,  # Increased from 30 to 50
        'bullet_speed': 8,  # Slower bullet speed
        'bullet_range': float('inf'),  # Infinite range
        'spread': 0,  # No spread
        'bullet_count': 1,
        'auto_fire': False,
        'color': GRAY,
        'can_overheat': False,  # No overheat for sniper
        'heat_per_shot': 0,
        'max_heat': 100,
        'cool_rate': 1,
        'penetration': 2  # Can hit two zombies
    }
}

# Zombie types
ZOMBIE_TYPES = {
    'standard': {
        'name': 'Standard Zombie',
        'health': 30,
        'speed_range': (0.7, 2.0),  # More variation in speed
        'damage': 5,
        'radius': 12,
        'color': DARK_GREEN,
        'attack_delay': 30,
        'spawn_weight': 100,  # Higher weight = more common
        'can_shoot': False
    },
    'big': {
        'name': 'Big Zombie',
        'health': 150,  # 5x standard zombie health
        'speed_range': (0.4, 0.9),  # Slower
        'damage': 10,
        'radius': 28,  # Increased size (was 20)
        'color': ORANGE,
        'attack_delay': 120,  # Slower attacks
        'spawn_weight': 5,    # Reduced spawn rate
        'can_shoot': True,
        'shoot_range': WIDTH // 2,
        'projectile_speed': 4,  # Very slow fireball (was 3)
        'projectile_color': (255, 100, 0),  # Orange-red fireball
        'projectile_radius': 10,  # Larger projectile (was 8)
        'projectile_damage': 15,
        'projectile_penetration': 1  # Can only hit one player
    },
    'fast': {
        'name': 'Fast Zombie',
        'health': 20,  # 2 pistol shots to kill
        'speed_range': (2.2, 3.0),  # Very fast
        'damage': 5,
        'radius': 8,
        'color': BRIGHT_RED,
        'attack_delay': 20,
        'spawn_weight': 30,
        'can_shoot': False
    },
    'sniper': {
        'name': 'Sniper Zombie',
        'health': 40,
        'speed_range': (0.5, 1.2),
        'damage': 10,
        'radius': 14,
        'color': PURPLE,
        'attack_delay': 100,  # Long delay between attacks
        'spawn_weight': 15,
        'can_shoot': True,
        'shoot_range': WIDTH // 2,  # Range at which it starts shooting
        'projectile_speed': 12,
        'projectile_color': NEON_CYAN,  # Bright neon cyan color
        'projectile_radius': 6,
        'projectile_damage': 15,
        'projectile_penetration': 1,  # Can only hit player once
        'projectile_range': WIDTH / 1.3  # Increased range
    }
}

# Bullet class
class Bullet:
    def __init__(self, x, y, angle, velocity, damage, max_range, color=BLACK, penetration=1, is_zombie_bullet=False, radius=3):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.angle = angle
        self.velocity = velocity
        self.radius = radius  # Allow custom radius
        self.color = color
        self.damage = damage
        self.max_range = max_range
        self.penetration = penetration  # How many zombies this bullet can pass through
        self.is_zombie_bullet = is_zombie_bullet  # To differentiate player bullets from zombie bullets
        self.hit_targets = []  # Keep track of entities this bullet has already hit
        
    def update(self):
        self.x += math.cos(self.angle) * self.velocity
        self.y += math.sin(self.angle) * self.velocity
        
        # Check if bullet is off-screen or has reached max range
        if (self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT):
            return True
            
        # Check if bullet has exceeded maximum range
        dx = self.x - self.start_x
        dy = self.y - self.start_y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > self.max_range:
            return True
            
        return False
        
    def draw(self, screen):
        # Draw bullet
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # For larger projectiles, add some visual effect
        if self.radius > 4:
            # Draw inner circle for fireballs (orange/yellow)
            if isinstance(self.color, tuple) and self.color[0] > 200 and self.color[1] > 50 and self.color[1] < 150:
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius - 3)
            
            # Draw glow effect for neon bullets (sniper zombie)
            elif self.color == NEON_CYAN:
                # Draw outer glow for better visibility
                glow_surface = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (0, 255, 255, 70), (self.radius*2, self.radius*2), self.radius*2)
                screen.blit(glow_surface, (int(self.x) - self.radius*2, int(self.y) - self.radius*2))
                
                # Inner white core
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 2)
                
                # Draw outline for improved visibility
                pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.radius + 1, 1)

# Weapon Pickup class
class WeaponPickup:
    def __init__(self, x, y, weapon_type):
        self.x = x
        self.y = y
        self.radius = 15
        self.weapon_type = weapon_type
        self.color = WEAPONS[weapon_type]['color']
        self.pickup_time = 600  # Frames before pickup disappears (10 seconds)
        
    def update(self):
        self.pickup_time -= 1
        return self.pickup_time <= 0
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 3)
        
        # Draw weapon name
        text = tiny_font.render(WEAPONS[self.weapon_type]['name'], True, BLACK)
        screen.blit(text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2))

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.color = BLUE
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.angle = 0
        self.shoot_cooldown = 0
        
        # Weapon system
        self.weapons = ['pistol']  # Start with pistol
        self.current_weapon = 0
        self.shooting = False  # Track if player is holding shoot button
        
        # Weapon heat system (only for machine gun)
        self.weapon_heat = 0
        self.weapon_overheated = False

    def get_current_weapon(self):
        return self.weapons[self.current_weapon]
        
    def switch_weapon(self, index):
        if 0 <= index < len(self.weapons):
            self.current_weapon = index
            self.shoot_cooldown = 0  # Reset cooldown when switching weapons
            self.weapon_heat = 0  # Reset heat when switching weapons
            self.weapon_overheated = False
            
    def cycle_weapon(self, direction):
        self.current_weapon = (self.current_weapon + direction) % len(self.weapons)
        self.shoot_cooldown = 0  # Reset cooldown when switching weapons
        self.weapon_heat = 0  # Reset heat when switching weapons
        self.weapon_overheated = False

    def move(self, keys):
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

        # Keep player on screen
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Cool down weapon if it's machine gun
        weapon_type = self.get_current_weapon()
        if weapon_type == 'machine_gun':
            weapon = WEAPONS[weapon_type]
            
            if self.weapon_heat > 0:
                self.weapon_heat -= weapon['cool_rate']
                if self.weapon_heat <= 0:
                    self.weapon_heat = 0
                    self.weapon_overheated = False

    def aim(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        self.angle = math.atan2(dy, dx)

    def shoot(self, bullets):
        # Ensure we have weapons available
        if not self.weapons:
            return False
            
        weapon_type = self.get_current_weapon()
        weapon = WEAPONS[weapon_type]
        
        # Check if weapon is overheated (only applies to machine gun)
        if weapon_type == 'machine_gun' and self.weapon_overheated:
            return False
            
        # Check if can shoot
        if self.shoot_cooldown <= 0:
            # If weapon is auto_fire, we need to be holding the shoot button
            if weapon['auto_fire'] and not self.shooting:
                return False
                
            # Create bullets
            for i in range(weapon['bullet_count']):
                # Calculate spread angle
                if weapon['spread'] > 0:
                    spread_angle = random.uniform(-weapon['spread'], weapon['spread'])
                    bullet_angle = self.angle + spread_angle
                else:
                    bullet_angle = self.angle
                    
                bullet_x = self.x + math.cos(bullet_angle) * self.radius
                bullet_y = self.y + math.sin(bullet_angle) * self.radius
                
                bullet = Bullet(
                    bullet_x, 
                    bullet_y, 
                    bullet_angle, 
                    weapon['bullet_speed'], 
                    weapon['damage'],
                    weapon['bullet_range'],
                    weapon['color'],
                    weapon['penetration']
                )
                bullets.append(bullet)
                
            self.shoot_cooldown = weapon['cooldown']
            
            # Add heat if weapon can overheat (only machine gun)
            if weapon_type == 'machine_gun':
                self.weapon_heat += weapon['heat_per_shot']
                
                # Check if weapon has overheated
                if self.weapon_heat >= weapon['max_heat']:
                    self.weapon_heat = weapon['max_heat']
                    self.weapon_overheated = True
                    if sounds_loaded:
                        overheat_sound.play()
            
            if sounds_loaded:
                shoot_sound.play()
            return True
        return False

    def take_damage(self, damage):
        self.health -= damage
        if sounds_loaded:
            player_hit_sound.play()
        return self.health <= 0
        
    def pickup_weapon(self, weapon_type):
        if weapon_type not in self.weapons:
            self.weapons.append(weapon_type)
            return True
        return False

    def draw(self, screen):
        # Draw player body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw player direction line
        line_length = self.radius * 1.5
        end_x = self.x + math.cos(self.angle) * line_length
        end_y = self.y + math.sin(self.angle) * line_length
        pygame.draw.line(screen, BLACK, (int(self.x), int(self.y)), (int(end_x), int(end_y)), 2)
        
        # Draw weapon heat bar if using machine gun
        weapon_type = self.get_current_weapon()
        if weapon_type == 'machine_gun':
            weapon = WEAPONS[weapon_type]
            
            heat_bar_length = 50
            heat_bar_height = 4
            heat_bar_x = self.x - heat_bar_length // 2
            heat_bar_y = self.y + self.radius + 15
            
            # Add a slightly darker outline to the heat bar for visibility
            pygame.draw.rect(screen, BLACK, (heat_bar_x-1, heat_bar_y-1, heat_bar_length+2, heat_bar_height+2), 1)
            
            # Background of heat bar
            pygame.draw.rect(screen, GRAY, (heat_bar_x, heat_bar_y, heat_bar_length, heat_bar_height))
            
            # Current heat level
            heat_percentage = self.weapon_heat / weapon['max_heat']
            current_heat_length = int(heat_bar_length * heat_percentage)
            
            # Color depends on heat level
            if heat_percentage < 0.5:
                heat_color = GREEN
            elif heat_percentage < 0.8:
                heat_color = YELLOW
            else:
                heat_color = RED
                
            if current_heat_length > 0:  # Only draw if there's heat
                pygame.draw.rect(screen, heat_color, (heat_bar_x, heat_bar_y, current_heat_length, heat_bar_height))
            
            # If weapon is overheated, show warning with flashing effect
            if self.weapon_overheated:
                # Flash the text based on frame count
                flash_color = RED if pygame.time.get_ticks() % 1000 < 500 else YELLOW
                overheat_text = tiny_font.render("OVERHEATED!", True, flash_color)
                screen.blit(overheat_text, (self.x - overheat_text.get_width() // 2, heat_bar_y + heat_bar_height + 20))
                prompt_text = tiny_font.render("Switch weapons", True, BLACK)
                screen.blit(prompt_text, (self.x - prompt_text.get_width() // 2, heat_bar_y + heat_bar_height + 35))
        
        # Draw health bar
        health_bar_length = 50
        health_bar_height = 5
        health_bar_x = self.x - health_bar_length // 2
        health_bar_y = self.y - self.radius - 10
        
        # Background of health bar
        pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, health_bar_length, health_bar_height))
        
        # Current health
        current_health_length = int(health_bar_length * (self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, (health_bar_x, health_bar_y, current_health_length, health_bar_height))
        
        # Draw current weapon
        weapon_text = tiny_font.render(WEAPONS[self.get_current_weapon()]['name'], True, BLACK)
        screen.blit(weapon_text, (self.x - weapon_text.get_width() // 2, self.y + self.radius + 5))

# Zombie class
class Zombie:
    def __init__(self, x, y, zombie_type='standard'):
        self.x = x
        self.y = y
        self.type = zombie_type
        self.type_data = ZOMBIE_TYPES[zombie_type]
        
        self.radius = self.type_data['radius']
        self.color = self.type_data['color']
        self.speed = random.uniform(*self.type_data['speed_range'])
        self.health = self.type_data['health']
        self.max_health = self.type_data['health']
        self.damage = self.type_data['damage']
        self.attack_cooldown = 0
        self.attack_delay = self.type_data['attack_delay']
        
        # For zombies that can shoot
        self.shot_cooldown = 0
        if self.type_data.get('can_shoot', False):
            self.shot_cooldown = random.randint(30, 60)  # Random initial cooldown
            print(f"Created a shooting {zombie_type} zombie with shot_cooldown {self.shot_cooldown}")
            
        # Flag to track if zombie has fully entered the screen
        self.in_screen = False

    def move(self, player):
        # First check if zombie has fully entered the screen
        if not self.in_screen:
            if (self.radius < self.x < WIDTH - self.radius and 
                self.radius < self.y < HEIGHT - self.radius):
                self.in_screen = True
    
        # Sniper zombies try to maintain distance
        if self.type == 'sniper':
            dx = player.x - self.x
            dy = player.y - self.y
            distance = max(math.sqrt(dx*dx + dy*dy), 0.1)
            
            # If too close to player, back away
            if distance < self.type_data['shoot_range'] * 0.5:
                self.x -= (dx / distance) * self.speed
                self.y -= (dy / distance) * self.speed
            # If at good distance, move sideways
            elif distance < self.type_data['shoot_range'] * 0.8:
                # Move perpendicular to the player
                perpendicular_angle = math.atan2(dy, dx) + math.pi / 2
                self.x += math.cos(perpendicular_angle) * self.speed
                self.y += math.sin(perpendicular_angle) * self.speed
            # If too far, approach player
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
        else:
            # Standard movement for other zombies
            dx = player.x - self.x
            dy = player.y - self.y
            distance = max(math.sqrt(dx*dx + dy*dy), 0.1)  # Avoid division by zero
            
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        # Keep zombies on screen after they've entered
        if self.in_screen:
            self.x = max(self.radius, min(WIDTH - self.radius, self.x))
            self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def update(self, player, zombies, bullets):
        self.move(player)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        # Check collision with player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.radius + player.radius and self.attack_cooldown <= 0:
            player.take_damage(self.damage)
            self.attack_cooldown = self.attack_delay
        
        # Shooting logic for zombies that can shoot
        if self.type_data.get('can_shoot', False):
            if self.shot_cooldown > 0:
                self.shot_cooldown -= 1
            else:
                # Check if player is in shooting range
                if distance < self.type_data['shoot_range']:
                    # Calculate angle to player
                    angle = math.atan2(dy, dx)
                    
                    # Add some inaccuracy based on zombie type
                    inaccuracy = 0.1 if self.type == 'sniper' else 0.2
                    angle += random.uniform(-inaccuracy, inaccuracy)
                    
                    # Create the projectile
                    projectile_range = self.type_data.get('projectile_range', WIDTH)  # Default to WIDTH if not specified
                    bullet = Bullet(
                        self.x, 
                        self.y, 
                        angle, 
                        self.type_data['projectile_speed'],
                        self.type_data['projectile_damage'],
                        projectile_range,  # Use specific range if available
                        self.type_data['projectile_color'],
                        self.type_data['projectile_penetration'],
                        True,  # Is zombie bullet
                        self.type_data['projectile_radius']  # Use custom radius
                    )
                    bullets.append(bullet)
                    
                    # Debug print to confirm shooting
                    print(f"{self.type_data['name']} fired a projectile!")
                    
                    # Reset cooldown
                    self.shot_cooldown = self.attack_delay
            
        # Simple collision avoidance with other zombies
        for other in zombies:
            if other != self:
                dx = other.x - self.x
                dy = other.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < self.radius + other.radius:
                    push_x = dx / distance * 0.5
                    push_y = dy / distance * 0.5
                    self.x -= push_x
                    self.y -= push_y
                    other.x += push_x
                    other.y += push_y

    def take_damage(self, damage, particles, blood_stains):
        old_health = self.health
        self.health -= damage
        
        # Create blood particles
        particle_count = 5
        if damage > 15:
            particle_count = 8
            
        # Check if it's a big zombie for enhanced effects
        is_big_zombie = (self.type == 'big')
        
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            # Vary particle size based on damage
            particle_size = random.randint(1, 4)
            if damage > 20:
                particle_size = random.randint(2, 5)
                speed = random.uniform(2, 4)
            particles.append(Particle(self.x, self.y, angle, speed, DARK_RED, particle_size, is_big_zombie))
            
        # Add blood stain - bigger for bigger hits
        stain_size = random.randint(3, 6)
        if damage > 15:
            stain_size = random.randint(5, 8)
        blood_stains.append((self.x, self.y, stain_size, DARK_RED))
        
        if sounds_loaded:
            if self.health <= 0:
                zombie_death_sound.play()
            else:
                zombie_hit_sound.play()
                
        return self.health <= 0

    def draw(self, screen):
        # Draw zombie body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw health bar
        health_bar_length = self.radius * 2 + 10
        health_bar_height = 4
        health_bar_x = self.x - health_bar_length // 2
        health_bar_y = self.y - self.radius - 8
        
        # Background of health bar
        pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, health_bar_length, health_bar_height))
        
        # Current health
        current_health_length = int(health_bar_length * (self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, (health_bar_x, health_bar_y, current_health_length, health_bar_height))
        
        # For zombies that can shoot, show an indicator when they're about to shoot
        if self.type_data.get('can_shoot', False) and self.shot_cooldown < 15:
            warning_color = RED if self.type == 'sniper' else (255, 120, 0) # Red for snipers, orange for big zombies
            pygame.draw.circle(screen, warning_color, (int(self.x), int(self.y)), int(self.radius * 1.3), 2)

# Blood particle class
class Particle:
    def __init__(self, x, y, angle, speed, color, radius=None, is_big_zombie=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.color = color
        self.radius = radius if radius is not None else random.randint(1, 3)
        self.lifetime = random.randint(20, 40)
        self.is_big_zombie = is_big_zombie  # Flag for enhanced effects
        
        if is_big_zombie:
            self.lifetime = random.randint(20, 60)  # Longer lifetime for big zombie particles
            self.alpha = 255  # Alpha for fading (only for big zombies)
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.lifetime -= 1
        self.speed *= 0.95  # Deceleration
        
        # Fade particles as they age (only for big zombies)
        if self.is_big_zombie and self.lifetime < 20:
            self.alpha = int(255 * (self.lifetime / 20))
        
        return self.lifetime <= 0
        
    def draw(self, screen):
        if self.is_big_zombie:
            # Enhanced drawing for big zombie particles
            jitter = random.randint(-1, 1)
            # Scale alpha for darker color as it fades
            color = self.color
            if isinstance(color, tuple) and len(color) == 3:
                # Apply alpha if the color is not already an RGBA tuple
                r, g, b = color
                color = (r, g, b, self.alpha)
            
            # Create a temporary surface for particles with alpha
            particle_surface = pygame.Surface((self.radius*2 + 2, self.radius*2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface, 
                color, 
                (self.radius+1, self.radius+1), 
                self.radius + jitter
            )
            screen.blit(particle_surface, (int(self.x) - self.radius - 1, int(self.y) - self.radius - 1))
        else:
            # Simple drawing for regular zombie particles
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Game state variables
game_state = "menu"  # menu, gameplay, game_over, paused
current_wave = 1
zombies_per_wave = 5
time_between_waves = 180  # Frames (3 seconds at 60 FPS)
wave_timer = 0
score = 0

# Game objects
player = Player(WIDTH // 2, HEIGHT // 2)
zombies = []
bullets = []
particles = []
blood_stains = []  # Permanent blood stains on the ground
max_blood_stains = 100  # Limit to prevent performance issues
weapon_pickups = []

# Determine zombie types to spawn based on wave number
def get_zombie_type(wave_number):
    # Calculate probabilities based on wave number
    # Later waves have more special zombies
    standard_prob = max(100 - wave_number * 5, 40)  # Decrease standard probability with waves, min 40%
    big_prob = min(5 + wave_number, 10)  # Increase big zombie probability with waves, max 10%
    fast_prob = min(10 + wave_number * 2, 30)  # Increase fast zombie probability with waves, max 30%
    sniper_prob = min(0 + wave_number, 15)  # Increase sniper probability with waves, max 15%
    
    # No sniper zombies in early waves
    if wave_number < 3:
        sniper_prob = 0
        
    # Normalize probabilities
    total = standard_prob + big_prob + fast_prob + sniper_prob
    standard_prob = standard_prob / total * 100
    big_prob = big_prob / total * 100
    fast_prob = fast_prob / total * 100
    sniper_prob = sniper_prob / total * 100
    
    # Print probabilities for debugging
    # print(f"Wave {wave_number} probabilities: Standard={standard_prob:.1f}%, Big={big_prob:.1f}%, Fast={fast_prob:.1f}%, Sniper={sniper_prob:.1f}%")
    
    # Weighted random selection
    roll = random.uniform(0, 100)
    if roll < standard_prob:
        return 'standard'
    elif roll < standard_prob + big_prob:
        return 'big'
    elif roll < standard_prob + big_prob + fast_prob:
        return 'fast'
    else:
        return 'sniper'

# Spawn zombies for a wave
def spawn_wave(wave_number):
    wave_zombies = []
    zombie_count = zombies_per_wave + (wave_number - 1) * 2
    
    # Count zombie types for debugging
    type_counts = {'standard': 0, 'big': 0, 'fast': 0, 'sniper': 0}
    
    for _ in range(zombie_count):
        # Spawn zombies at the edge of the screen
        side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        
        if side == 0:  # Top
            x = random.randint(0, WIDTH)
            y = -20
        elif side == 1:  # Right
            x = WIDTH + 20
            y = random.randint(0, HEIGHT)
        elif side == 2:  # Bottom
            x = random.randint(0, WIDTH)
            y = HEIGHT + 20
        else:  # Left
            x = -20
            y = random.randint(0, HEIGHT)
        
        zombie_type = get_zombie_type(wave_number)
        type_counts[zombie_type] += 1
        wave_zombies.append(Zombie(x, y, zombie_type))
    
    # Print zombie type counts for debugging
    print(f"Wave {wave_number} zombie types: {type_counts}")
    return wave_zombies

# Spawn weapon pickup
def spawn_weapon_pickup():
    """Spawn a weapon pickup that the player can collect"""
    # Get weapons the player doesn't have yet
    available_weapons = [w for w in WEAPONS.keys() if w not in player.weapons]
    
    if available_weapons:
        # Pick a random weapon
        weapon_type = random.choice(available_weapons)
        
        # Spawn in a random position on the screen (away from edges)
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        
        weapon_pickups.append(WeaponPickup(x, y, weapon_type))
        print(f"Spawned weapon pickup: {weapon_type}")
    else:
        print("No more weapons available to pick up")

# Game loop
def menu():
    global game_state
    
    screen.fill(WHITE)
    
    title = font.render("Zombie Survival", True, DARK_GREEN)
    instruction = small_font.render("Press SPACE to Start", True, BLACK)
    # Controls explanation in menu
    controls = small_font.render("Controls: WASD to move, Mouse/Space to shoot", True, BLACK)
    controls2 = small_font.render("Number keys (1-4) or E to switch weapons, P to pause", True, BLACK)
    
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT // 2))
    screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT // 2 + 40))
    screen.blit(controls2, (WIDTH // 2 - controls2.get_width() // 2, HEIGHT // 2 + 70))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_state = "gameplay"
                reset_game()

def gameplay():
    global game_state, current_wave, wave_timer, score, zombies, blood_stains, weapon_pickups
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                player.shooting = True
                player.shoot(bullets)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                player.shooting = False
        elif event.type == pygame.KEYDOWN:
            # Weapon switching with number keys
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                weapon_index = event.key - pygame.K_1  # Convert to 0-based index
                if weapon_index < len(player.weapons):
                    player.switch_weapon(weapon_index)
            # Cycle weapons with E
            elif event.key == pygame.K_e:
                player.cycle_weapon(1)  # Cycle forward
            # Shooting with space
            elif event.key == pygame.K_SPACE:
                player.shooting = True
                player.shoot(bullets)  # Will only overheat if it's a machine gun
            # Pause game with P
            elif event.key == pygame.K_p:
                game_state = "paused"
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                player.shooting = False
    
    # Get keyboard input
    keys = pygame.key.get_pressed()
    player.move(keys)
    
    # Continue auto-firing if shooting button is held and weapon is machine gun
    weapon_type = player.get_current_weapon()
    if player.shooting and WEAPONS[weapon_type]['auto_fire']:
        if not (weapon_type == 'machine_gun' and player.weapon_overheated):
            player.shoot(bullets)
    
    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()
    player.aim(mouse_pos)
    
    # Update game objects
    player.update()
    
    # Update weapon pickups
    i = 0
    while i < len(weapon_pickups):
        if weapon_pickups[i].update():  # Returns True if pickup should be removed (timed out)
            weapon_pickups.pop(i)
        else:
            # Check for collision with player
            dx = player.x - weapon_pickups[i].x
            dy = player.y - weapon_pickups[i].y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < player.radius + weapon_pickups[i].radius:
                if player.pickup_weapon(weapon_pickups[i].weapon_type):
                    if sounds_loaded:
                        pickup_sound.play()
                    print(f"Player picked up {weapon_pickups[i].weapon_type}")
                weapon_pickups.pop(i)
            else:
                i += 1
    
    # Update bullets and check for collisions
    i = 0
    while i < len(bullets):
        # Check if bullet should be removed due to lifetime or going off-screen
        if bullets[i].update():
            bullets.pop(i)
            continue  # Skip to next bullet
        
        # Copy the current bullet for easier reference
        bullet = bullets[i]
        bullet_removed = False
        
        # Handle zombie bullets hitting player
        if bullet.is_zombie_bullet:
            # Check if this bullet has already hit the player
            if id(player) not in bullet.hit_targets:  
                dx = bullet.x - player.x
                dy = bullet.y - player.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < bullet.radius + player.radius:
                    player.take_damage(bullet.damage)
                    bullet.hit_targets.append(id(player))  # Mark player as hit
                    
                    # For sniper zombie bullets, allow penetration
                    if bullet.color == NEON_CYAN:  # Sniper zombie bullet
                        # If it's penetrating projectile, don't remove yet
                        if len(bullet.hit_targets) >= bullet.penetration:
                            bullets.pop(i)
                            bullet_removed = True
                    else:
                        # Regular zombie bullets get removed after hitting
                        bullets.pop(i)
                        bullet_removed = True
        
        # Handle player bullets hitting zombies
        else:
            hit_zombies = []  # Track which zombies were hit in this frame
            
            # Find all zombies hit by this bullet that haven't been hit already
            for j, zombie in enumerate(zombies):
                # Skip zombies this bullet has already hit
                if id(zombie) in bullet.hit_targets:
                    continue
                    
                dx = bullet.x - zombie.x
                dy = bullet.y - zombie.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < bullet.radius + zombie.radius:
                    hit_zombies.append(j)
                    bullet.hit_targets.append(id(zombie))  # Mark this zombie as hit
                    
                    # Stop checking if we've hit maximum penetration
                    if len(bullet.hit_targets) >= bullet.penetration:
                        break
            
            # Process hits in reverse order (to handle removals properly)
            for j in sorted(hit_zombies, reverse=True):
                # Safety check to make sure the zombie index is still valid
                if j < len(zombies):
                    if zombies[j].take_damage(bullet.damage, particles, blood_stains):
                        score += 10
                        zombies.pop(j)
            
            # Remove bullet if it has reached its penetration limit
            if len(bullet.hit_targets) >= bullet.penetration and hit_zombies:
                bullets.pop(i)
                bullet_removed = True
        
        # Only increment index if bullet wasn't removed
        if not bullet_removed:
            i += 1
    
    # Update zombies
    for zombie in zombies:
        zombie.update(player, zombies, bullets)
        
    # Update particles
    i = 0
    while i < len(particles):
        if particles[i].update():  # Returns True if particle should be removed
            particles.pop(i)
        else:
            i += 1
    
    # Limit blood stains
    if len(blood_stains) > max_blood_stains:
        blood_stains = blood_stains[-max_blood_stains:]
    
    # Check for player death
    if player.health <= 0:
        game_state = "game_over"
        if sounds_loaded:
            game_over_sound.play()
        return
    
    # Wave management - check if all zombies are dead
    if len(zombies) == 0:
        # If there's a wave timer, count it down
        if wave_timer <= 0:
            # Start the next wave
            current_wave += 1
            print(f"Starting wave {current_wave}")
            
            # Spawn weapon pickup every 3 waves
            if current_wave % 3 == 0:
                print(f"Wave {current_wave} is divisible by 3 - attempting to spawn weapon pickup")
                spawn_weapon_pickup()
                
            zombies = spawn_wave(current_wave)
            wave_timer = time_between_waves
        else:
            wave_timer -= 1
    
    # Drawing
    screen.fill(WHITE)
    
    # Draw blood stains first (they stay on the ground)
    for x, y, radius, color in blood_stains:
        # Draw with some variation
        pygame.draw.circle(screen, color, (int(x), int(y)), radius)
        # Add darker center to some stains for depth
        if random.random() < 0.5:  # 50% chance
            darker_color = (max(0, color[0] - 30), max(0, color[1] - 30), max(0, color[2] - 30))
            pygame.draw.circle(screen, darker_color, (int(x), int(y)), radius // 2)
    
    # Draw weapon pickups
    for pickup in weapon_pickups:
        pickup.draw(screen)
    
    # Draw other game objects
    for particle in particles:
        particle.draw(screen)
    
    for bullet in bullets:
        bullet.draw(screen)
    
    for zombie in zombies:
        zombie.draw(screen)
    
    player.draw(screen)
    
    # Draw UI
    draw_ui()
    
    pygame.display.flip()

def game_over():
    global game_state
    
    screen.fill(WHITE)
    
    game_over_text = font.render("Game Over", True, RED)
    wave_text = small_font.render(f"You survived until wave {current_wave}", True, BLACK)
    score_text = small_font.render(f"Score: {score}", True, BLACK)
    restart_text = small_font.render("Press SPACE to Play Again", True, BLACK)
    menu_text = small_font.render("Press ESC for Menu", True, BLACK)
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
    screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, HEIGHT // 2 - 20))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 10))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 80))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_state = "gameplay"
                reset_game()
            elif event.key == pygame.K_ESCAPE:
                game_state = "menu"

def draw_ui():
    # Draw player health bar at the bottom of the screen
    health_bar_length = 200
    health_bar_height = 20
    health_bar_x = 20
    health_bar_y = HEIGHT - 30
    
    pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, health_bar_length, health_bar_height))
    current_health_length = int(health_bar_length * (player.health / player.max_health))
    pygame.draw.rect(screen, GREEN, (health_bar_x, health_bar_y, current_health_length, health_bar_height))
    
    health_text = small_font.render(f"Health: {player.health}/{player.max_health}", True, BLACK)
    screen.blit(health_text, (health_bar_x + 5, health_bar_y - 25))
    
    # Draw weapon inventory
    inventory_x = 20
    inventory_y = 20
    
    weapon_text = small_font.render("Weapons:", True, BLACK)
    screen.blit(weapon_text, (inventory_x, inventory_y))
    
    for i, weapon in enumerate(player.weapons):
        color = YELLOW if i == player.current_weapon else BLACK
        text = small_font.render(f"{i+1}: {WEAPONS[weapon]['name']}", True, color)
        screen.blit(text, (inventory_x, inventory_y + 30 + i * 25))
    
    # Draw wave information
    wave_text = small_font.render(f"Wave: {current_wave}", True, BLACK)
    screen.blit(wave_text, (WIDTH - wave_text.get_width() - 20, 20))
    
    # Draw zombie count
    zombie_text = small_font.render(f"Zombies: {len(zombies)}", True, BLACK)
    screen.blit(zombie_text, (WIDTH - zombie_text.get_width() - 20, 50))
    
    # Draw score
    score_text = small_font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 80))
    
    # Count zombie types for display
    zombie_counts = {}
    for zombie in zombies:
        zombie_type = zombie.type
        if zombie_type in zombie_counts:
            zombie_counts[zombie_type] += 1
        else:
            zombie_counts[zombie_type] = 1
    
    # Display zombie type counts
    y_offset = 110
    for z_type, count in zombie_counts.items():
        type_text = small_font.render(f"{ZOMBIE_TYPES[z_type]['name']}: {count}", True, ZOMBIE_TYPES[z_type]['color'])
        screen.blit(type_text, (WIDTH - type_text.get_width() - 20, y_offset))
        y_offset += 25
    
    # Draw wave timer if applicable
    if len(zombies) == 0 and wave_timer > 0:
        next_wave_text = small_font.render(f"Next wave in: {wave_timer // 60 + 1}", True, BLACK)
        screen.blit(next_wave_text, (WIDTH // 2 - next_wave_text.get_width() // 2, HEIGHT // 3))
        
        # If a weapon pickup is active, draw an indicator
        if weapon_pickups:
            pickup_text = small_font.render("Weapon pickup available!", True, BLUE)
            screen.blit(pickup_text, (WIDTH // 2 - pickup_text.get_width() // 2, HEIGHT // 3 + 30))

def reset_game():
    global player, zombies, bullets, particles, blood_stains, weapon_pickups, current_wave, wave_timer, score
    
    player = Player(WIDTH // 2, HEIGHT // 2)
    zombies = spawn_wave(1)
    bullets = []
    particles = []
    blood_stains = []
    weapon_pickups = []
    current_wave = 1
    wave_timer = 0
    score = 0
    
    print("Game reset. Starting wave 1.")

# Main game loop
# def main():
#     while True:
#         clock.tick(FPS)
        
#         if game_state == "menu":
#             menu()
#         elif game_state == "gameplay":
#             gameplay()
#         elif game_state == "game_over":
#             game_over()
#         elif game_state == "paused":
#             paused()

# Async version for web deployment (uncomment to use with pygbag)
async def main():
    while True:
        clock.tick(FPS)
        
        if game_state == "menu":
            menu()
        elif game_state == "gameplay":
            gameplay()
        elif game_state == "game_over":
            game_over()
        
        # This is needed for web compatibility
        await asyncio.sleep(0)

if __name__ == "__main__":
    main()
    # For web deployment (uncomment for pygbag):
    # asyncio.run(main_web())