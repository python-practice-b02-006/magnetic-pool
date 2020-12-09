import pygame
import pygame_gui
import game
import data

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 60
DT = FPS/100
BG_COLOR = pygame.Color('white')


class Manager:
    """Handles events and switching between menus."""
    def __init__(self):
        """Creates buttons, manager, game."""
        self.level_number = data.number_of_levels()
        self.make_level_pictures()
        self.manager = pygame_gui.UIManager(WINDOW_SIZE,
                                            "themes/buttons/level_buttons.json")
        self.running = True
        self.game_on = False
        self.construction = False
        self.game = None
        self.constructor = None

        self.slb_rect = [pygame.Rect((160, WINDOW_HEIGHT - 50*3//2), (100, 50)),
                         pygame.Rect((WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2 - 50), (100, 50))]
        self.select_level_button = pygame_gui.elements.UIButton(relative_rect=self.slb_rect[1],
                                                                text='Levels',
                                                                manager=self.manager)
        self.mmb_rect = [pygame.Rect((50, WINDOW_HEIGHT - 50 * 3 // 2), (100, 50)),
                         pygame.Rect((WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2 + 35), (100, 50))]
        self.main_menu_button = pygame_gui.elements.UIButton(relative_rect=self.mmb_rect[0],
                                                             text='Main menu',
                                                             manager=self.manager,
                                                             visible=0)

        self.level_buttons = self.make_level_buttons()
        self.new_level_button = pygame_gui.elements.UIButton(relative_rect=self.slb_rect[0],
                                                             text='New_level',
                                                             manager=self.manager,
                                                             visible=0)

    def make_level_pictures(self):
        """Makes pictures of fields of all levels."""
        for i in range(self.level_number):
            game.Game(i+1)

    def make_level_buttons(self, hor=4, vert=3):
        """Makes buttons for all levels."""
        width = (WINDOW_WIDTH - 30 * hor) // hor
        height = (WINDOW_HEIGHT - 75 - 20 * vert) // vert
        coords = [[15 * (2 * (i % hor) + 1) + width * (i % hor),
                   10 * (2 * ((i//hor) % vert) + 1) + height * ((i//hor) % vert)]
                  for i in range(self.level_number)]
        levels_rect = [pygame.Rect(coords[i], (width, height))
                       for i in range(self.level_number)]
        level_buttons = [pygame_gui.elements.UIButton(relative_rect=levels_rect[i],
                                                      text="",
                                                      manager=self.manager,
                                                      visible=0,
                                                      object_id="level_" + str(i+1))
                         for i in range(self.level_number)]
        return level_buttons

    def process(self, screen):
        """Runs the game."""
        self.handle_events()

        self.manager.update(DT)

        screen.fill(BG_COLOR)

        if self.game_on:
            self.game.draw_on_field()
            screen.blit(self.game.field, (0, 0))

        if self.construction:
            self.constructor.draw()
            screen.blit(self.constructor.field, (0, 0))

        self.manager.draw_ui(screen)
        self.update_buttons()

    def handle_events(self):
        """Handles the events."""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.select_level_button:
                        self.select_level()
                    if event.ui_element == self.main_menu_button:
                        self.main_menu()
                    if event.ui_element == self.new_level_button:
                        self.new_level()
                    for i, button in enumerate(self.level_buttons):
                        if event.ui_element == button:
                            self.start_level(i + 1)
            self.manager.process_events(event)
        if self.game_on:
            if not self.game.win:
                self.game.update(events, DT)
            else:
                self.win_game()
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
        self.new_level_button.visible = 0
        for button in self.level_buttons:
            button.visible = 0
        self.game_on = False
        self.game = None
        self.construction = False
        self.constructor = None

    def select_level(self):
        """Actions after select level button was pushed."""
        self.main_menu_button.visible = 1
        self.main_menu_button.rect = self.mmb_rect[0]
        self.main_menu_button.rebuild()
        self.select_level_button.visible = 0
        self.select_level_button.rect = self.slb_rect[0]
        self.select_level_button.rebuild()
        for button in self.level_buttons:
            button.visible = 1
        self.new_level_button.visible = 1
        self.game_on = False
        self.game = None
        self.construction = False
        self.constructor = None

    def start_level(self, level):
        """Actions after a level was selected."""
        self.select_level_button.visible = 1
        self.new_level_button.visible = 0
        for level_button in self.level_buttons:
            level_button.visible = 0
        self.game_on = True
        self.game = game.Game(level)

    def new_level(self):
        """Actions after construction of a level was started."""
        self.new_level_button.visible = 0
        self.select_level_button.visible = 1
        for level_button in self.level_buttons:
            level_button.visible = 0
        self.construction = True
        self.constructor = game.Constructor(self.level_number + 1)

    def win_game(self):
        """Actions after game was won."""
        self.main_menu_button.rect = self.mmb_rect[1]
        self.main_menu_button.rebuild()
        self.select_level_button.rect = self.slb_rect[1]
        self.select_level_button.rebuild()

    def update_buttons(self):
        if self.level_number < data.number_of_levels():
            print(1)
            self.level_number = data.number_of_levels()
            self.level_buttons = self.make_level_buttons()


def main():
    """
    Creates main cycle and the screen. Calls manager.
    """
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
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
