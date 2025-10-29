# ui.py
import pygame
import os
from settings import *

# =========================
#   Helpers (sprites / fonte)
# =========================

def load_sprite(file_name, size=None):
    path = os.path.join('assets', 'sprites', file_name)
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            return pygame.transform.scale(image, size)
        return image
    except pygame.error:
        print(f"AVISO: Sprite '{path}' não encontrado. Usando fallback.")
        w, h = size if size else (50, 50)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill(MAGENTA)
        return surf

def load_medieval_font(size):
    """
    Tenta carregar uma fonte 'medieval' de assets/fonts/.
    Coloque um desses arquivos em assets/fonts/:
      - UnifrakturCook-Bold.ttf
      - Cinzel-Black.ttf
      - MedievalSharp.ttf
      - OldLondon.ttf
    Se não achar, usa a fonte padrão do pygame.
    """
    candidates = [
        os.path.join('assets', 'fonts', 'UnifrakturCook-Bold.ttf'),
        os.path.join('assets', 'fonts', 'Cinzel-Black.ttf'),
        os.path.join('assets', 'fonts', 'MedievalSharp.ttf'),
        os.path.join('assets', 'fonts', 'OldLondon.ttf'),
    ]
    for p in candidates:
        try:
            if os.path.exists(p):
                return pygame.font.Font(p, size)
        except Exception:
            pass
    return pygame.font.Font(None, size)

# cache do fundo de menu
_MENU_BG = None
def get_menu_bg():
    global _MENU_BG
    if _MENU_BG is None:
        _MENU_BG = load_sprite('Fundo.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
    return _MENU_BG

# =========================
#   Layout / Grid
# =========================
GRID = 16
MARGIN = 16
SHOW_FPS = False  # deixe True se quiser ver o FPS no HUD

def g(n):  # múltiplo de grid (sempre int)
    return int(n * GRID)

def snap(v):
    return int(round(v / GRID) * GRID)

# =========================
#   Paleta / Estilo medieval
# =========================
PARCHMENT = (222, 209, 171)
PARCHMENT_DARK = (190, 176, 140)
GOLD = (196, 154, 0)
GOLD_LIGHT = (236, 204, 84)
HEALTH_RED = (210, 46, 46)
HEALTH_DARK = (120, 20, 20)
MANA_BLUE = (70, 90, 180)
MANA_LIGHT = (120, 150, 230)
INK = (35, 30, 25)

# =========================
#   Utilitários de desenho
# =========================
def draw_gradient_rect(surface, rect, color_top, color_bottom):
    x, y, w, h = rect
    x = int(x); y = int(y); w = int(w); h = int(h)
    if h <= 0 or w <= 0:
        return
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w - 1, y + i))

def draw_parchment_panel(surface, rect, border=3, corner_radius=10, alpha=200):
    x, y, w, h = rect
    x = int(x); y = int(y); w = int(w); h = int(h)
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*PARCHMENT, alpha), (0, 0, w, h), border_radius=corner_radius)
    pygame.draw.rect(panel, (*PARCHMENT_DARK, int(alpha * 0.35)), (3, 3, w - 6, h - 6), border_radius=corner_radius)
    pygame.draw.rect(panel, (*GOLD, alpha), (0, 0, w, h), border, border_radius=corner_radius)
    surface.blit(panel, (x, y))

def draw_fancy_bar(surface, x, y, w, h, ratio, fg_top, fg_bottom, label_text, label_color=INK, tick_every=10):
    x = int(x); y = int(y); w = int(w); h = int(h)
    ratio = max(0.0, min(1.0, float(ratio)))

    pygame.draw.rect(surface, GOLD, (x - 3, y - 3, w + 6, h + 6), border_radius=8)
    pygame.draw.rect(surface, GOLD_LIGHT, (x - 2, y - 2, w + 4, h + 4), 2, border_radius=8)
    pygame.draw.rect(surface, PARCHMENT, (x, y, w, h), border_radius=6)

    fill_w = int(w * ratio)
    if fill_w > 0:
        draw_gradient_rect(surface, (x, y, fill_w, h), fg_top, fg_bottom)
        pygame.draw.rect(surface, (0, 0, 0), (x, y, fill_w, h), 1, border_radius=6)

    if tick_every and w > 0:
        step = max(1, w // int(tick_every))
        for i in range(0, w, step):
            pygame.draw.line(surface, (0, 0, 0), (x + i, y + 1), (x + i, y + h - 2), 1)

    pygame.draw.rect(surface, INK, (x, y, w, h), 2, border_radius=6)

    if label_text:
        lbl_font = load_medieval_font(24)
        lbl_surf = lbl_font.render(label_text, True, label_color)
        surface.blit(lbl_surf, (x + 8, y - lbl_surf.get_height()))

def draw_heart(surface, center, size=14, color=(200, 0, 0)):
    x, y = center
    x = int(x); y = int(y)
    r = int(size // 3)
    pygame.draw.circle(surface, color, (x - r, y - r), r)
    pygame.draw.circle(surface, color, (x + r, y - r), r)
    pygame.draw.polygon(surface, color, [(x - 2 * r, y - r), (x + 2 * r, y - r), (x, y + 2 * r)])

def draw_scroll_tag(surface, text, pos):
    font = load_medieval_font(22)
    txt = font.render(text, True, INK)
    pad = 8
    rect = pygame.Rect(0, 0, txt.get_width() + pad * 2, txt.get_height() + pad * 2)
    rect.topleft = (int(pos[0]), int(pos[1]))
    draw_parchment_panel(surface, rect, border=2, corner_radius=8, alpha=210)
    surface.blit(txt, (rect.x + pad, rect.y + pad))

def draw_ability_slot(surface, center, size, key_text, cooldown_ms, cooldown_total_ms):
    x, y = center
    x = int(x); y = int(y)
    r = int(size // 2)

    # hexágono estilo runa
    pts = []
    for i in range(6):
        ang = pygame.math.Vector2(1, 0).rotate(i * 60)
        pts.append((x + int(ang.x * r), y + int(ang.y * r)))
    pygame.draw.polygon(surface, GOLD, pts, 0)
    pygame.draw.polygon(surface, INK, pts, 3)
    inner_r = int(r * 0.82)
    inner_pts = []
    for i in range(6):
        ang = pygame.math.Vector2(1, 0).rotate(i * 60)
        inner_pts.append((x + int(ang.x * inner_r), y + int(ang.y * inner_r)))
    pygame.draw.polygon(surface, (40, 40, 40), inner_pts, 0)
    pygame.draw.polygon(surface, GOLD_LIGHT, inner_pts, 2)

    # cooldown overlay
    if cooldown_total_ms and cooldown_ms > 0:
        ratio = max(0.0, min(1.0, cooldown_ms / float(cooldown_total_ms)))
        h = int(r * 2 * ratio)
        overlay = pygame.Surface((r * 2, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (x - r, y + r - h))

        sec = max(0, int((cooldown_ms + 999) // 1000))
        num = pygame.font.Font(None, 28).render(str(sec), True, WHITE)
        surface.blit(num, num.get_rect(center=(x, y)))
    else:
        glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 120, 80), (r, r), r)
        surface.blit(glow, (x - r, y - r))

    # letra da tecla
    key = load_medieval_font(24).render(key_text, True, WHITE)
    surface.blit(key, key.get_rect(center=(x, y)))

# =========================
#   Cards / Level Up
# =========================
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
            "PASSIVE_HEAL": "Pergaminho-regen.png",
        }
        sprite_filename = sprite_map.get(upgrade_id, "Pergaminho-Cooldown.png")
        self.image = load_sprite(sprite_filename, (160, 240))
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

def draw_tooltip(surface, card):
    font_title = load_medieval_font(28)
    font_desc = pygame.font.Font(None, 24)
    title_surf = font_title.render(card.title, True, INK)
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
    screen.blit(overlay, (0, 0))
    title_text = load_medieval_font(52).render("LEVEL UP! ESCOLHA UM PERGAMINHO:", True, YELLOW)
    screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, g(6))))
    hovered_card = None
    for card in upgrade_cards:
        card.draw(screen)
        if card.is_hovered():
            hovered_card = card
    if hovered_card:
        draw_tooltip(screen, hovered_card)

# =========================
#   Boss UI (TOP-LEFT)
# =========================
def draw_boss_health_bar(surface, boss):
    if boss and boss.alive():
        # barra no topo-esquerdo
        x = MARGIN
        y = MARGIN
        w, h = g(28), g(1.5)       # 448 x 24
        ratio = boss.hp / boss.max_hp if boss.max_hp > 0 else 0

        # chapinhas laterais
        pygame.draw.rect(surface, GOLD, (x - g(2), y - 6, g(2), h + 12), border_radius=6)
        pygame.draw.rect(surface, GOLD, (x + w,    y - 6, g(2), h + 12), border_radius=6)

        draw_fancy_bar(surface, x, y, w, h, ratio, (150, 40, 40), (90, 20, 20), boss.name, label_color=WHITE, tick_every=20)

def draw_boss_prompt(screen, font):
    # selo pequeno "CHEFE!" abaixo da barra do chefe (top-left)
    tag_font = load_medieval_font(24)
    text = tag_font.render("CHEFE!", True, YELLOW)
    bg = pygame.Surface((text.get_width() + 12, text.get_height() + 6), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 120))
    rect = bg.get_rect(topleft=(MARGIN + g(10), MARGIN + g(1.8)))  # alinhado próximo à barra
    screen.blit(bg, rect)
    screen.blit(text, text.get_rect(center=rect.center))

# =========================
#   HUD (ancorado nas bordas)
# =========================
def draw_hud(screen, player, score, kills, font, fps):
    # --- Painel Score/Abates (TOP-RIGHT) ---
    right_w = g(14)  # 224
    right_rect = pygame.Rect(SCREEN_WIDTH - MARGIN - right_w, MARGIN, right_w, g(3))
    draw_parchment_panel(screen, right_rect, border=2, corner_radius=10, alpha=210)

    line_font = load_medieval_font(22)
    txt = line_font.render(f"Score {score}  |  Abates {kills}", True, INK)
    screen.blit(txt, txt.get_rect(center=(right_rect.centerx, right_rect.centery)))

    if SHOW_FPS:
        fps_font = pygame.font.Font(None, 20)
        fps_surf = fps_font.render(f"{int(fps)} FPS", True, (220, 220, 220))
        screen.blit(fps_surf, (SCREEN_WIDTH - fps_surf.get_width() - MARGIN, right_rect.bottom + 4))

    # --- Painel HP/XP (BOTTOM-LEFT) ---
    panel_w = g(20)  # 320
    panel_h = g(6)   # 96
    panel_rect = pygame.Rect(MARGIN, SCREEN_HEIGHT - MARGIN - panel_h, panel_w, panel_h)
    draw_parchment_panel(screen, panel_rect, border=2, corner_radius=10, alpha=210)

    # HP
    hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 0
    bar_hp_x = panel_rect.x + g(1)
    bar_hp_y = panel_rect.y + g(0.6)
    bar_hp_w = panel_w - g(2)
    bar_hp_h = g(1.25)  # 20
    draw_heart(screen, (bar_hp_x - 10, bar_hp_y + bar_hp_h // 2), size=14, color=(200, 30, 30))
    draw_fancy_bar(screen, bar_hp_x, bar_hp_y, bar_hp_w, bar_hp_h, hp_ratio, HEALTH_RED, HEALTH_DARK, "Vita")

    # Texto HP discreto à direita
    small = load_medieval_font(20)
    hp_text = small.render(f"{int(player.hp)}/{player.max_hp}", True, INK)
    screen.blit(hp_text, (bar_hp_x + bar_hp_w - hp_text.get_width(), bar_hp_y - hp_text.get_height()))

    # XP + Level
    xp_ratio = player.xp / player.xp_to_next_level if player.xp_to_next_level > 0 else 1
    bar_xp_x = bar_hp_x
    bar_xp_y = panel_rect.bottom - g(1.9)  # sobe um pouco
    bar_xp_w = bar_hp_w
    bar_xp_h = g(1.0)  # 16
    draw_fancy_bar(screen, bar_xp_x, bar_xp_y, bar_xp_w, bar_xp_h, xp_ratio, MANA_LIGHT, MANA_BLUE, f"Lv. {player.level}", label_color=INK, tick_every=25)

    # --- Habilidades (BOTTOM-RIGHT) ---
    size = g(4)        # 64
    padding = g(1)     # 16
    total = 4
    total_w = total * size + (total - 1) * padding
    start_x = SCREEN_WIDTH - MARGIN - total_w + size // 2
    base_y = SCREEN_HEIGHT - MARGIN - size // 2

    abilities_info = [
        ("Q", player.valkyrie),
        ("E", player.shield),
        ("F", player.thunder_leap),
        ("R", player.phoenix_call),
    ]
    for i, (key, ability) in enumerate(abilities_info):
        cx = start_x + i * (size + padding)
        draw_ability_slot(screen, (cx, base_y), size, key, ability.cooldown_timer, ability.cooldown)

    # --- Efeito: borda pulsante quando HP baixo ---
    if hp_ratio < 0.25:
        t = pygame.time.get_ticks() / 250.0
        alpha = int(80 + 40 * (0.5 + 0.5 * pygame.math.sin(t)))
        border = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # moldura grossa nas bordas
        thickness = g(0.5)  # 8px
        pygame.draw.rect(border, (255, 0, 0, alpha), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), thickness)
        screen.blit(border, (0, 0))

# =========================
#   Background & Dia/Noite
# =========================
def draw_background(surface, grass_tile):
    """Preenche a tela com o tile de grama (ou outra textura)."""
    tile_w, tile_h = grass_tile.get_size()
    for x in range(0, SCREEN_WIDTH, tile_w):
        for y in range(0, SCREEN_HEIGHT, tile_h):
            surface.blit(grass_tile, (x, y))

def is_night(cycle_timer):
    cycle_duration = 120000
    time_of_day = (cycle_timer % cycle_duration) / cycle_duration
    return 0.55 < time_of_day < 0.95

def draw_day_night_cycle(surface, cycle_timer, player):
    cycle_duration = 120000
    time_of_day = (cycle_timer % cycle_duration) / cycle_duration
    darkness = 0
    if 0.5 < time_of_day < 1.0:
        if time_of_day < 0.75:
            darkness = int((time_of_day - 0.5) * 2 * 180)
        else:
            darkness = int((1.0 - time_of_day) * 2 * 180)
    darkness = max(0, min(darkness, 180))
    if darkness > 0:
        light_mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        light_mask.fill((0, 0, 0, darkness))
        pygame.draw.circle(light_mask, (0, 0, 0, 0), player.rect.center, 150)
        surface.blit(light_mask, (0, 0))

# =========================
#   Telas: Menu / Opções / Game Over
# =========================
def _draw_bg_with_overlay(screen, alpha=120):
    screen.blit(get_menu_bg(), (0, 0))
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (0, 0))

def draw_main_menu(screen, font, selected_index):
    _draw_bg_with_overlay(screen, alpha=140)
    title_font = load_medieval_font(96)
    subtitle_font = pygame.font.Font(None, 36)

    title = title_font.render("ACTION RPG", True, YELLOW)
    shadow = title_font.render("ACTION RPG", True, BLACK)
    screen.blit(shadow, shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, g(10) + 2)))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, g(10))))

    subtitle = subtitle_font.render("Top-Down Horde Survival", True, GREY)
    screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, g(12))))

    menu_items = ["Iniciar Jogo", "Opções", "Sair"]
    for i, item in enumerate(menu_items):
        color = YELLOW if i == selected_index else WHITE
        text = pygame.font.Font(None, 40).render(item, True, color)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, g(20) + i * g(3))))

    hint = subtitle_font.render("↑/↓ para navegar • Enter para confirmar", True, GREY)
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - g(3))))

def draw_options(screen, font):
    _draw_bg_with_overlay(screen, alpha=140)
    title_font = load_medieval_font(72)
    title = title_font.render("Opções", True, YELLOW)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, g(8))))

    lines = [
        "Controles:",
        "  • WASD - Mover",
        "  • Mouse - Mirar / Atirar",
        "  • Q / E / F / R - Habilidades",
        "  • ESC - Pausar",
        " ",
        "Dica: inimigos ficam mais fortes à noite!",
    ]
    small = pygame.font.Font(None, 32)
    for i, line in enumerate(lines):
        color = WHITE if not line.strip().startswith("Dica") else GREY
        txt = small.render(line, True, color)
        screen.blit(txt, (SCREEN_WIDTH // 2 - g(14), g(12) + i * g(2)))

    back = small.render("Pressione ESC para voltar ao Menu", True, GREY)
    screen.blit(back, back.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - g(3))))

def draw_game_over(screen, font, selected_index):
    _draw_bg_with_overlay(screen, alpha=170)
    title_font = load_medieval_font(96)
    title = title_font.render("GAME OVER", True, RED)
    shadow = title_font.render("GAME OVER", True, BLACK)
    screen.blit(shadow, shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, g(12) + 2)))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, g(12))))

    options = ["Reiniciar", "Voltar ao Menu"]
    for i, opt in enumerate(options):
        color = YELLOW if i == selected_index else WHITE
        text = pygame.font.Font(None, 40).render(opt, True, color)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, g(18) + i * g(3))))

def draw_pause(screen, font):
    pause_font = load_medieval_font(74)
    pause_text = pause_font.render("PAUSADO", True, WHITE)
    screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
