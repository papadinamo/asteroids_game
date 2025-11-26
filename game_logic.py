import pygame
import random
import math
from game_objects import Ship, Bullet, Asteroid, Explosion
from config import *


class GameLogic:
    """Класс, управляющий логикой игры"""

    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """Сброс состояния игры к начальному"""
        self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.bullets = []
        self.asteroids = []
        self.explosions = []
        self.score = INITIAL_SCORE
        self.lives = INITIAL_LIVES
        self.game_state = "start"
        self.asteroid_timer = 0
        self.background_offset = 0

    def handle_events(self, events):
        """Обработка событий игры"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == "start":
                    # Проверка щелчка по заставке
                    title_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 100)
                    if title_rect.collidepoint(event.pos):
                        self.game_state = "playing"
                elif self.game_state == "game_over":
                    # Перезапуск игры при щелчке
                    self.reset_game()
                    self.game_state = "playing"

        if self.game_state == "playing":
            keys = pygame.key.get_pressed()

            # Вращение корабля
            if keys[pygame.K_LEFT]:
                self.ship.rotate(-1)
            if keys[pygame.K_RIGHT]:
                self.ship.rotate(1)

            # Ускорение корабля
            if keys[pygame.K_UP]:
                self.ship.thrust()
            else:
                self.ship.stop_thrust()

            # Выстрел
            if keys[pygame.K_SPACE]:
                if not hasattr(self, 'last_shot') or pygame.time.get_ticks() - self.last_shot > 300:
                    nose_x, nose_y = self.ship.get_nose_position()
                    self.bullets.append(Bullet(nose_x, nose_y, self.ship.angle))
                    self.last_shot = pygame.time.get_ticks()

    def update(self):
        """Обновление состояния игры"""
        if self.game_state != "playing":
            return

        # Обновление фона
        self.background_offset = (self.background_offset - 1) % SCREEN_WIDTH

        # Обновление корабля
        self.ship.update()

        # Обновление ракет
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

        # Генерация астероидов
        self.asteroid_timer += 1
        if self.asteroid_timer >= ASTEROID_SPAWN_RATE:
            self.asteroids.append(Asteroid())
            self.asteroid_timer = 0

        # Обновление астероидов
        for asteroid in self.asteroids[:]:
            asteroid.update()

        # Обновление взрывов
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)

        # Проверка столкновений ракет с астероидами
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if (bullet.get_rect().colliderect(asteroid.get_rect()) and
                        self.distance(bullet.x, bullet.y, asteroid.x, asteroid.y) < asteroid.size):
                    self.explosions.append(Explosion(asteroid.x, asteroid.y))
                    self.asteroids.remove(asteroid)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.score += 1
                    break

        # Проверка столкновений корабля с астероидами
        for asteroid in self.asteroids[:]:
            if (self.ship.get_rect().colliderect(asteroid.get_rect()) and
                    self.distance(self.ship.x, self.ship.y, asteroid.x, asteroid.y) <
                    (self.ship.size + asteroid.size)):
                self.explosions.append(Explosion(asteroid.x, asteroid.y))
                self.asteroids.remove(asteroid)
                self.lives -= 1

                if self.lives <= 0:
                    self.game_state = "game_over"
                else:
                    # Возрождение корабля
                    self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                break

    def distance(self, x1, y1, x2, y2):
        """Вычисление расстояния между двумя точками"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def __init__(self):
        self.reset_game()
        self.load_images()

    def load_images(self):
        """Загрузка изображений для игры"""
        try:
            # Загрузка фонового изображения
            self.background_image = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
            # Масштабирование изображения под размер экрана
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            # Установка прозрачности
            self.background_image.set_alpha(128)
        except pygame.error as e:
            print(f"Не удалось загрузить фоновое изображение: {e}")
            print("Будет использован стандартный фон")
            self.background_image = None

    def draw_background(self, screen):
        """Отрисовка фона с изображением"""
        # Заливка черным цветом как базовый фон
        screen.fill(BLACK)

        if self.background_image is not None:
            # Создаем поверхность для фона с движением
            bg_width = self.background_image.get_width()

            # Рисуем два изображения для бесшовной прокрутки
            screen.blit(self.background_image, (self.background_offset, 0))
            screen.blit(self.background_image, (self.background_offset - bg_width, 0))
        else:
            # Стандартный фон
            bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

            # Рисуем фоновые астероиды
            for i in range(5):
                x = (self.background_offset + i * 200) % SCREEN_WIDTH
                for j in range(4):
                    y = j * 150
                    size = 15 + i * 2

                    # Простой астероид для фона
                    points = []
                    num_points = 6
                    for k in range(num_points):
                        angle = 2 * math.pi * k / num_points
                        distance = size * random.uniform(0.8, 1.0)
                        points.append((x + math.cos(angle) * distance,
                                       y + math.sin(angle) * distance))

                    pygame.draw.polygon(bg_surface, (100, 100, 100, 100), points, 1)

            screen.blit(bg_surface, (0, 0))

    def draw_ui(self, screen, font):
        """Отрисовка интерфейса пользователя"""
        # Отображение счета
        score_text = font.render(f"{SCORE_TEXT}{self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Отображение жизней
        lives_text = font.render(f"{LIVES_TEXT}{self.lives}", True, WHITE)
        screen.blit(lives_text, (10, 40))

        # Отображение жизней в виде кораблей
        for i in range(self.lives):
            life_ship = Ship(SCREEN_WIDTH - 50 - i * 40, 30)
            life_ship.size = 15
            life_ship.draw(screen)

    def draw_start_screen(self, screen, font, big_font):
        """Отрисовка начального экрана"""
        self.draw_background(screen)

        # Заголовок игры
        title_text = big_font.render(GAME_TITLE, True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(title_text, title_rect)

        # Инструкция
        start_text = font.render(START_TEXT, True, GREEN)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(start_text, start_rect)

        # Управление
        controls = [
            "Управление:",
            "Стрелки ← → - вращение",
            "Стрелка ↑ - ускорение",
            "Пробел - выстрел"
        ]

        for i, text in enumerate(controls):
            control_text = font.render(text, True, BLUE)
            screen.blit(control_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100 + i * 30))

    def draw_game_over(self, screen, font, big_font):
        """Отрисовка экрана окончания игры"""
        self.draw_background(screen)

        # Сообщение о конце игры
        game_over_text = big_font.render(GAME_OVER_TEXT, True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)

        # Финальный счет
        final_score = font.render(f"Финальный счет: {self.score}", True, WHITE)
        score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(final_score, score_rect)

        # Инструкция для перезапуска
        restart_text = font.render("Щелкните для новой игры", True, GREEN)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        screen.blit(restart_text, restart_rect)

BACKGROUND_IMAGE_PATH = "pictures/background.png"
