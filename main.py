import pygame
import pygame_gui
import game
import objects
import numpy as np

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 60
DT = FPS/100
BG_COLOR = pygame.Color('white')


class Manager:
    """Handles events and switching between menus."""
    def __init__(self):
        """Creates buttons, manager, game."""
        self.manager = pygame_gui.UIManager(WINDOW_SIZE)
        self.running = True
        self.game_on = False
        self.game = None

        self.slb_rect = [pygame.Rect((160, 525), (100, 50)), pygame.Rect((350, 275), (100, 50))]
        self.select_level_button = pygame_gui.elements.UIButton(relative_rect=self.slb_rect[1],
                                                                text='Levels',
                                                                manager=self.manager)
        self.sgb_rect = [pygame.Rect((50, 525), (100, 50)), pygame.Rect((350, 335), (100, 50))]
        self.stop_game_button = pygame_gui.elements.UIButton(relative_rect=self.sgb_rect[0],
                                                             text='Main menu',
                                                             manager=self.manager,
                                                             visible=0)

    def process(self, screen):
        """Runs the game."""
        self.handle_events()

        self.manager.update(DT)

        screen.fill(BG_COLOR)

        if self.game_on:
            self.game.draw_on_field()
            screen.blit(self.game.field, (0, 0))

        self.manager.draw_ui(screen)

    def handle_events(self):
        """
        Handles the events.
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.select_level_button:
                        self.stop_game_button.visible = 1
                        self.stop_game_button.rect = self.sgb_rect[0]
                        self.stop_game_button.rebuild()
                        self.select_level_button.visible = 1
                        self.select_level_button.rect = self.slb_rect[0]
                        self.select_level_button.rebuild()
                        self.game_on = True
                        self.game = game.Game(1)
                    if event.ui_element == self.stop_game_button:
                        self.select_level_button.visible = 1
                        self.select_level_button.rect = self.slb_rect[1]
                        self.select_level_button.rebuild()
                        self.stop_game_button.visible = 0
                        self.game_on = False
                        self.game = None

            self.manager.process_events(event)
        if self.game_on:
            if not self.game.win:
                self.game.update(events, DT)
            else:
                self.stop_game_button.rect = self.sgb_rect[1]
                self.stop_game_button.rebuild()
                self.select_level_button.rect = self.slb_rect[1]
                self.select_level_button.rebuild()


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