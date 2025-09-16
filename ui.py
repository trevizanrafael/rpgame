# ui.py
import pygame
import os
from settings import *

# NOVO: Classe para os cards de upgrade (os pergaminhos)
class UpgradeCard(pygame.sprite.Sprite):
    def __init__(self, x, y, upgrade_id, title, description):
        super().__init__()
        self.upgrade_id = upgrade_id
        self.title = title
        self.description = description

        sprite_map = {
            "HP_MAX": "Pergaminho-VidaMax.png",
            "COOLDOWN": "Pergaminho-Cooldown.png",
            "FIRE_ARROWS": "Pergaminho-Fogo.png",
            "CHAIN_LIGHTNING": "Pergaminho-Raio.png",
            "PASSIVE_HEAL": "Pergaminho-regen.png"
        }
        sprite_filename = sprite_map.get(upgrade_id, "Pergaminho-Cooldown.png")
        
        self.image = load_sprite(sprite_filename, (160, 240))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

def load_sprite(file_name, size=None):
    path = os.path.join('assets', 'sprites', file_name)
    try:
        image = pygame.image.load(path).convert_alpha()
        if size: return pygame.transform.scale(image, size)
        return image
    except pygame.error:
        print(f"AVISO: Arquivo de sprite '{path}' não encontrado. Usando cor de fallback.")
        fallback_surface = pygame.Surface(size if size else (50,50)); fallback_surface.fill(MAGENTA)
        return fallback_surface

def draw_background(surface, grass_tile):
    w, h = grass_tile.get_size()
    for x in range(0, SCREEN_WIDTH, w):
        for y in range(0, SCREEN_HEIGHT, h): surface.blit(grass_tile, (x, y))

def is_night(cycle_timer):
    cycle_duration = 120000; time_of_day = (cycle_timer % cycle_duration) / cycle_duration
    return 0.55 < time_of_day < 0.95

def draw_day_night_cycle(surface, cycle_timer, player):
    cycle_duration = 120000; time_of_day = (cycle_timer % cycle_duration) / cycle_duration
    darkness = 0
    if 0.5 < time_of_day < 1.0:
        if time_of_day < 0.75: darkness = int((time_of_day - 0.5) * 2 * 180)
        else: darkness = int((1.0 - time_of_day) * 2 * 180)
    darkness = max(0, min(darkness, 180))
    if darkness > 0:
        light_mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA); light_mask.fill((0,0,0,darkness))
        pygame.draw.circle(light_mask, (0,0,0,0), player.rect.center, 150)
        surface.blit(light_mask, (0,0))

def draw_hud(screen, player, score, kills, font, fps):
    small_font = pygame.font.Font(None, 24)
    hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 0
    pygame.draw.rect(screen, GREY, (10, 10, 200, 25)); pygame.draw.rect(screen, FIRE_RED, (10, 10, 200 * hp_ratio, 25))
    pygame.draw.rect(screen, BLACK, (10, 10, 200, 25), 2)
    hp_text = small_font.render(f"{int(player.hp)} / {player.max_hp}", True, WHITE); screen.blit(hp_text, hp_text.get_rect(center=(110, 22)))
    xp_ratio = player.xp / player.xp_to_next_level if player.xp_to_next_level > 0 else 1
    pygame.draw.rect(screen, GREY, (10, 40, 200, 15)); pygame.draw.rect(screen, XP_COLOR, (10, 40, 200 * xp_ratio, 15))
    pygame.draw.rect(screen, BLACK, (10, 40, 200, 15), 2)
    xp_text = small_font.render(f"LVL {player.level}", True, WHITE); screen.blit(xp_text, xp_text.get_rect(midleft=(220, 48)))
    score_text = small_font.render(f"Score: {score}", True, WHITE); screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))
    kills_text = small_font.render(f"Abates: {kills}", True, WHITE); screen.blit(kills_text, (SCREEN_WIDTH - kills_text.get_width() - 10, 30))
    fps_text = small_font.render(f"FPS: {int(fps)}", True, WHITE); screen.blit(fps_text, (SCREEN_WIDTH - fps_text.get_width() - 10, 50))
    
    # ALTERADO: Habilidades corrigidas para o novo esquema de teclas
    abilities_info = [
        ("Q", player.valkyrie), ("E", player.shield),
        ("F", player.thunder_leap), ("R", player.phoenix_call)
    ]
    icon_size = 50; padding = 10; total_width = len(abilities_info) * icon_size + (len(abilities_info) - 1) * padding
    start_x = (SCREEN_WIDTH - total_width) / 2; y_pos = SCREEN_HEIGHT - icon_size - 10
    for i, (key, ability) in enumerate(abilities_info):
        x_pos = start_x + i * (icon_size + padding); pygame.draw.rect(screen, GREY, (x_pos, y_pos, icon_size, icon_size))
        if ability.cooldown > 0 and ability.cooldown_timer > 0:
            cd_ratio = ability.cooldown_timer / ability.cooldown
            overlay_height = int(icon_size * cd_ratio)
            overlay = pygame.Surface((icon_size, overlay_height), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); screen.blit(overlay, (x_pos, y_pos))
        pygame.draw.rect(screen, BLACK, (x_pos, y_pos, icon_size, icon_size), 2)
        key_text = font.render(key, True, WHITE); screen.blit(key_text, key_text.get_rect(center=(x_pos + icon_size / 2, y_pos + icon_size / 2)))

def draw_tooltip(surface, card):
    font_title = pygame.font.Font(None, 28)
    font_desc = pygame.font.Font(None, 24)
    title_surf = font_title.render(card.title, True, YELLOW)
    desc_surf = font_desc.render(card.description, True, WHITE)
    width = max(title_surf.get_width(), desc_surf.get_width()) + 20
    height = title_surf.get_height() + desc_surf.get_height() + 15
    tooltip_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    tooltip_surf.fill((0, 0, 0, 180))
    tooltip_surf.blit(title_surf, (10, 5))
    tooltip_surf.blit(desc_surf, (10, 10 + title_surf.get_height()))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    surface.blit(tooltip_surf, (mouse_x + 15, mouse_y + 15))

def draw_level_up_screen(screen, font, upgrade_cards):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0,0))
    title_text = pygame.font.Font(None, 60).render("LEVEL UP! ESCOLHA UM PERGAMINHO:", True, YELLOW)
    screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, 100)))
    hovered_card = None
    for card in upgrade_cards:
        card.draw(screen)
        if card.is_hovered():
            hovered_card = card
    if hovered_card:
        draw_tooltip(screen, hovered_card)

def draw_boss_health_bar(surface, boss):
    if boss and boss.alive():
        ratio = boss.hp / boss.max_hp if boss.max_hp > 0 else 0
        surface.blit(pygame.font.Font(None, 24).render(boss.name, True, WHITE), (400 - len(boss.name) * 5, 10))
        pygame.draw.rect(surface, BLACK, (200, 40, 400, 20), 2)
        pygame.draw.rect(surface, FIRE_RED, (200, 40, 400 * ratio, 20))

def draw_boss_prompt(screen, font):
    prompt_text = font.render("Derrote o CHEFE para continuar", True, YELLOW)
    bg_surface = pygame.Surface((prompt_text.get_width() + 20, prompt_text.get_height() + 10), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 128))
    screen.blit(bg_surface, bg_surface.get_rect(center=(screen.get_width() / 2, 80)))
    screen.blit(prompt_text, prompt_text.get_rect(center=(screen.get_width() / 2, 85)))

def draw_game_over(screen, font):
    game_over_font = pygame.font.Font(None, 74)
    game_over_text = game_over_font.render("GAME OVER", True, RED)
    restart_text = font.render("Pressione P para reiniciar", True, WHITE)
    screen.blit(game_over_text, (game_over_text.get_rect(center=(400, 270))))
    screen.blit(restart_text, (restart_text.get_rect(center=(400, 330))))

def draw_pause(screen, font):
    pause_font = pygame.font.Font(None, 74)
    pause_text = pause_font.render("PAUSADO", True, WHITE)
    screen.blit(pause_text, (pause_text.get_rect(center=(400, 300))))