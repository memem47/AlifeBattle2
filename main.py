import pygame

import config
from game import Game
from renderer import draw_game


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("AlifeBattle v0.1")
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()

        dt = min(clock.tick(config.TARGET_FPS) / 1000.0, config.MAX_DT)
        game.update(dt)
        draw_game(screen, game)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()