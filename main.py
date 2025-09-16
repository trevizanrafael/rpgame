# main.py
import pygame
import random
import os

from settings import *
import ui
import combat
from player import Player, Arrow
from enemy import Grunt, Tank, Bomber, Assassin, TitanusRex, Morgana, Draken
from particles import Particle

# --- Variáveis Globais de Estado ---
player, enemies, bosses, projectiles, score, kills = None, None, None, None, 0, 0
game_state, current_boss = 'PLAYING', None; current_music = None
spawned_bosses = set()
upgrade_cards = pygame.sprite.Group()

def load_sounds():
    sounds = {}; sound_files = {'shoot': "shoot.wav", 'hit': "hit.wav", 'enemy_death': "enemy_death.wav", 'game_over': "game_over.wav"}
    class DummySound:
        def play(self): pass
    dummy = DummySound()
    for name, path in sound_files.items():
        try: sounds[name] = pygame.mixer.Sound(os.path.join('assets', 'sounds', path))
        except (pygame.error, FileNotFoundError): sounds[name] = dummy
    return sounds

def play_music(track):
    global current_music
    if track == current_music: return
    
    music_map = {'background': 'background_music.mp3', 'boss': 'RAFAEL.mp3'}
    file = music_map.get(track)
    
    if file:
        try:
            # ALTERADO: Removida a subpasta 'music' do caminho
            full_path = os.path.join('assets', file)
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            current_music = track
        except pygame.error as e:
            print(f"Aviso: Arquivo de música '{file}' não encontrado ou com erro: {e}")
            current_music = track

def reset_game():
    global player, enemies, bosses, projectiles, score, kills, game_state, current_boss, spawned_bosses
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    enemies, bosses = pygame.sprite.Group(), pygame.sprite.Group()
    projectiles = {
        'player': pygame.sprite.Group(), 'player_explosions': pygame.sprite.Group(), 
        'enemy': pygame.sprite.Group(), 'environment': pygame.sprite.Group(),
        'vfx': pygame.sprite.Group(), 'enemy_explosions': pygame.sprite.Group()
    }
    score, kills = 0, 0; game_state = 'PLAYING'; current_boss = None
    spawned_bosses = set(); play_music('background'); upgrade_cards.empty()

def get_available_enemies(player_level):
    enemy_pool = [Grunt, Tank]
    if player_level >= 3: enemy_pool.append(Bomber)
    if player_level >= 4: enemy_pool.append(Assassin)
    return enemy_pool

def handle_state_transitions(boss_spawn_triggers):
    global game_state, current_boss, spawned_bosses, kills, score, player
    if game_state == 'PLAYING':
        for k, boss_class in boss_spawn_triggers.items():
            if kills >= k and boss_class not in spawned_bosses:
                game_state = 'BOSS_FIGHT'; enemies.empty()
                current_boss = boss_class((SCREEN_WIDTH, SCREEN_HEIGHT))
                bosses.add(current_boss); spawned_bosses.add(boss_class)
                pygame.time.set_timer(spawn_event, 0)
                player.rect.center = (100, SCREEN_HEIGHT / 2); play_music('boss')
                return
    elif game_state == 'BOSS_FIGHT' and current_boss and not current_boss.alive():
        game_state = 'PLAYING'; current_boss = None
        pygame.time.set_timer(spawn_event, 2000); score += 500; play_music('background')

# --- Loop Principal do Jogo ---
def main():
    global score, kills, game_state, current_boss, spawn_event, projectiles, player, enemies, bosses, spawned_bosses
    pygame.init(); pygame.mixer.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Action RPG - Reverted")
    clock, font = pygame.time.Clock(), pygame.font.Font(None, 36)
    
    sounds = load_sounds()
    grass_tile = ui.load_sprite('grama.png', (64,64))
    boss_spawn_triggers = {2: TitanusRex, 4: Morgana, 7: Draken}
    reset_game()
    
    spawn_event, SHAKE_EVENT = pygame.USEREVENT + 1, pygame.USEREVENT + 2
    pygame.time.set_timer(spawn_event, 2000)
    shake_timer, shake_magnitude = 0, 0
    running = True; cycle_timer = 0

    while running:
        dt = clock.tick(FPS)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state in ['PLAYING', 'BOSS_FIGHT']: game_state = 'PAUSED'
                    elif game_state == 'PAUSED': game_state = 'PLAYING' if not current_boss else 'BOSS_FIGHT'
                if event.key == pygame.K_p: reset_game()
            if event.type == SHAKE_EVENT: shake_timer, shake_magnitude = event.duration, event.magnitude

            if game_state == 'LEVEL_UP':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for card in upgrade_cards:
                        if card.rect.collidepoint(event.pos):
                            player.apply_upgrade(card.upgrade_id)
                            game_state = 'PLAYING' if not current_boss else 'BOSS_FIGHT'
                            upgrade_cards.empty()
                            break
                continue
            
            if game_state in ['PLAYING', 'BOSS_FIGHT'] and player.hp > 0:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    projectiles['player'].add(Arrow(player.rect.center, pygame.mouse.get_pos())); sounds['shoot'].play()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: player.valkyrie.activate(player, projectiles, sounds)
                    if event.key == pygame.K_e: player.shield.activate(player, projectiles, sounds)
                    if event.key == pygame.K_f: player.thunder_leap.activate(player, projectiles, sounds)
                    if event.key == pygame.K_r: player.phoenix_call.activate(player, projectiles, sounds)

            if event.type == spawn_event and game_state == 'PLAYING':
                enemy_class = random.choice(get_available_enemies(player.level))
                enemies.add(enemy_class((SCREEN_WIDTH, SCREEN_HEIGHT), ui.is_night(cycle_timer)))

        if game_state in ['PLAYING', 'BOSS_FIGHT']:
            cycle_timer += dt
            handle_state_transitions(boss_spawn_triggers)
            
            player.update(projectiles, dt)
            enemies.update(player.rect, projectiles, enemies, dt)
            bosses.update(player.rect, projectiles, enemies, dt)
            for group in projectiles.values(): group.update(dt)
            
            score_change, kills_change = combat.handle_collisions(player, enemies, bosses, projectiles, sounds)
            score += score_change; kills += kills_change
            
            if player.leveled_up_flag:
                game_state = 'LEVEL_UP'
                player.leveled_up_flag = False
                upgrade_cards.empty()
                card_positions = [(SCREEN_WIDTH/2 - 200, SCREEN_HEIGHT/2), (SCREEN_WIDTH/2, SCREEN_HEIGHT/2), (SCREEN_WIDTH/2 + 200, SCREEN_HEIGHT/2)]
                for i, upgrade_data in enumerate(player.available_upgrades):
                    title, desc, up_id = upgrade_data
                    card = ui.UpgradeCard(card_positions[i][0], card_positions[i][1], up_id, title, desc)
                    upgrade_cards.add(card)

            if player.hp <= 0: game_state = 'GAME_OVER'; sounds['game_over'].play()

        world_surface.fill(BLACK)
        ui.draw_background(world_surface, grass_tile)
        player.draw(world_surface)

        for group in [enemies, bosses, *projectiles.values()]:
            for sprite in group:
                if hasattr(sprite, 'draw'): sprite.draw(world_surface)
        ui.draw_day_night_cycle(world_surface, cycle_timer, player)
        render_offset = [0, 0]
        if shake_timer > 0: shake_timer -= dt; render_offset = [random.randint(-shake_magnitude, shake_magnitude) for _ in range(2)]
        screen.fill(BLACK); screen.blit(world_surface, render_offset)
        
        ui.draw_hud(screen, player, score, kills, font, clock.get_fps())
        if game_state == 'BOSS_FIGHT':
            ui.draw_boss_health_bar(screen, current_boss); ui.draw_boss_prompt(screen, font)
        
        if game_state == 'GAME_OVER': ui.draw_game_over(screen, font)
        elif game_state == 'PAUSED': ui.draw_pause(screen, font)
        elif game_state == 'LEVEL_UP': ui.draw_level_up_screen(screen, font, upgrade_cards)
        
        pygame.display.flip()
        
    pygame.quit()

if __name__ == '__main__':
    main()