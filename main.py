import pygame
import pygame_gui
import game
import objects

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 60
DT = FPS/1000
BG_COLOR = pygame.Color('black')


class Manager:
    """Handles events and switching between menus."""
    def __init__(self):
        """Creates buttons, manager, game."""
        self.manager = pygame_gui.UIManager(WINDOW_SIZE)
        self.running = True
        self.game_on = False
        self.game = None

        self.main_menu_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                             text='Start game',
                                                             manager=self.manager)
        self.stop_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 525), (100, 50)),
                                                             text='Stop game',
                                                             manager=self.manager,
                                                             visible=0)

    def process(self, screen):
        """Runs the game."""
        self.handle_events()

        self.manager.update(DT)

        screen.fill(BG_COLOR)
        self.manager.draw_ui(screen)

        if self.game_on:
            screen.blit(self.game.field, (25, 0))

    def handle_events(self):
        """
        Handles the events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.main_menu_button:
                        self.main_menu_button.visible = 0
                        self.stop_game_button.visible = 1
                        self.game_on = True
                        self.game = game.Game(1)
                    if event.ui_element == self.stop_game_button:
                        self.main_menu_button.visible = 1
                        self.stop_game_button.visible = 0
                        self.game_on = False
                        self.game = None

            if self.game_on and event.type == pygame.MOUSEBUTTONDOWN:
                self.game.update(event)

            self.manager.process_events(event)


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