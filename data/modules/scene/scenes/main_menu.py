import settings
from ..scene import scene
from data.modules.type.stellar_obj import star, planet, moon, background_stars
from data.modules.services.gui import *


class main_menu(scene):
    def __init__(self, game):
        super().__init__(game)
        self.planet_colors = [
            (0.30, (20,  80,  180)),   # mar profundo
            (0.45, (40,  120, 210)),   # mar poco profundo
            (0.52, (210, 190, 130)),   # arena
            (0.63, (60,  140,  50)),   # tierra/hierba
            (0.75, (80,  100,  60)),   # bosque
            (0.85, (120, 110,  90)),   # montaña
            (1.00, (230, 230, 240)),   # nieve
        ]

        self.sun_colors = [
            (0.17, (143,  107,  30)),
            (0.23, (179,  156,  10)),
            (0.36, (183,  177,  20)),
            (1.00, (230,  217,  30)),
        ]

        self.map = 1
        self.mid = ((game.screen.get_width()//2), (game.screen.get_height()//2))
        w_scr = game.screen.get_width()
        h_scr = game.screen.get_height()

        # BG Stars
        self.stars = background_stars(w_scr, h_scr)

        # Stellar objects
        self.sun = star(self.mid[0]+32*6, self.mid[1], 130, (215, 198, 32), 10, 10)
        self.planet = planet(self.mid[0] - 32, self.mid[1], 15, (20, 111, 184), 10)
        self.moon = moon(self.mid[0] - 32*1, self.mid[1], 9, (133, 136, 140), 100)

        # Menu 
        self.play_btn = img_button(32*2, h_scr - 32*11, game.gui, 0, 32*4, 32*3, 32, 2, "Play", game.font, (255, 255, 255), 0, 32*5.5, 16, 16, "left")
        self.settings_btn = img_button(32*2, h_scr - 32*8, game.gui, 0, 32*4, 32*3, 32, 2, "Settings", game.font, (255, 255, 255), 16, 32*5, 16, 16, "left")
        self.exit_btn = img_button(32*2, h_scr - 32*5, game.gui, 0, 32*4, 32*3, 32, 2, "Exit", game.font, (255, 255, 255), 32, 32*5.5, 16, 16, "left")

        # Settings
        self.stn_back = img_button((w_scr - 32*8) - w_scr, h_scr - 32*5, game.gui, 0, 32*4, 32*3, 32, 2, "Back", game.font, (255, 255, 255), 0, 32*5, 16, 16, "right")

        self.vol_bg = img_button(32*2 - w_scr, 32*2, game.gui, 0, 32*4, 32*3, 32, 2)
        self.vol_slide = slide(self.vol_bg.x + 16, self.vol_bg.y + 25, 32*5, 12, min_val=0, max_val=1, value=0.5, border_rad=20,
                               handle_radius=15, track_color=(130, 130, 130), fill_color=(120, 120, 120), handle_color=(100, 100, 100))
        self.vol_txt = text(self.vol_bg.x + 32*6, self.vol_bg.y + 20, f'Volumen: {int(settings.vol*100)}%', game.font, scale=2.5)

        self.sfx_bg = img_button(32*2 - w_scr, 32*5, game.gui, 0, 32*4, 32*3, 32, 2)
        self.sfx_slide = slide(self.sfx_bg.x + 16, self.sfx_bg.y + 25, 32*5, 12, min_val=0, max_val=1, value=0.5, border_rad=20,
                                handle_radius=15, track_color=(130, 130, 130), fill_color=(120, 120, 120), handle_color=(100, 100, 100))
        self.sfx_txt = text(self.sfx_bg.x + 32*6, self.sfx_bg.y + 20, f'SFX: {int(settings.sfx*100)}%', game.font, scale=2.5)
        
        # Game menu
        self.game_panel = panel(32*2 + w_scr, 32*2, game.gui, 32, 9, 7, 32, 64, 96, 0, 32, 64, scale=2)

        self.panelw_back = img_button(32*2 + w_scr, h_scr - 32*5, game.gui, 0, 32*4, 32*3, 32, 2, "Back", game.font, (255, 255, 255), 0, 32*5, 16, 16, "left")

        self.w_name_txt = text(self.game_panel.x + 24, self.game_panel.y + 24, "Name", game.font, scale=2)
        self.w_name_input = img_input(self.w_name_txt.x, self.w_name_txt.y + 24, game.gui, 0, 32*4, 32*3, 32, game.font, 2, "Mundo", txt_scale=2)

        self.dif_txt = text(self.w_name_input.x, self.w_name_input.y + 32*3, "Difficulty", game.font, scale=2)

        self.easy_btn = img_button(self.dif_txt.x, self.dif_txt.y + 24, game.gui, 0, 0, 32, 32, 2, icon_sx=32*2.5, icon_sy=32*5.5, icon_w=16, icon_h=16)
        self.easy_txt = text(self.easy_btn.x + 20, self.easy_btn.y + 64, "Easy", game.font)

        self.normal_btn = img_button(self.easy_btn.x + 32*2, self.easy_btn.y, game.gui, 0, 0, 32, 32, 2, icon_sx=32*2, icon_sy=32*5, icon_w=16, icon_h=16)
        self.normal_txt = text(self.normal_btn.x + 14, self.easy_btn.y + 64, "Normal", game.font)

        self.hard_btn = img_button(self.normal_btn.x + 32*2, self.normal_btn.y, game.gui, 0, 0, 32, 32, 2, icon_sx=32*2.5, icon_sy=32*5, icon_w=16, icon_h=16)
        self.hard_txt = text(self.hard_btn.x + 20, self.easy_btn.y + 64, "Hard", game.font)

        self.w_seed_txt = text(self.w_name_input.x, self.easy_btn.y + 32*3, "Seed", game.font, scale=2)
        self.w_seed_input = img_input(self.w_seed_txt.x, self.w_seed_txt.y + 24, game.gui, 0, 32*4, 32*3, 32, game.font, 2, "1", "numbers", 2)    

        self.enter_wrld = img_button(self.w_seed_input.x, self.w_seed_input.y + 32*2.25, game.gui, 0, 32*4, 32*3, 32, 2, "Play", game.font, (255, 255, 255), 0, 32*5.5, 16, 16, "left")

        self.world_panel = panel(self.w_name_txt.x + 32 * 7 - 16, 32*2 + 32, game.gui, 32, 5, 6, 32, 64, 96, 0, 32, 64, scale=2)

        # [Nombre, dificultad, semilla]
        self.world_data = [self.w_name_input.txt, "Easy", int(self.w_seed_input.txt)]
        self.dif_sel = "Easy"

        self.name_pan = text(self.world_panel.x + 16, self.world_panel.y + 10, f'Name: {self.w_name_input.get_text()}', game.font, scale=2)
        self.dif_pan = text(self.name_pan.x, self.name_pan.y + 32*2.5, f'Difficulty: {self.dif_sel}', game.font, scale=2)
        self.seed_pan = text(self.dif_pan.x, self.dif_pan.y + 32*2.5, f'Seed: {self.w_seed_input.get_text}', game.font, scale=2)
        
        self.x = 0
        self.y = 0
        
    def events(self, event):
        self.w_name_input.event(event)
        self.w_seed_input.event(event)

        if self.exit_btn.event() == True:
            self.game.running = False

        if self.settings_btn.event() == True:
            # Menu
            self.settings_btn.move_to(self.game.screen.get_width() + self.settings_btn.x, self.settings_btn.y)
            self.play_btn.move_to(self.game.screen.get_width() + self.play_btn.x, self.play_btn.y)
            self.exit_btn.move_to(self.game.screen.get_width() + self.exit_btn.x, self.exit_btn.y)

            # Settings
            self.stn_back.move_to(self.game.screen.get_width() + self.stn_back.x, self.stn_back.y)

            self.vol_bg.move_to(self.game.screen.get_width() + self.vol_bg.x, self.vol_bg.y)
            self.vol_slide.move_to(self.game.screen.get_width() + self.vol_slide.x, self.vol_slide.y)
            self.vol_txt.move_to(self.game.screen.get_width() + self.vol_txt.x, self.vol_txt.y)

            self.sfx_bg.move_to(self.game.screen.get_width() + self.sfx_bg.x, self.sfx_bg.y)
            self.sfx_slide.move_to(self.game.screen.get_width() + self.sfx_slide.x, self.sfx_slide.y)
            self.sfx_txt.move_to(self.game.screen.get_width() + self.sfx_txt.x, self.sfx_txt.y)

            # Game menu
            self.game_panel.move_to(self.game.screen.get_width() + self.game_panel.x, self.game_panel.y)
            self.panelw_back.move_to(self.game.screen.get_width() + self.panelw_back.x, self.panelw_back.y)

            self.w_name_txt.move_to(self.game.screen.get_width() + self.w_name_txt.x, self.w_name_txt.y)
            self.w_name_input.move_to(self.game.screen.get_width() + self.w_name_input.x, self.w_name_input.y)

            self.dif_txt.move_to(self.game.screen.get_width() + self.dif_txt.x, self.dif_txt.y)

            self.easy_btn.move_to(self.game.screen.get_width() + self.easy_btn.x, self.easy_btn.y)
            self.easy_txt.move_to(self.game.screen.get_width() + self.easy_txt.x, self.easy_txt.y)

            self.normal_btn.move_to(self.game.screen.get_width() + self.normal_btn.x, self.normal_btn.y)
            self.normal_txt.move_to(self.game.screen.get_width() + self.normal_txt.x, self.normal_txt.y)

            self.hard_btn.move_to(self.game.screen.get_width() + self.hard_btn.x, self.hard_btn.y)
            self.hard_txt.move_to(self.game.screen.get_width() + self.hard_txt.x, self.hard_txt.y)

            self.w_seed_txt.move_to(self.game.screen.get_width() + self.w_seed_txt.x, self.w_seed_txt.y)
            self.w_seed_input.move_to(self.game.screen.get_width() + self.w_seed_input.x, self.w_seed_input.y)

            self.world_panel.move_to(self.game.screen.get_width() + self.world_panel.x, self.world_panel.y)

            self.name_pan.move_to(self.game.screen.get_width() + self.name_pan.x, self.name_pan.y)
            self.dif_pan.move_to(self.game.screen.get_width() + self.dif_pan.x, self.dif_pan.y)
            self.seed_pan.move_to(self.game.screen.get_width() + self.seed_pan.x, self.seed_pan.y)

            self.enter_wrld.move_to(self.game.screen.get_width() + self.enter_wrld.x, self.enter_wrld.y)

        if self.panelw_back.event() == True:
            # Menu
            self.settings_btn.move_to(self.game.screen.get_width() + self.settings_btn.x, self.settings_btn.y)
            self.play_btn.move_to(self.game.screen.get_width() + self.play_btn.x, self.play_btn.y)
            self.exit_btn.move_to(self.game.screen.get_width() + self.exit_btn.x, self.exit_btn.y)

            # Settings
            self.stn_back.move_to(self.game.screen.get_width() + self.stn_back.x, self.stn_back.y)

            self.vol_bg.move_to(self.game.screen.get_width() + self.vol_bg.x, self.vol_bg.y)
            self.vol_slide.move_to(self.game.screen.get_width() + self.vol_slide.x, self.vol_slide.y)
            self.vol_txt.move_to(self.game.screen.get_width() + self.vol_txt.x, self.vol_txt.y)

            self.sfx_bg.move_to(self.game.screen.get_width() + self.sfx_bg.x, self.sfx_bg.y)
            self.sfx_slide.move_to(self.game.screen.get_width() + self.sfx_slide.x, self.sfx_slide.y)
            self.sfx_txt.move_to(self.game.screen.get_width() + self.sfx_txt.x, self.sfx_txt.y)

            # Game menu
            self.game_panel.move_to(self.game.screen.get_width() + self.game_panel.x, self.game_panel.y)
            self.panelw_back.move_to(self.game.screen.get_width() + self.panelw_back.x, self.panelw_back.y)

            self.w_name_txt.move_to(self.game.screen.get_width() + self.w_name_txt.x, self.w_name_txt.y)
            self.w_name_input.move_to(self.game.screen.get_width() + self.w_name_input.x, self.w_name_input.y)

            self.dif_txt.move_to(self.game.screen.get_width() + self.dif_txt.x, self.dif_txt.y)

            self.easy_btn.move_to(self.game.screen.get_width() + self.easy_btn.x, self.easy_btn.y)
            self.easy_txt.move_to(self.game.screen.get_width() + self.easy_txt.x, self.easy_txt.y)

            self.normal_btn.move_to(self.game.screen.get_width() + self.normal_btn.x, self.normal_btn.y)
            self.normal_txt.move_to(self.game.screen.get_width() + self.normal_txt.x, self.normal_txt.y)

            self.hard_btn.move_to(self.game.screen.get_width() + self.hard_btn.x, self.hard_btn.y)
            self.hard_txt.move_to(self.game.screen.get_width() + self.hard_txt.x, self.hard_txt.y)

            self.w_seed_txt.move_to(self.game.screen.get_width() + self.w_seed_txt.x, self.w_seed_txt.y)
            self.w_seed_input.move_to(self.game.screen.get_width() + self.w_seed_input.x, self.w_seed_input.y)

            self.world_panel.move_to(self.game.screen.get_width() + self.world_panel.x, self.world_panel.y)

            self.name_pan.move_to(self.game.screen.get_width() + self.name_pan.x, self.name_pan.y)
            self.dif_pan.move_to(self.game.screen.get_width() + self.dif_pan.x, self.dif_pan.y)
            self.seed_pan.move_to(self.game.screen.get_width() + self.seed_pan.x, self.seed_pan.y)

            self.enter_wrld.move_to(self.game.screen.get_width() + self.enter_wrld.x, self.enter_wrld.y)

        if self.stn_back.event() == True:
            # Menu
            self.settings_btn.move_to(self.settings_btn.x - self.game.screen.get_width(), self.settings_btn.y)
            self.play_btn.move_to(self.play_btn.x - self.game.screen.get_width(), self.play_btn.y)
            self.exit_btn.move_to(self.exit_btn.x - self.game.screen.get_width(), self.exit_btn.y)

            # Settings
            self.stn_back.move_to(self.stn_back.x - self.game.screen.get_width(), self.stn_back.y)
            
            self.vol_bg.move_to(self.vol_bg.x - self.game.screen.get_width(), self.vol_bg.y)
            self.vol_slide.move_to(self.vol_slide.x - self.game.screen.get_width(), self.vol_slide.y)
            self.vol_txt.move_to(self.vol_txt.x - self.game.screen.get_width(), self.vol_txt.y)

            self.sfx_bg.move_to(self.sfx_bg.x - self.game.screen.get_width(), self.sfx_bg.y)
            self.sfx_slide.move_to(self.sfx_slide.x - self.game.screen.get_width(), self.sfx_slide.y)
            self.sfx_txt.move_to(self.sfx_txt.x - self.game.screen.get_width(), self.sfx_txt.y)

            # Game menu
            self.game_panel.move_to(self.game_panel.x - self.game.screen.get_width(), self.game_panel.y) 
            self.panelw_back.move_to(self.panelw_back.x - self.game.screen.get_width(), self.panelw_back.y)

            self.w_name_txt.move_to(self.w_name_txt.x - self.game.screen.get_width(), self.w_name_txt.y)
            self.w_name_input.move_to(self.w_name_input.x - self.game.screen.get_width(), self.w_name_input.y)

            self.dif_txt.move_to(self.dif_txt.x - self.game.screen.get_width(), self.dif_txt.y)

            self.easy_btn.move_to(self.easy_btn.x - self.game.screen.get_width(), self.easy_btn.y)
            self.easy_txt.move_to(self.easy_txt.x - self.game.screen.get_width(), self.easy_txt.y)

            self.normal_btn.move_to(self.normal_btn.x - self.game.screen.get_width(), self.normal_btn.y)
            self.normal_txt.move_to(self.normal_txt.x - self.game.screen.get_width(), self.normal_txt.y)

            self.hard_btn.move_to(self.hard_btn.x - self.game.screen.get_width(), self.hard_btn.y)
            self.hard_txt.move_to(self.hard_txt.x - self.game.screen.get_width(), self.hard_txt.y)

            self.w_seed_txt.move_to(self.w_seed_txt.x - self.game.screen.get_width(), self.w_seed_txt.y)
            self.w_seed_input.move_to(self.w_seed_input.x - self.game.screen.get_width(), self.w_seed_input.y)

            self.world_panel.move_to(self.world_panel.x - self.game.screen.get_width(), self.world_panel.y)

            self.name_pan.move_to(self.name_pan.x - self.game.screen.get_width(), self.name_pan.y)
            self.dif_pan.move_to(self.dif_pan.x - self.game.screen.get_width(), self.dif_pan.y)
            self.seed_pan.move_to(self.seed_pan.x - self.game.screen.get_width(), self.seed_pan.y)

            self.enter_wrld.move_to(self.enter_wrld.x - self.game.screen.get_width(), self.enter_wrld.y)

        if self.play_btn.event() == True:
            # Menu
            self.settings_btn.move_to(self.settings_btn.x - self.game.screen.get_width(), self.settings_btn.y)
            self.play_btn.move_to(self.play_btn.x - self.game.screen.get_width(), self.play_btn.y)
            self.exit_btn.move_to(self.exit_btn.x - self.game.screen.get_width(), self.exit_btn.y)

            # Settings
            self.stn_back.move_to(self.stn_back.x - self.game.screen.get_width(), self.stn_back.y)
            
            self.vol_bg.move_to(self.vol_bg.x - self.game.screen.get_width(), self.vol_bg.y)
            self.vol_slide.move_to(self.vol_slide.x - self.game.screen.get_width(), self.vol_slide.y)
            self.vol_txt.move_to(self.vol_txt.x - self.game.screen.get_width(), self.vol_txt.y)

            self.sfx_bg.move_to(self.sfx_bg.x - self.game.screen.get_width(), self.sfx_bg.y)
            self.sfx_slide.move_to(self.sfx_slide.x - self.game.screen.get_width(), self.sfx_slide.y)
            self.sfx_txt.move_to(self.sfx_txt.x - self.game.screen.get_width(), self.sfx_txt.y)

            # Game menu
            self.game_panel.move_to(self.game_panel.x - self.game.screen.get_width(), self.game_panel.y) 
            self.panelw_back.move_to(self.panelw_back.x - self.game.screen.get_width(), self.panelw_back.y)

            self.w_name_txt.move_to(self.w_name_txt.x - self.game.screen.get_width(), self.w_name_txt.y)
            self.w_name_input.move_to(self.w_name_input.x - self.game.screen.get_width(), self.w_name_input.y)

            self.dif_txt.move_to(self.dif_txt.x - self.game.screen.get_width(), self.dif_txt.y)

            self.easy_btn.move_to(self.easy_btn.x - self.game.screen.get_width(), self.easy_btn.y)
            self.easy_txt.move_to(self.easy_txt.x - self.game.screen.get_width(), self.easy_txt.y)

            self.normal_btn.move_to(self.normal_btn.x - self.game.screen.get_width(), self.normal_btn.y)
            self.normal_txt.move_to(self.normal_txt.x - self.game.screen.get_width(), self.normal_txt.y)

            self.hard_btn.move_to(self.hard_btn.x - self.game.screen.get_width(), self.hard_btn.y)
            self.hard_txt.move_to(self.hard_txt.x - self.game.screen.get_width(), self.hard_txt.y)

            self.w_seed_txt.move_to(self.w_seed_txt.x - self.game.screen.get_width(), self.w_seed_txt.y)
            self.w_seed_input.move_to(self.w_seed_input.x - self.game.screen.get_width(), self.w_seed_input.y)

            self.world_panel.move_to(self.world_panel.x - self.game.screen.get_width(), self.world_panel.y)

            self.name_pan.move_to(self.name_pan.x - self.game.screen.get_width(), self.name_pan.y)
            self.dif_pan.move_to(self.dif_pan.x - self.game.screen.get_width(), self.dif_pan.y)
            self.seed_pan.move_to(self.seed_pan.x - self.game.screen.get_width(), self.seed_pan.y)

            self.enter_wrld.move_to(self.enter_wrld.x - self.game.screen.get_width(), self.enter_wrld.y)

        if self.easy_btn.event():
            self.dif_sel = "Easy"

        if self.normal_btn.event():
            self.dif_sel = "Normal"

        if self.hard_btn.event():
            self.dif_sel = "Hard"

        if self.enter_wrld.event():
            self.world_data = [self.w_name_input.get_text(), self.dif_sel, int(self.w_seed_input.get_text())]
            self.game.set_scene("game", self.world_data)

        if self.vol_slide.event():
            self.vol_txt.set_text(f'Volumen: {int(settings.vol*100)}%')
            settings.vol = self.vol_slide.get_value()

        if self.sfx_slide.event():
            self.sfx_txt.set_text(f'SFX: {int(settings.sfx*100)}%')
            settings.sfx = self.sfx_slide.get_value()

    def update(self):
        mid = ((self.game.screen.get_width()//2), (self.game.screen.get_height()//2))
        self.sun.set_pos(mid[0]+32*6, mid[1])
        dt = self.game.clock.get_time()/60
        self.sun.update(dt, 0.01)
        self.planet.update(dt, 0.08)
        self.planet.orbit(self.sun, 32*16, -0.01, -32*5, 0, 0)
        self.moon.update(dt, 0.002)
        self.moon.orbit(self.planet, 32, -0.005, 0, 0, 0)

        # Game panel
        self.name_pan.set_text(f'Name: \n{self.w_name_input.get_text()}')
        self.dif_pan.set_text(f'Difficulty: \n{self.dif_sel}')
        self.seed_pan.set_text(f'Seed: \n{self.w_seed_input.get_text()}')

        # Menu
        self.play_btn.update_movement()
        self.settings_btn.update_movement()
        self.exit_btn.update_movement()

        # Settings
        self.stn_back.update_movement()

        self.vol_bg.update_movement()
        self.vol_slide.update_movement()
        self.vol_txt.update_movement()

        self.sfx_bg.update_movement()
        self.sfx_slide.update_movement()
        self.sfx_txt.update_movement()

        # Game panel
        self.game_panel.update_movement()
        self.panelw_back.update_movement()

        self.w_name_txt.update_movement()
        self.w_name_input.update_movement()

        self.dif_txt.update_movement()

        self.easy_btn.update_movement()
        self.easy_txt.update_movement()

        self.normal_btn.update_movement()
        self.normal_txt.update_movement()

        self.hard_btn.update_movement()
        self.hard_txt.update_movement()

        self.w_seed_txt.update_movement()
        self.w_seed_input.update_movement()

        self.world_panel.update_movement()

        self.name_pan.update_movement()
        self.dif_pan.update_movement()
        self.seed_pan.update_movement()

        self.enter_wrld.update_movement()

    def draw(self, screen):
        self.x += 1
        self.y += 1
        self.stars.draw(screen, self.x, self.y)

        if self.planet.orbit_z < 0:
            if self.moon.orbit_z < 0:
                self.moon.draw(screen, 0.3, light_source=self.sun)
                self.planet.draw(screen, 0.7, colors=self.planet_colors, light_source=self.sun)
            else:
                self.planet.draw(screen, 0.7, colors=self.planet_colors, light_source=self.sun)
                self.moon.draw(screen, 0.3, light_source=self.sun)
            self.sun.draw(screen, colors=self.sun_colors)
            
        else:
            self.sun.draw(screen, colors=self.sun_colors)
            if self.moon.orbit_z < 0:
                self.moon.draw(screen, 0.3, light_source=self.sun)
                self.planet.draw(screen, 0.7, colors=self.planet_colors, light_source=self.sun)
            else:
                self.planet.draw(screen, 0.7, colors=self.planet_colors, light_source=self.sun)
                self.moon.draw(screen, 0.3, light_source=self.sun)

        # Menu
        self.play_btn.draw(screen)
        self.settings_btn.draw(screen)
        self.exit_btn.draw(screen)

        # Settings
        self.stn_back.draw(screen)

        self.vol_bg.draw(screen)
        self.vol_slide.draw(screen)
        self.vol_txt.draw(screen)

        self.sfx_bg.draw(screen)
        self.sfx_slide.draw(screen)
        self.sfx_txt.draw(screen)

        self.game_panel.draw(screen)
        self.panelw_back.draw(screen)

        self.w_name_txt.draw(screen)
        self.w_name_input.draw(screen)

        self.dif_txt.draw(screen)

        self.easy_btn.draw(screen)
        self.easy_txt.draw(screen)

        self.normal_btn.draw(screen)
        self.normal_txt.draw(screen)

        self.hard_btn.draw(screen)
        self.hard_txt.draw(screen)

        self.w_seed_txt.draw(screen)
        self.w_seed_input.draw(screen)

        self.world_panel.draw(screen)

        self.name_pan.draw(screen)
        self.dif_pan.draw(screen)
        self.seed_pan.draw(screen)

        self.enter_wrld.draw(screen)
