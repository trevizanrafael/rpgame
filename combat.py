# combat.py
import pygame
import math
from player import Phoenix, ValkyrieSprite, Arrow, LeapExplosion
from enemy import Boss, Illusion, Meteor
from particles import create_particles, LightningBolt

def handle_collisions(player, enemies, bosses, projectiles, sounds):
    score_change = 0
    kills_change = 0
    all_enemies = pygame.sprite.Group(enemies, bosses)

    def on_enemy_death(enemy):
        nonlocal score_change, kills_change
        if player.gain_xp(getattr(enemy, 'xp_value', 5)):
            player.level_up()
        
        create_particles(enemy.rect.center, 'blood', projectiles['vfx'])
        score_change += getattr(enemy, 'score_value', 10)
        if not isinstance(enemy, (Boss, Illusion)):
            kills_change += 1
        sounds['enemy_death'].play()

    # Colisões de projéteis do jogador com inimigos
    for proj in projectiles['player']:
        hits = pygame.sprite.spritecollide(proj, all_enemies, False)
        for enemy in hits:
            if isinstance(proj, Phoenix):
                if enemy not in proj.hit_enemies:
                    enemy.take_damage(50, sounds)
                    proj.hit_enemies.add(enemy)
            elif isinstance(proj, ValkyrieSprite):
                if pygame.time.get_ticks() - getattr(enemy, 'last_hit_time', 0) > 300:
                    enemy.take_damage(15, sounds)
                    enemy.last_hit_time = pygame.time.get_ticks()
            elif isinstance(proj, Arrow):
                kb = (0, 0)
                norm_vel = math.hypot(proj.vel_x, proj.vel_y)
                if norm_vel > 0:
                    kb = ((proj.vel_x / norm_vel) * 10, (proj.vel_y / norm_vel) * 10)
                
                enemy.take_damage(25, sounds, knockback=kb)
                proj.kill()
                
                if player.has_fire_arrows:
                    enemy.apply_effect('fire', 3000, 5)
                if player.has_chain_lightning:
                    for other_enemy in list(enemies) + list(bosses):
                        if other_enemy != enemy and math.hypot(enemy.rect.centerx - other_enemy.rect.centerx, enemy.rect.centery - other_enemy.rect.centery) < 150:
                            other_enemy.take_damage(15, sounds)
                            projectiles['vfx'].add(LightningBolt(enemy.rect.center, other_enemy.rect.center))
                            break
            
            if not enemy.alive():
                on_enemy_death(enemy)

    # Colisões de explosões do jogador com inimigos
    for explosion in projectiles['player_explosions']:
        hits = pygame.sprite.spritecollide(explosion, all_enemies, False)
        for enemy in hits:
            enemy.take_damage(explosion.damage, sounds)
        explosion.kill()

    # Colisões de coisas inimigas com o jogador
    if not player.shield.active:
        # NOVO: Lógica para dano de explosões inimigas no jogador
        for explosion in projectiles['enemy_explosions']:
            if explosion.rect.colliderect(player.rect):
                player.take_damage(explosion.damage)
            explosion.kill()

        for proj in projectiles['enemy']:
            if isinstance(proj, Meteor) and proj.exploded:
                if proj.rect.colliderect(player.rect) and not proj.has_damaged:
                    player.take_damage(proj.damage)
                    proj.has_damaged = True
            elif pygame.sprite.collide_rect(proj, player):
                player.take_damage(getattr(proj, 'damage', 10))
                if not isinstance(proj, Meteor):
                    proj.kill()
        
        if pygame.sprite.spritecollide(player, all_enemies, False):
            player.take_damage(20)

    # Colisões com o ambiente
    for cloud in projectiles.get('environment', []):
        if pygame.sprite.collide_rect(cloud, player):
            cloud.damage_player(player)

    return score_change, kills_change