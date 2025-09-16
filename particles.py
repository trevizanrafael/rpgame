# particles.py
import pygame
import math
import random
from settings import *

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, color, size, life, velocity):
        super().__init__()
        self.image = pygame.Surface(size); self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.life = life; self.creation_time = pygame.time.get_ticks()
        self.vx, self.vy = velocity
    def update(self, dt):
        if pygame.time.get_ticks() - self.creation_time > self.life: self.kill()
        self.rect.x += self.vx * (dt / 16.67); self.rect.y += self.vy * (dt / 16.67)
    def draw(self, surface): surface.blit(self.image, self.rect)

def create_particles(pos, p_type, group):
    count = random.randint(8, 15)
    color = RED
    if p_type == 'blood': color = RED
    elif p_type == 'fragments': color = GREY
    
    if p_type in ['blood', 'fragments']:
        for _ in range(count):
            vel = (random.uniform(-3, 3), random.uniform(-3, 3))
            group.add(Particle(pos, color, (random.randint(2,4), random.randint(2,4)), random.randint(200, 400), vel))
    elif p_type == 'dust':
        vel = (random.uniform(-0.5, 0.5), random.uniform(-0.5, -1))
        group.add(Particle(pos, (139, 115, 85), (random.randint(3,6), random.randint(3,6)), 400, vel))
    elif p_type == 'sparks':
        for _ in range(count):
            vel = (random.uniform(-2, 2), random.uniform(-2, 2))
            group.add(Particle(pos, ORANGE, (3, 3), 200, vel))

class LightningBolt(pygame.sprite.Sprite):
    def __init__(self, start_pos, end_pos):
        super().__init__()
        self.lifetime = 100; self.creation_time = pygame.time.get_ticks()
        dx, dy = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
        length = int(math.hypot(dx, dy)); angle = math.degrees(math.atan2(-dy, dx))
        if length == 0: length = 1
        self.image = pygame.Surface((length, 2), pygame.SRCALPHA); self.image.fill(YELLOW)
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=start_pos)
    def update(self, dt):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime: self.kill()
    def draw(self, surface): surface.blit(self.image, self.rect)