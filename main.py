import pygame
import sys
from game_logic import GameLogic
from config import *


def main():
    """Основная функция игры"""
    # Инициализация Pygame
    pygame.init()

    # Создание окна
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Астероиды")

    # Создание игровой логики
    game = GameLogic()

    # Шрифты
    font = pygame.font.SysFont('Arial', 24)
    big_font = pygame.font.SysFont('Arial', 48, bold=True)

    # Часы для контроля FPS
    clock = pygame.time.Clock()

    # Главный игровой цикл
    running = True
    while running:
        # Обработка событий
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Обработка игровых событий
        game.handle_events(events)

        # Обновление игры
        game.update()

        # Отрисовка
        if game.game_state == "start":
            game.draw_start_screen(screen, font, big_font)
        elif game.game_state == "playing":
            game.draw_background(screen)

            # Отрисовка игровых объектов
            for asteroid in game.asteroids:
                asteroid.draw(screen)

            for bullet in game.bullets:
                bullet.draw(screen)

            for explosion in game.explosions:
                explosion.draw(screen)

            game.ship.draw(screen)
            game.draw_ui(screen, font)
        elif game.game_state == "game_over":
            game.draw_game_over(screen, font, big_font)
            game.draw_ui(screen, font)

        # Обновление экрана
        pygame.display.flip()

        # Контроль FPS
        clock.tick(60)

    # Завершение Pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()