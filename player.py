# player.py
import pygame
import math
import random
from settings import *
from particles import create_particles

class Ability:
    def __init__(self, cooldown): self.cooldown = cooldown; self.cooldown_timer = 0
    def update_cooldown(self, dt):
        if self.cooldown_timer > 0: self.cooldown_timer -= dt
class InstantAbility(Ability):
    def activate(self, p, pr, s):
        if self.cooldown_timer <= 0: self.cooldown_timer = self.cooldown; self.effect(p, pr, s); return True
        return False
    def effect(self, p, pr, s): pass
class DurationAbility(Ability):
    def __init__(self, cooldown, duration):
        super().__init__(cooldown); self.duration = duration; self.active = False; self.active_timer = 0; self.sprite = None
    def activate(self, p, pr, s):
        if self.cooldown_timer <= 0 and not self.active:
            self.active = True; self.cooldown_timer = self.cooldown; self.active_timer = self.duration
            self.on_activate(p, pr, s); return True
        return False
    def update(self, player, projectiles, dt):
        self.update_cooldown(dt)
        if self.active:
            self.active_timer -= dt
            if self.sprite: self.sprite.follow(player.rect.center, dt)
            if self.active_timer <= 0: self.active = False; self.on_deactivate(projectiles)
    def on_activate(self, p, pr, s): pass
    def on_deactivate(self, projectiles):
        if self.sprite: self.sprite.kill(); self.sprite = None
    def draw(self, surface):
        if self.active and self.sprite: self.sprite.draw(surface)
class BaseAuraSprite(pygame.sprite.Sprite):
    def __init__(self, center_pos, radius):
        super().__init__(); self.radius = radius; self.angle = 0
    def follow(self, player_center, dt): self.rect.center = player_center
    def draw(self, surface): surface.blit(self.image, self.rect)
class ShieldSprite(BaseAuraSprite):
    def __init__(self, center_pos):
        super().__init__(center_pos, 40)
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*CYAN, 128), (self.radius, self.radius), self.radius, 5)
        self.rect = self.image.get_rect(center=center_pos)
class ValkyrieSprite(BaseAuraSprite):
    def __init__(self, center_pos):
        super().__init__(center_pos, 100)
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center_pos)
    def follow(self, player_center, dt):
        super().follow(player_center, dt); self.angle = (self.angle + 0.4 * dt) % 360; self.image.fill((0,0,0,0))
        for i in range(3):
            rad = math.radians(self.angle + i * 120)
            x, y = self.radius + math.cos(rad) * (self.radius-10), self.radius + math.sin(rad) * (self.radius-10)
            pygame.draw.circle(self.image, YELLOW, (int(x), int(y)), 8)
class Shield(DurationAbility):
    def __init__(self): super().__init__(cooldown=5000, duration=2000)
    def on_activate(self, p, pr, s): self.sprite = ShieldSprite(p.rect.center)
class Valkyrie(DurationAbility):
    def __init__(self): super().__init__(cooldown=8000, duration=3000)
    def on_activate(self, p, pr, s): self.sprite = ValkyrieSprite(p.rect.center); pr['vfx'].add(self.sprite)
class ThunderLeap(InstantAbility):
    def __init__(self): super().__init__(cooldown=10000)
    def effect(self, p, pr, s): p.rect.center = pygame.mouse.get_pos(); pr['player_explosions'].add(LeapExplosion(p.rect.center))
class PhoenixCall(InstantAbility):
    def __init__(self): super().__init__(cooldown=20000)
    def effect(self, p, pr, s): pr['player'].add(Phoenix(p.rect.center, pygame.mouse.get_pos()))
class LeapExplosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__(); self.radius = 80
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*YELLOW, 200), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=center); self.lifetime = 200; self.damage = 60
    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0: self.kill()
    def draw(self, surface): surface.blit(self.image, self.rect)
class Phoenix(pygame.sprite.Sprite):
    def __init__(self, start, target):
        super().__init__(); self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, FIRE_RED, self.image.get_rect()); self.rect = self.image.get_rect(center=start)
        dx, dy = target[0] - start[0], target[1] - start[1]; dist = math.hypot(dx, dy)
        self.vel_x, self.vel_y = (dx/dist)*10 if dist>0 else 0, (dy/dist)*10 if dist>0 else 0
        self.hit_enemies = set()
    def update(self, dt):
        move_speed = dt / 16.67; self.rect.x += self.vel_x * move_speed; self.rect.y += self.vel_y * move_speed
        if not pygame.display.get_surface().get_rect().colliderect(self.rect): self.kill()
    def draw(self, surface): surface.blit(self.image, self.rect)
class Arrow(pygame.sprite.Sprite):
    def __init__(self, start, target):
        super().__init__(); self.image = pygame.Surface([10, 3]); self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=start)
        dx, dy = target[0] - start[0], target[1] - start[1]; dist = math.hypot(dx, dy)
        self.vel_x, self.vel_y = (dx/dist)*12 if dist>0 else 0, (dy/dist)*12 if dist>0 else 0
    def update(self, dt):
        move_speed = dt / 16.67; self.rect.x += self.vel_x * move_speed; self.rect.y += self.vel_y * move_speed
        if not pygame.display.get_surface().get_rect().colliderect(self.rect): self.kill()
    def draw(self, surface): surface.blit(self.image, self.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(); self.image = pygame.Surface([40, 40]); self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y)); self.speed = 5
        self.max_hp = 100; self.hp = 100; self.damage_cooldown_duration = 1000
        self.damage_cooldown_timer = 0; self.flash_timer = 0; self.flash_duration = 100
        self.shield = Shield(); self.valkyrie = Valkyrie()
        self.thunder_leap = ThunderLeap(); self.phoenix_call = PhoenixCall()
        self.duration_abilities = [self.shield, self.valkyrie]
        self.instant_abilities = [self.thunder_leap, self.phoenix_call]
        self.level = 1; self.xp = 0; self.xp_to_next_level = 100
        self.available_upgrades = []; self.leveled_up_flag = False
        self.has_fire_arrows = False; self.has_chain_lightning = False; self.has_passive_heal = False
        self.passive_heal_timer = 0; self.passive_heal_interval = 2500

    def gain_xp(self, amount):
        self.xp += amount
    
    def level_up(self):
        self.level += 1; self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        self.hp = self.max_hp; self.available_upgrades = self.get_upgrade_options()
        self.leveled_up_flag = True

    def get_upgrade_options(self):
        options_pool = [
            ("Vida Máxima", "+20 de HP Máximo e cura completa.", "HP_MAX"), 
            ("Agilidade", "Reduz todos os cooldowns em 10%.", "COOLDOWN")
        ]
        if not self.has_fire_arrows: options_pool.append(("PASSIVA: Flechas de Fogo", "Aplica dano de queimadura por 3s.", "FIRE_ARROWS"))
        if not self.has_chain_lightning: options_pool.append(("PASSIVA: Flechas Elétricas", "O dano ricocheteia para um inimigo próximo.", "CHAIN_LIGHTNING"))
        if not self.has_passive_heal: options_pool.append(("PASSIVA: Regeneração", "Cura 10 de HP a cada 2.5 segundos.", "PASSIVE_HEAL"))
        return random.sample(options_pool, k=min(3, len(options_pool)))

    def apply_upgrade(self, upgrade_id):
        if upgrade_id == "HP_MAX": self.max_hp += 20; self.hp += 20
        elif upgrade_id == "COOLDOWN":
            for ability in self.duration_abilities + self.instant_abilities: ability.cooldown = int(ability.cooldown * 0.9)
        elif upgrade_id == "FIRE_ARROWS": self.has_fire_arrows = True
        elif upgrade_id == "CHAIN_LIGHTNING": self.has_chain_lightning = True
        elif upgrade_id == "PASSIVE_HEAL": self.has_passive_heal = True

    # ALTERADO: Assinatura da função update (sem 'obstacles')
    def update(self, projectiles, dt):
        if self.xp >= self.xp_to_next_level: self.level_up()
        if self.has_passive_heal:
            self.passive_heal_timer += dt
            if self.passive_heal_timer >= self.passive_heal_interval:
                self.passive_heal_timer = 0; self.hp = min(self.max_hp, self.hp + 10)
        keys = pygame.key.get_pressed(); move_speed = self.speed * (dt / 16.67)
        moved = False
        if keys[pygame.K_w]: self.rect.y -= move_speed; moved = True
        if keys[pygame.K_s]: self.rect.y += move_speed; moved = True
        if keys[pygame.K_a]: self.rect.x -= move_speed; moved = True
        if keys[pygame.K_d]: self.rect.x += move_speed; moved = True
        if moved and random.random() < 0.2: create_particles(self.rect.midbottom, 'dust', projectiles['vfx'])
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())
        if self.damage_cooldown_timer > 0: self.damage_cooldown_timer -= dt
        if self.flash_timer > 0: self.flash_timer -= dt
        for ability in self.duration_abilities: ability.update(self, projectiles, dt)
        for ability in self.instant_abilities: ability.update_cooldown(dt)
            
    def take_damage(self, amount):
        if not self.shield.active and self.damage_cooldown_timer <= 0:
            self.hp -= amount; self.flash_timer = self.flash_duration
            self.damage_cooldown_timer = self.damage_cooldown_duration
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 2, duration=200, magnitude=5))

    def draw(self, surface):
        color = WHITE if self.flash_timer > 0 else BLUE
        self.image.fill(color); surface.blit(self.image, self.rect)
        for ability in self.duration_abilities: ability.draw(surface)
