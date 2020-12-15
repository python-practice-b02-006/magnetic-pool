import pygame
import pygame_gui
import game
import data
import numpy as np

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 60
DT = FPS / 100
BG_COLOR = pygame.Color('white')


class Manager:
    """Handles events and switching between menus.

    Attributes:
        level_number: number of levels currently available.
        manager: object that manages menu buttons.

        running: variable that shows if the app is still opened.
        game_on: variable that shows if a game (a level) is being played.
        construction: variable that shows if a new level is being constructed.
        chaos_on: variable that shows if chaos is being studied.
        game: object that represents a game (a level).
        constructor: object that represents a level constructor.
        chaos_study: object that represents a chaos study.
        chaos_mode: variable that determines what happens if one clicks on a level button. If False the game will
            start,otherwise a chaos study will begin.

        slb_rect: array of rectangles, containing select level button in different menus.
        select_level_button: button that leads to menu where one can select a level to play, or to study.

        mmb_rect: array of rectangles, containing main menu button in different menus.
        main_menu_button: button that leads to main menu.

        lb_managers: objects that manage level buttons.
        level_buttons: array of buttons. If one clicks on a button from the array a level will start or the study will
            begin.
        new_level_button: button that leads to a menu where one can create a new level.

        cb_rect: rectangle, containing chaos button.
        chaos_button: button that changes chaos_mode.

        sliders_rect: rectangles that contain sliders.
        sliders: sliders that are used in chaos study mode.
    """
    def __init__(self):
        self.level_number = data.number_of_levels()
        self.make_level_pictures()
        self.manager = pygame_gui.UIManager(WINDOW_SIZE,
                                            "themes/buttons/menu_buttons.json")
        self.running = True
        self.game_on = False
        self.info_on = False
        self.construction = False
        self.chaos_on = False
        self.game = None
        self.constructor = None
        self.chaos_study = None
        self.chaos_mode = False

        self.slb_rect = [pygame.Rect((160, WINDOW_HEIGHT - 50 * 3 // 2), (100, 50)),
                         pygame.Rect((WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 50 - 70), (100, 50))]
        self.select_level_button = pygame_gui.elements.UIButton(relative_rect=self.slb_rect[1],
                                                                text='Levels',
                                                                manager=self.manager,
                                                                object_id="menu_button")
        self.mmb_rect = [pygame.Rect((25, WINDOW_HEIGHT - 50 * 3 // 2), (100, 50)),
                         pygame.Rect((WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 35), (100, 50))]
        self.main_menu_button = pygame_gui.elements.UIButton(relative_rect=self.mmb_rect[0],
                                                             text='Main menu',
                                                             manager=self.manager,
                                                             visible=0,
                                                             object_id="menu_button")
        self.cb_rect = self.slb_rect[1].copy()
        self.cb_rect.top = self.cb_rect.bottom + 5
        self.credits_button = pygame_gui.elements.UIButton(relative_rect=self.cb_rect,
                                                           text='Credits',
                                                           manager=self.manager,
                                                           object_id="menu_button")
        self.hb_rect = self.cb_rect.copy()
        self.hb_rect.top = self.cb_rect.bottom + 5
        self.help_button = pygame_gui.elements.UIButton(relative_rect=self.hb_rect,
                                                           text='Help',
                                                           manager=self.manager,
                                                           object_id="menu_button")
        self.exit_rect = self.hb_rect.copy()
        self.exit_rect.top = self.hb_rect.bottom + 5
        self.exit_button = pygame_gui.elements.UIButton(relative_rect=self.exit_rect,
                                                           text='Exit',
                                                           manager=self.manager,
                                                           object_id="menu_button")

        self.lb_managers = []
        self.level_buttons = self.make_level_buttons()
        self.new_level_button = pygame_gui.elements.UIButton(relative_rect=self.slb_rect[0],
                                                             text='New level',
                                                             manager=self.manager,
                                                             visible=0,
                                                             object_id="menu_button")
        self.cb_rect = pygame.Rect((245 + 20, WINDOW_HEIGHT - 50 * 3 // 2), (100, 50))
        self.chaos_button = pygame_gui.elements.UIButton(relative_rect=self.cb_rect,
                                                         text="Chaos",
                                                         manager=self.manager,
                                                         visible=0,
                                                         object_id="menu_button")
        self.sliders_rect = [
            pygame.Rect((245, WINDOW_HEIGHT - 50 * 3 // 2), (100, 50)),
            pygame.Rect((355, WINDOW_HEIGHT - 50 * 3 // 2), (100, 50)),
            pygame.Rect((465, WINDOW_HEIGHT - 50 * 3 // 2), (100, 50)),
        ]
        self.sliders = []
        self.slider_values = [pygame.Surface((100, 20)) for i in range(3)]

    def make_level_pictures(self):
        """Makes pictures of fields of all levels."""
        for i in range(self.level_number):
            game.Game(i + 1)
            data.make_level_button_theme(i + 1)

    def make_level_buttons(self, hor=4, vert=3):
        """Makes buttons for all levels."""
        width = (WINDOW_WIDTH - 30 * hor) // hor
        height = (WINDOW_HEIGHT - 75 - 20 * vert) // vert
        coords = [[15 * (2 * (i % hor) + 1) + width * (i % hor),
                   10 * (2 * ((i // hor) % vert) + 1) + height * ((i // hor) % vert)]
                  for i in range(self.level_number)]
        levels_rect = [pygame.Rect(coords[i], (width, height))
                       for i in range(self.level_number)]
        self.lb_managers = [pygame_gui.UIManager(WINDOW_SIZE, "themes/buttons/level_" + str(i + 1) + ".json")
                            for i in range(self.level_number)]
        level_buttons = [pygame_gui.elements.UIButton(relative_rect=levels_rect[i],
                                                      text="",
                                                      manager=self.lb_managers[i],
                                                      visible=0,
                                                      object_id="level_" + str(i + 1))
                         for i in range(self.level_number)]
        return level_buttons

    def process(self, screen):
        """Runs the game."""
        self.handle_events()

        self.manager.update(DT)
        for manager in self.lb_managers:
            manager.update(DT)

        screen.fill(BG_COLOR)

        if self.game_on:
            self.game.draw_on_field()
            screen.blit(self.game.field, (0, 0))

        if self.construction:
            self.constructor.draw()
            screen.blit(self.constructor.field, (0, 0))

        if self.chaos_on:
            self.chaos_study.draw_on_field()
            screen.blit(self.chaos_study.field, (0, 0))
            for i in range(3):
                screen.blit(self.slider_values[i], (self.sliders_rect[i][0], self.sliders_rect[i][1] + 50))

        if self.info_on:
            screen.blit(self.info, self.info_rect)

        self.manager.draw_ui(screen)
        for manager in self.lb_managers:
            manager.draw_ui(screen)
        self.update_buttons()

    def handle_events(self):
        """Handles the events."""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.credits_button:
                        text = data.read_info("credits.txt")
                        self.display_info(text)
                    if event.ui_element == self.help_button:
                        text = data.read_info("help.txt")
                        self.display_info(text)
                    if event.ui_element == self.exit_button:
                        self.running = False
                    if event.ui_element == self.select_level_button:
                        self.select_level()
                    if event.ui_element == self.main_menu_button:
                        self.main_menu()
                    if event.ui_element == self.new_level_button:
                        self.new_level()
                    if event.ui_element == self.chaos_button:
                        self.chaos_mode = not self.chaos_mode
                        if self.chaos_mode:
                            self.chaos_button.text = "Game"
                            self.chaos_button.rebuild()
                        else:
                            self.chaos_button.text = "Chaos"
                            self.chaos_button.rebuild()
                    for i, button in enumerate(self.level_buttons):
                        if event.ui_element == button:
                            if not self.chaos_mode:
                                self.start_level(i + 1)
                            else:
                                self.start_chaos_study(i + 1)
                if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    for slider in self.sliders:
                        if event.ui_element == slider:
                            self.update_value()
            self.manager.process_events(event)
            for manager in self.lb_managers:
                manager.process_events(event)

            if self.info_on and event.type == pygame.KEYDOWN \
                    and pygame.key.get_pressed()[pygame.K_c]:
                pygame.scrap.put(pygame.SCRAP_TEXT,
                b"https://github.com/python-practice-b02-006/magnetic-pool")


        if self.game_on:
            if not self.game.win:
                self.game.update(events, DT)
            else:
                self.win_game()
        if self.chaos_on:
            variables = [slider.get_current_value() for slider in self.sliders]
            self.chaos_study.update(events, DT, variables)
        if self.construction:
            if not self.constructor.stage == 3:
                self.constructor.update(events)

    def main_menu(self):
        """Actions after main menu button was pushed."""
        self.select_level_button.visible = 1
        self.select_level_button.rect = self.slb_rect[1]
        self.select_level_button.rebuild()

        self.main_menu_button.visible = 0
        self.main_menu_button.rect = self.mmb_rect[0]
        self.main_menu_button.rebuild()

        self.credits_button.visible = 1
        self.credits_button.rebuild()

        self.help_button.visible = 1
        self.help_button.rebuild()

        self.exit_button.visible = 1
        self.exit_button.rebuild()

        self.new_level_button.visible = 0
        self.chaos_button.visible = 0
        for button in self.level_buttons:
            button.visible = 0
        self.game_on = False
        self.game = None
        self.construction = False
        self.constructor = None
        self.chaos_on = False
        self.chaos_study = None

        self.info_on = False

        self.delete_sliders()

    def select_level(self):
        """Actions after select level button was pushed."""
        self.main_menu_button.visible = 1
        self.main_menu_button.rect = self.mmb_rect[0]
        self.main_menu_button.rebuild()
        self.select_level_button.visible = 0
        self.select_level_button.rect = self.slb_rect[0]
        self.select_level_button.rebuild()

        self.credits_button.visible = 0
        self.help_button.visible = 0
        self.exit_button.visible = 0
        for button in self.level_buttons:
            button.visible = 1
        self.new_level_button.visible = 1
        self.chaos_button.visible = 1
        self.game_on = False
        self.game = None
        self.construction = False
        self.constructor = None
        self.chaos_on = False
        self.chaos_study = None
        self.delete_sliders()

    def display_info(self, text):
        self.info_on = True
        self.main_menu_button.visible = 1
        self.main_menu_button.rect = self.mmb_rect[0]
        self.main_menu_button.rebuild()
        self.credits_button.visible = 0
        self.help_button.visible = 0
        self.exit_button.visible = 0
        self.select_level_button.visible = 0

        self.info_rect = pygame.Rect(0, 0, WINDOW_WIDTH - 100, WINDOW_HEIGHT // 1.2)
        self.info_rect.centerx = WINDOW_WIDTH // 2
        self.info_rect.bottom = self.main_menu_button.rect.top - 5

        self.info = pygame.Surface(self.info_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.info, pygame.Color("#808080"), (0, 0, *self.info.get_size()), 1)

        font = pygame.font.SysFont("arial", 20)
        rendered_char = font.render("1", 1, pygame.Color('black'))
        text_h = rendered_char.get_height()
        for i, line in enumerate(text.splitlines()):
            rendered_line = font.render(line, 1, pygame.Color("black"))
            self.info.blit(rendered_line, (4, 1 + i * text_h))

    def start_level(self, level):
        """Actions after a level was selected."""
        self.select_level_button.visible = 1
        self.new_level_button.visible = 0
        self.chaos_button.visible = 0
        for level_button in self.level_buttons:
            level_button.visible = 0
        self.game_on = True
        self.game = game.Game(level)

    def new_level(self):
        """Actions after construction of a level was started."""
        self.new_level_button.visible = 0
        self.select_level_button.visible = 1
        self.chaos_button.visible = 0
        for level_button in self.level_buttons:
            level_button.visible = 0
        self.construction = True
        self.constructor = game.Constructor(self.level_number + 1)

    def win_game(self):
        """Actions after game was won."""
        self.make_level_pictures()
        self.level_buttons = self.make_level_buttons()
        self.main_menu_button.rect = self.mmb_rect[1]
        self.main_menu_button.rebuild()
        self.select_level_button.rect = self.slb_rect[1]
        self.select_level_button.rebuild()

    def update_buttons(self):
        """Updates buttons."""
        if self.level_number < data.number_of_levels():
            self.level_number = data.number_of_levels()
            self.level_buttons = self.make_level_buttons()

    def start_chaos_study(self, level):
        """Actions before the chaos study begins."""
        self.select_level_button.visible = 1
        self.new_level_button.visible = 0
        self.build_sliders()
        self.update_value()
        self.chaos_button.visible = 0
        for level_button in self.level_buttons:
            level_button.visible = 0
        self.chaos_on = True
        self.chaos_study = game.ChaosStudy(level)

    def build_sliders(self):
        """Creates sliders."""
        self.sliders.append(pygame_gui.elements.UIHorizontalSlider(relative_rect=self.sliders_rect[0],
                                                                   start_value=1,
                                                                   value_range=(0.0, 5.0),
                                                                   object_id="menu_button",
                                                                   manager=self.manager,
                                                                   visible=1))
        self.sliders.append(pygame_gui.elements.UIHorizontalSlider(relative_rect=self.sliders_rect[1],
                                                                   start_value=np.pi/360,
                                                                   value_range=(0.0, np.pi/90),
                                                                   object_id="menu_button",
                                                                   manager=self.manager,
                                                                   visible=1))
        self.sliders.append(pygame_gui.elements.UIHorizontalSlider(relative_rect=self.sliders_rect[2],
                                                                   start_value=10,
                                                                   value_range=(1, 100),
                                                                   object_id="menu_button",
                                                                   manager=self.manager,
                                                                   visible=1))
        self.update_value()

    def delete_sliders(self):
        """Deletes sliders."""
        for slider in self.sliders:
            slider.kill()
            self.sliders = []

    def update_value(self):
        """Updates text that shows the value of the slider."""
        texts = ["Coord", "Angle", "Balls"]
        for i, slider in enumerate(self.sliders):
            self.slider_values[i].fill(BG_COLOR)
            font = pygame.font.Font(None, 20)
            value = slider.get_current_value()
            if i == 1:
                value = value / np.pi * 180
            value = int(100 * value) / 100
            text = font.render(str(texts[i]) + f": {value}", 1, pygame.Color('black'))
            text_x = 0
            text_y = 0
            self.slider_values[i].blit(text, (text_x, text_y))


def main():
    """Creates main cycle and the screen. Calls manager."""
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.scrap.init()
    clock = pygame.time.Clock()

    manager = Manager()

    running = True

    while running:
        clock.tick(FPS)

        manager.process(screen)
        running = manager.running

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
