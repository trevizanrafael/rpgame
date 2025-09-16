# enemy.py
import pygame
import math
import random
from settings import *
from ui import load_sprite
from particles import create_particles
from player import LeapExplosion

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, speed, hp, score, xp, screen_dims):
        super().__init__()
        self.speed = speed; self.max_hp = hp; self.hp = hp; self.score_value = score; self.xp_value = xp
        self.screen_width, self.screen_height = screen_dims
        self.last_hit_time = 0; self.flash_timer = 0; self.flash_duration = 100; self.effects = {}
        self.projectiles = None
    def apply_effect(self, effect_type, duration, damage_per_tick=0):
        self.effects[effect_type] = {'duration': duration, 'damage': damage_per_tick, 'timer': 1000}
    def take_damage(self, amount, sounds, knockback=(0, 0)):
        self.hp -= amount; self.flash_timer = self.flash_duration
        sounds['hit'].play(); self.rect.x += knockback[0]; self.rect.y += knockback[1]
        if self.hp <= 0: self.kill()

    # ALTERADO: Assinatura de update (sem 'obstacles')
    def update(self, player_rect, projectiles, enemies, dt):
        self.projectiles = projectiles
        self.move(player_rect, dt)
        if self.flash_timer > 0: self.flash_timer -= dt
        to_remove = []
        for effect, data in self.effects.items():
            data['duration'] -= dt
            if data['duration'] <= 0: to_remove.append(effect)
            else:
                if 'damage' in data:
                    data['timer'] -= dt
                    if data['timer'] <= 0:
                        data['timer'] = 1000; self.hp -= data['damage']
                        create_particles(self.rect.center, 'sparks', projectiles['vfx'])
                        if self.hp <= 0: self.kill()
        for effect in to_remove: del self.effects[effect]
    def draw(self, surface):
        surface.blit(self.image, self.rect)
    
    # ALTERADO: Assinatura de move (sem 'obstacles')
    def move(self, player_rect, dt, move_multiplier=1):
        dx, dy = player_rect.centerx - self.rect.centerx, player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            move_speed = self.speed * (dt / 16.67) * move_multiplier
            self.rect.x += (dx / dist) * move_speed; self.rect.y += (dy / dist) * move_speed

class Grunt(Enemy):
    def __init__(self, screen_dims, is_night):
        side = random.choice(['top', 'left', 'right'])
        if side == 'top': pos = (random.randint(0, screen_dims[0]), -30)
        elif side == 'left': pos = (-30, random.randint(0, screen_dims[1]))
        else: pos = (screen_dims[0] + 30, random.randint(0, screen_dims[1]))
        speed = random.uniform(1.5, 2.5); hp = 100
        if is_night: speed *= 1.2; hp = int(hp * 1.5)
        super().__init__(pos, speed, hp, 10, 10, screen_dims)
        self.frames = [load_sprite('Grunt-1.png', (60, 60)), load_sprite('Grunt-2.png', (60, 60))]
        self.current_frame = 0; self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=pos)
        self.anim_timer = 0; self.anim_speed = 300
    def update(self, player_rect, projectiles, enemies, dt):
        super().update(player_rect, projectiles, enemies, dt)
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0; self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
    def draw(self, surface):
        if self.flash_timer > 0:
            flash_img = self.image.copy(); flash_img.fill(WHITE, special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(flash_img, self.rect)
        else:
            surface.blit(self.image, self.rect)

class Tank(Grunt):
    def __init__(self, screen_dims, is_night):
        super().__init__(screen_dims, is_night)
        self.frames = [load_sprite('Tank-1.png', (70, 70)), load_sprite('Tank-2.png', (70, 70))]
        self.image = self.frames[0]; self.rect = self.image.get_rect(center=self.rect.center)
        self.speed = 1.5; self.max_hp = self.hp = 300; self.score_value = 30; self.xp_value = 25; self.anim_speed = 400
        if is_night: self.speed *= 1.2; self.hp = int(self.hp * 1.5)

class Bomber(Grunt):
    def __init__(self, screen_dims, is_night):
        super().__init__(screen_dims, is_night)
        self.image = pygame.Surface((35,35)); self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.original_color = ORANGE; self.speed *= 1.5; self.xp_value = 15; self.score_value=5
    def update(self, player_rect, projectiles, enemies, dt):
        super().update(player_rect, projectiles, enemies, dt)
        if self.rect.colliderect(player_rect): 
            self.kill()
    def kill(self):
        if self.projectiles:
            self.projectiles['enemy_explosions'].add(LeapExplosion(self.rect.center))
        super(Grunt, self).kill()
    def draw(self, surface):
        color = WHITE if self.flash_timer > 0 else self.original_color
        self.image.fill(color); surface.blit(self.image, self.rect)

class Assassin(Grunt):
    def __init__(self, screen_dims, is_night):
        super().__init__(screen_dims, is_night)
        self.image = pygame.Surface((30,30), pygame.SRCALPHA); self.original_color = (60,60,60)
        self.image.fill(self.original_color); self.rect = self.image.get_rect(center=self.rect.center)
        self.speed *= 1.2; self.alpha = 50; self.image.set_alpha(self.alpha); self.reveal_distance = 120; self.xp_value = 20
        self.hp = 25
    def take_damage(self, amount, sounds, knockback=(0, 0)):
        if self.alpha < 255: return
        super().take_damage(amount, sounds, knockback)
    def update(self, player_rect, projectiles, enemies, dt):
        super().update(player_rect, projectiles, enemies, dt)
        dist = math.hypot(player_rect.centerx - self.rect.centerx, player_rect.centery - self.rect.centery)
        self.alpha = 255 if dist < self.reveal_distance else 50
    def draw(self, surface): 
        temp_image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        color_to_draw = WHITE if self.flash_timer > 0 else self.original_color
        temp_image.fill(color_to_draw); temp_image.set_alpha(self.alpha)
        surface.blit(temp_image, self.rect)
        
class Shockwave(pygame.sprite.Sprite):
    def __init__(self, x, y, target, angle_offset=0):
        super().__init__(); self.image = pygame.Surface([10, 40]); self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(x, y))
        angle = math.atan2(target.centery - y, target.centerx - x) + math.radians(angle_offset)
        self.vel_x = math.cos(angle) * 6; self.vel_y = math.sin(angle) * 6; self.damage = 30
    def update(self, dt):
        move_speed = dt / 16.67; self.rect.x += self.vel_x * move_speed; self.rect.y += self.vel_y * move_speed
        if not pygame.display.get_surface().get_rect().colliderect(self.rect): self.kill()
    def draw(self, surface): surface.blit(self.image, self.rect)

class PoisonFog(pygame.sprite.Sprite):
    def __init__(self, center_pos):
        super().__init__(); self.radius = 100
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*PURPLE, 100), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=center_pos)
        self.duration = 8000; self.damage = 5; self.damage_interval = 500; self.last_damage_time = 0
    def update(self, dt):
        self.duration -= dt
        if self.duration <= 0: self.kill()
    def damage_player(self, player):
        now = pygame.time.get_ticks()
        if now - self.last_damage_time > self.damage_interval: player.take_damage(self.damage); self.last_damage_time = now
    def draw(self, surface): surface.blit(self.image, self.rect)

# NOVO: Classe Illusion readicionada ao arquivo
class Illusion(Enemy):
    def __init__(self, pos, screen_width, screen_height):
        offset_pos = (pos[0] + random.randint(-50, 50), pos[1] + random.randint(-50, 50))
        super().__init__(offset_pos, 1.5, 1, 0, 0, (screen_width, screen_height))
        self.image = load_sprite('Morgana-Flutuando.png', (90, 120))
        self.image.set_alpha(128)
        self.rect = self.image.get_rect(center=offset_pos)
    def draw(self, surface): # Ilusões não piscam ao tomar dano
        surface.blit(self.image, self.rect)

class FireCone(pygame.sprite.Sprite):
    def __init__(self, start, angle):
        super().__init__(); self.image = pygame.Surface((18, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, FIRE_RED, self.image.get_rect()); self.rect = self.image.get_rect(center=start)
        self.vx, self.vy = math.cos(angle)*10, math.sin(angle)*10; self.damage = 18; self.lifetime = 700
    def update(self, dt):
        f = dt/16.67; self.rect.x += int(self.vx*f); self.rect.y += int(self.vy*f); self.lifetime -= dt
        if self.lifetime <= 0 or not pygame.display.get_surface().get_rect().colliderect(self.rect): self.kill()
    def draw(self, surf): surf.blit(self.image, self.rect)

class Meteor(pygame.sprite.Sprite):
    def __init__(self, target_pos):
        super().__init__(); self.telegraph_time = 700; self.exploded = False; self.has_damaged = False
        self.radius = 28; self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*FIRE_RED, 90), (self.radius, self.radius), self.radius, 3)
        self.rect = self.image.get_rect(center=target_pos); self.damage = 35
    def update(self, dt):
        self.telegraph_time -= dt
        if self.telegraph_time <= 0 and not self.exploded:
            self.exploded = True; self.image.fill((0,0,0,0))
            pygame.draw.circle(self.image, (*ORANGE, 190), (self.radius, self.radius), self.radius)
            self.telegraph_time = 150 
        elif self.exploded and self.telegraph_time <= 0: self.kill()
    def draw(self, surf): surf.blit(self.image, self.rect)
        
class Boss(Enemy):
    def __init__(self, pos, speed, hp, score, xp, screen_dims, name):
        super().__init__(pos, speed, hp, score, xp, screen_dims)
        self.name = name; self.action_timer = 0; self.action_index = 0; self.actions = []
    def take_damage(self, amount, sounds, knockback=(0, 0)):
        super().take_damage(amount, sounds, knockback=(knockback[0]/5.0, knockback[1]/5.0))
    def start_action_sequence(self):
        self.action_index = 0; action = self.actions[self.action_index]; self.action_timer = action['duration']
    def next_action(self):
        self.action_index = (self.action_index + 1) % len(self.actions)
        action = self.actions[self.action_index]; self.action_timer = action['duration']
        
    def update(self, p_rect, pr, en, dt):
        self.action_timer -= dt
        self.perform_action(p_rect, pr, en, dt)
        if self.flash_timer > 0: self.flash_timer -= dt
        if self.action_timer <= 0: self.next_action()
    def perform_action(self, p_rect, pr, en, dt): pass

class TitanusRex(Boss):
    def __init__(self, screen_dims):
        pos = (screen_dims[0] - 80, screen_dims[1] / 2)
        super().__init__(pos, 2.0, 500, 500, 100, screen_dims, "TITANUS REX")
        sprite_size = (150, 150)
        self.sprites = {
            'idle': load_sprite('Rex-Idle.png', sprite_size),
            'walk': [load_sprite('Rex-direita.png', sprite_size), load_sprite('Rex-Walk-2.png', sprite_size)],
            'prepare_dash': load_sprite('Rex-Prepare-Dash.png', sprite_size),
            'dash': load_sprite('Rex-Dash.png', sprite_size),
            'hurt': load_sprite('Rex-Dano.png', sprite_size)
        }
        self.current_walk_frame = 0; self.anim_timer = 0; self.anim_speed = 400
        self.image = self.sprites['idle']; self.rect = self.image.get_rect(center=pos); self.facing_right = False
        self.actions = [
            {'name': 'WALK', 'duration': 4000, 'speed_multiplier': 1.0},
            {'name': 'PREPARE_DASH', 'duration': 140},
            {'name': 'DASH', 'duration': 500, 'speed_multiplier': 16.0},
            {'name': 'COOLDOWN', 'duration': 1500},
        ]
        self.dash_direction = (0, 0); self.start_action_sequence()
        
    # ALTERADO: Assinatura da função update
    def update(self, player_rect, projectiles, enemies, dt):
        super().update(player_rect, projectiles, enemies, dt)
        action_name = self.actions[self.action_index]['name']; current_sprite_base = self.sprites['idle']
        if action_name == 'WALK' or action_name == 'COOLDOWN':
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0; self.current_walk_frame = (self.current_walk_frame + 1) % len(self.sprites['walk'])
            current_sprite_base = self.sprites['walk'][self.current_walk_frame]
            self.facing_right = self.rect.centerx < player_rect.centerx
        elif action_name == 'PREPARE_DASH': current_sprite_base = self.sprites['prepare_dash']
        elif action_name == 'DASH': current_sprite_base = self.sprites['dash']
        self.image = pygame.transform.flip(current_sprite_base, not self.facing_right, False)
        
    def perform_action(self, p_rect, pr, en, dt):
        action = self.actions[self.action_index]; name = action['name']
        if name in ['WALK', 'COOLDOWN']: self.move(p_rect, dt, action.get('speed_multiplier', 0.8))
        if name == 'PREPARE_DASH':
            if self.action_timer > action['duration'] - dt*2: 
                dx, dy = p_rect.centerx - self.rect.centerx, p_rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0: self.dash_direction = (dx / dist, dy / dist)
        elif name == 'DASH':
            move_speed = self.speed * (dt / 16.67) * action['speed_multiplier']
            self.rect.x += self.dash_direction[0] * move_speed; self.rect.y += self.dash_direction[1] * move_speed
            
    def draw(self, surface):
        if self.flash_timer > 0:
            flash_image = self.sprites['hurt'].copy()
            if not self.facing_right: flash_image = pygame.transform.flip(flash_image, True, False)
            surface.blit(flash_image, self.rect)
        else:
            surface.blit(self.image, self.rect)

class Morgana(Boss):
    def __init__(self, screen_dims):
        pos = (screen_dims[0] - 60, screen_dims[1] / 2)
        super().__init__(pos, 2, 300, 500, 100, screen_dims, "MORGANA")
        self.is_visible = True; sprite_size = (90, 120)
        self.sprites = {
            'idle': load_sprite('Morgana-Flutuando.png', sprite_size), 'casting': load_sprite('Morgana-Casting.png', sprite_size),
            'hurt': load_sprite('Morgana-Dano.png', sprite_size), 'move': load_sprite('Morgana-Kiting-Direita.png', sprite_size)
        }
        self.image = self.sprites['idle']; self.rect = self.image.get_rect(center=pos); self.facing_right = False
        self.preferred_distance = 350
        self.actions = [ {'name': 'KITE', 'duration': 4000}, {'name': 'POISON_FOG', 'duration': 2000}, {'name': 'KITE', 'duration': 4000},
                         {'name': 'PREPARE_ILLUSIONS', 'duration': 1000}, {'name': 'VANISH', 'duration': 1000}, {'name': 'REAPPEAR', 'duration': 100} ]
        self.start_action_sequence()
    
    # ALTERADO: Assinatura da função update
    def update(self, player_rect, projectiles, enemies, dt):
        super().update(player_rect, projectiles, enemies, dt)
        action_name = self.actions[self.action_index]['name']; current_sprite_key = 'idle'
        self.is_visible = (action_name != 'VANISH')
        if action_name == 'KITE':
            self.facing_right = self.rect.centerx < player_rect.centerx; current_sprite_key = 'move'
        elif action_name in ['POISON_FOG', 'PREPARE_ILLUSIONS']: current_sprite_key = 'casting'
        self.image = pygame.transform.flip(self.sprites[current_sprite_key], not self.facing_right, False)
    def draw(self, surface):
        if not self.is_visible: return
        if self.flash_timer > 0: surface.blit(self.sprites['hurt'], self.rect)
        else: surface.blit(self.image, self.rect)
    def perform_action(self, p_rect, pr, en, dt):
        action = self.actions[self.action_index]; name = action['name']
        if name == 'KITE':
            dist = math.hypot(p_rect.centerx - self.rect.centerx, p_rect.centery - self.rect.centery)
            if dist < self.preferred_distance:
                dx, dy = p_rect.centerx - self.rect.centerx, p_rect.centery - self.rect.centery
                strafe_dx, strafe_dy = -dy, dx; dist_strafe = math.hypot(strafe_dx, strafe_dy)
                if dist_strafe > 0:
                    move_speed = self.speed * (dt / 16.67)
                    self.rect.x += (strafe_dx / dist_strafe) * move_speed; self.rect.y += (strafe_dy / dist_strafe) * move_speed
            else: self.move(p_rect, dt)
        elif name == 'POISON_FOG':
            if self.action_timer > action['duration'] - dt*2: pr['environment'].add(PoisonFog(p_rect.center))
        elif name == 'REAPPEAR':
            if self.action_timer > action['duration'] - dt*2:
                self.rect.center = (random.randint(100, 700), random.randint(150, 550))
                for _ in range(2): en.add(Illusion(self.rect.center, self.screen_width, self.screen_height))

class Draken(Boss):
    def __init__(self, screen_dims):
        w, h = screen_dims; pos = (w - 80, h / 2)
        super().__init__(pos, 2.2, 450, 500, 150, screen_dims, "DRAKEN")
        sprite_size = (110, 110)
        self.sprites = {
            'idle': load_sprite('Draken-Idle.png', sprite_size), 'chase': load_sprite('Draken-Chase-Direita.png', sprite_size),
            'cone': load_sprite('Draken-Rajada.png', sprite_size), 'meteor': load_sprite('Draken-Chuva.png', sprite_size),
            'hurt': load_sprite('Draken-Dano.png', sprite_size),
        }
        self.image = self.sprites['idle']; self.rect = self.image.get_rect(center=pos); self.facing_right = False
        self.actions = [
            {'name': 'CHASE', 'duration': 3500, 'speed_multiplier': 1.2}, {'name': 'FIRE_CONE', 'duration': 1200},
            {'name': 'COOLDOWN', 'duration': 1200}, {'name': 'METEOR_RAIN', 'duration': 3000},
            {'name': 'COOLDOWN', 'duration': 1500},
        ]
        self.start_action_sequence()
        
    # ALTERADO: Assinatura da função update
    def update(self, player_rect, projectiles, enemies, dt):
        super().update(player_rect, projectiles, enemies, dt)
        action_name = self.actions[self.action_index]['name']; current_sprite_key = 'idle'
        if action_name == 'CHASE':
            self.facing_right = self.rect.centerx < player_rect.centerx; current_sprite_key = 'chase'
        elif action_name == 'FIRE_CONE': current_sprite_key = 'cone'
        elif action_name == 'METEOR_RAIN': current_sprite_key = 'meteor'
        self.image = pygame.transform.flip(self.sprites[current_sprite_key], not self.facing_right, False)
    def draw(self, surface):
        if self.flash_timer > 0: surface.blit(self.sprites['hurt'], self.rect)
        else: surface.blit(self.image, self.rect)
    def perform_action(self, p_rect, pr, en, dt):
        action = self.actions[self.action_index]; name = action['name']
        if name in ('CHASE', 'COOLDOWN'): self.move(p_rect, dt, action.get('speed_multiplier', 1.0))
        elif name == 'FIRE_CONE':
            if self.action_timer > action['duration'] - dt * 2:
                base_angle = math.atan2(p_rect.centery - self.rect.centery, p_rect.centerx - self.rect.centerx)
                for spread in (-0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4): 
                    pr['enemy'].add(FireCone(self.rect.center, base_angle + spread))
        elif name == 'METEOR_RAIN':
            if self.action_timer > action['duration'] - dt * 2:
                for _ in range(40):
                    target = (random.randint(80, self.screen_width-80), random.randint(120, self.screen_height-40))
                    pr['enemy'].add(Meteor(target))