import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(True)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.new_game()
        self.paused = False
        self.menu_items = ["ГРОМКОСТЬ -", "ГРОМКОСТЬ +", "ВЫЙТИ"]
        self.menu_selected = 0
        self.volume = 0.5
        pg.mixer.music.set_volume(self.volume)
        self.font_menu = pg.font.SysFont('Comic Sans MS', 48, bold=True)

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

    def update(self):
        if self.paused:
            pg.display.flip()
            self.delta_time = self.clock.tick(FPS)
            return
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        self.object_renderer.draw()
        self.weapon.draw()
        if self.paused:
            self.draw_pause_menu()
            return
        font = pg.font.SysFont('Comic Sans MS', 48, bold=True)
        screen_w, screen_h = self.screen.get_size()
        health_text = font.render(f'HP: {self.player.health}', True, (255, 0, 0))
        health_rect = health_text.get_rect(bottomright=(screen_w - 30, screen_h - 30))
        self.screen.blit(health_text, health_rect)
        stamina_text = font.render(f'STAM: {int(self.player.stamina)}', True, (0, 255, 0))
        stamina_rect = stamina_text.get_rect(bottomleft=(30, screen_h - 90))
        self.screen.blit(stamina_text, stamina_rect)
        now = pg.time.get_ticks()
        cd = max(0, (self.player.heal_cooldown - (now - self.player.last_heal)) // 1000)
        heal_cd_text = font.render(f'HEAL CD: {cd}s', True, (0, 200, 255))
        heal_cd_rect = heal_cd_text.get_rect(bottomleft=(30, screen_h - 30))
        self.screen.blit(heal_cd_text, heal_cd_rect)

    def draw_pause_menu(self):
        overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        w, h = self.screen.get_size()
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 0) if i == self.menu_selected else (255, 255, 255)
            text = self.font_menu.render(item, True, color)
            rect = text.get_rect(center=(w // 2, h // 2 + i * 60))
            self.screen.blit(text, rect)
        vol_text = self.font_menu.render(f'ГРОМКОСТЬ: {int(self.volume * 100)}%', True, (0, 200, 255))
        vol_rect = vol_text.get_rect(center=(w // 2, h // 2 - 100))
        self.screen.blit(vol_text, vol_rect)

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            if self.paused:
                self.handle_menu_event(event)
                continue
            self.player.single_fire_event(event)
            if event.type == pg.KEYDOWN and event.key == pg.K_e:
                self.player.try_heal()
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                self.paused = True

    def handle_menu_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                self.menu_selected = (self.menu_selected - 1) % len(self.menu_items)
            elif event.key == pg.K_DOWN:
                self.menu_selected = (self.menu_selected + 1) % len(self.menu_items)
            elif event.key == pg.K_RETURN:
                if self.menu_selected == 0:
                    self.volume = max(0, self.volume - 0.1)
                    pg.mixer.music.set_volume(self.volume)
                elif self.menu_selected == 1:
                    self.volume = min(1, self.volume + 0.1)
                    pg.mixer.music.set_volume(self.volume)
                elif self.menu_selected == 2:
                    pg.quit()
                    sys.exit()
            elif event.key == pg.K_TAB or event.key == pg.K_ESCAPE:
                self.paused = False

if __name__ == '__main__':
    game = Game()
    while True:
        game.check_events()
        game.update()
        game.draw()