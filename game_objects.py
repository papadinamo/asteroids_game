import pygame
import math
import random
import os
from config import *


class GameObject:
    """Базовый класс для всех игровых объектов с поддержкой изображений"""

    def __init__(self, x, y, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.angle = 0
        self.active = True
        self.image = None
        self.original_image = None
        self.rect = None

    def load_image(self, image_path, scale=1.0):
        """Загрузка и масштабирование изображения"""
        try:
            if os.path.exists(image_path):
                self.original_image = pygame.image.load(image_path).convert_alpha()
                if scale != 1.0:
                    new_width = int(self.original_image.get_width() * scale)
                    new_height = int(self.original_image.get_height() * scale)
                    self.original_image = pygame.transform.scale(self.original_image, (new_width, new_height))
                self.image = self.original_image
                self.rect = self.image.get_rect(center=(self.x, self.y))
                return True
            else:
                print(f"Файл {image_path} не найден")
                return False
        except pygame.error as e:
            print(f"Ошибка загрузки изображения {image_path}: {e}")
            return False

    def update_image_rotation(self):
        """Обновление поворота изображения"""
        if self.original_image:
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            old_center = self.rect.center if self.rect else (self.x, self.y)
            self.rect = self.image.get_rect(center=old_center)

    def update(self):
        """Обновление позиции объекта"""
        self.x += self.vx
        self.y += self.vy

        # Тороидальная геометрия
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0

        # Обновление rect для отрисовки
        if self.rect and self.image:
            self.rect.center = (self.x, self.y)

    def draw(self, screen):
        """Отрисовка объекта с изображением"""
        if self.image and self.rect:
            screen.blit(self.image, self.rect)
        else:
            # Резервная отрисовка (красный прямоугольник)
            pygame.draw.rect(screen, RED, (self.x - 10, self.y - 10, 20, 20), 2)

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        if self.rect:
            return self.rect
        else:
            return pygame.Rect(self.x - 10, self.y - 10, 20, 20)


class Ship(GameObject):
    """Класс корабля игрока с поддержкой изображений"""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.acceleration = 0
        self.thrusting = False
        self.size = SHIP_SIZE

        # Загрузка изображений корабля
        self.ship_image_normal = None
        self.ship_image_thrust = None
        self.load_ship_images()

    def load_ship_images(self):
        """Загрузка изображений корабля для разных состояний"""
        # Основное изображение корабля
        if not self.load_image("pictures/ship.png", 0.5):
            # Если изображение не загружено, создаем простое
            self.create_ship_image()

        # Сохраняем нормальное изображение
        self.ship_image_normal = self.original_image

        # Загружаем изображение с работающими двигателями
        if os.path.exists("ship_thrust.png"):
            thrust_image = pygame.image.load("ship_thrust.png").convert_alpha()
            thrust_image = pygame.transform.scale(thrust_image,
                                                  (self.ship_image_normal.get_width(),
                                                   self.ship_image_normal.get_height()))
            self.ship_image_thrust = thrust_image
        else:
            # Создаем изображение с двигателями
            self.ship_image_thrust = self.create_thrust_image()

    def create_ship_image(self):
        """Создание изображения корабля программно (резервный вариант)"""
        size = 40
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Корпус корабля (треугольник)
        points = [
            (size // 2, 0),  # нос
            (0, size),  # левый низ
            (size, size)  # правый низ
        ]
        pygame.draw.polygon(surface, WHITE, points)

        # Детали
        pygame.draw.polygon(surface, BLUE, [(size // 2, size // 3), (size // 4, size), (size * 3 // 4, size)])

        self.original_image = surface
        self.image = surface
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def create_thrust_image(self):
        """Создание изображения корабля с работающими двигателями"""
        if not self.ship_image_normal:
            return None

        # Копируем нормальное изображение
        thrust_surface = self.ship_image_normal.copy()

        # Добавляем эффект пламени
        size = thrust_surface.get_size()
        flame_points = [
            (size[0] // 2, size[1]),  # центр
            (size[0] // 3, size[1] + 15),  # левый
            (size[0] // 2, size[1] + 25),  # центр низ
            (size[0] * 2 // 3, size[1] + 15)  # правый
        ]
        pygame.draw.polygon(thrust_surface, YELLOW, flame_points)
        pygame.draw.polygon(thrust_surface, RED, [
            (size[0] // 2, size[1] + 5),
            (size[0] // 2.5, size[1] + 15),
            (size[0] // 2, size[1] + 20),
            (size[0] * 1.5 // 2, size[1] + 15)
        ])

        return thrust_surface

    def rotate(self, direction):
        """Вращение корабля"""
        self.angle += direction * SHIP_ROTATION_SPEED
        self.update_image_rotation()

    def thrust(self):
        """Включение двигателей"""
        self.thrusting = True
        # Ускорение в направлении носа корабля
        angle_rad = math.radians(self.angle)
        self.acceleration = SHIP_ACCELERATION
        self.vx += math.sin(angle_rad) * self.acceleration
        self.vy += -math.cos(angle_rad) * self.acceleration

        # Смена изображения на корабль с двигателями
        if self.ship_image_thrust:
            self.original_image = self.ship_image_thrust
            self.update_image_rotation()

    def stop_thrust(self):
        """Выключение двигателей"""
        self.thrusting = False
        self.acceleration = 0

        # Возврат к нормальному изображению
        if self.ship_image_normal:
            self.original_image = self.ship_image_normal
            self.update_image_rotation()

    def update(self):
        """Обновление состояния корабля"""
        # Применение трения при выключенных двигателях
        if not self.thrusting:
            self.vx *= SHIP_FRICTION
            self.vy *= SHIP_FRICTION

        super().update()

    def get_nose_position(self):
        """Возвращает позицию носа корабля для выстрела"""
        if self.image and self.rect:
            # Используем реальные размеры изображения
            angle_rad = math.radians(self.angle)
            distance = self.rect.height // 2 + 5
            nose_x = self.x + math.sin(angle_rad) * distance
            nose_y = self.y - math.cos(angle_rad) * distance
        else:
            # Резервный расчет
            angle_rad = math.radians(self.angle)
            nose_x = self.x + math.sin(angle_rad) * self.size
            nose_y = self.y - math.cos(angle_rad) * self.size

        return nose_x, nose_y


class Bullet(GameObject):
    """Класс ракеты с графическим изображением"""

    def __init__(self, x, y, angle):
        # Начальная скорость в направлении выстрела
        angle_rad = math.radians(angle)
        vx = math.sin(angle_rad) * BULLET_SPEED
        vy = -math.cos(angle_rad) * BULLET_SPEED

        super().__init__(x, y, vx, vy)
        self.angle = angle
        self.lifetime = BULLET_LIFETIME

        # Загрузка изображения ракеты
        if not self.load_image("pictures/rocket.png", 0.3):
            self.create_rocket_image()

    def create_rocket_image(self):
        """Создание изображения ракеты программно"""
        surface = pygame.Surface((20, 40), pygame.SRCALPHA)

        # Корпус ракеты
        points = [
            (10, 0),  # нос
            (5, 15),  # левый верх
            (5, 35),  # левый низ
            (15, 35),  # правый низ
            (15, 15)  # правый верх
        ]
        pygame.draw.polygon(surface, WHITE, points)

        # Нос ракеты
        pygame.draw.polygon(surface, RED, [
            (10, 0),
            (7, 8),
            (13, 8)
        ])

        # Пламя
        pygame.draw.polygon(surface, (255, 165, 0), [  # оранжевый
            (7, 35),
            (10, 40),
            (13, 35)
        ])

        self.original_image = surface
        self.update_image_rotation()

    def update(self):
        """Обновление состояния ракеты"""
        super().update()
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False


class Asteroid(GameObject):
    """Класс астероида с графическим изображением"""

    def __init__(self, x=None, y=None):
        # Случайная позиция, если не задана
        if x is None or y is None:
            side = random.randint(0, 3)
            if side == 0:  # верх
                x = random.randint(0, SCREEN_WIDTH)
                y = -50
            elif side == 1:  # право
                x = SCREEN_WIDTH + 50
                y = random.randint(0, SCREEN_HEIGHT)
            elif side == 2:  # низ
                x = random.randint(0, SCREEN_WIDTH)
                y = SCREEN_HEIGHT + 50
            else:  # лево
                x = -50
                y = random.randint(0, SCREEN_HEIGHT)

        # Случайная скорость и вращение
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        super().__init__(x, y, vx, vy)

        self.rotation_speed = random.uniform(ASTEROID_MIN_ROTATION, ASTEROID_MAX_ROTATION)
        self.size = random.randint(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)

        # Загрузка изображения астероида
        asteroid_images = ["asteroid1.png", "asteroid2.png", "asteroid3.png"]
        selected_image = random.choice(asteroid_images)

        # Масштабирование в зависимости от размера
        scale = self.size / 40.0  # 40 - базовый размер

        if not self.load_image(selected_image, scale):
            self.create_asteroid_image()

    def create_asteroid_image(self):
        """Создание изображения астероида программно"""
        size = self.size
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        # Создаем неправильную форму астероида
        points = []
        num_points = random.randint(8, 12)
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            distance = size * random.uniform(0.7, 1.0)
            x = size + math.cos(angle) * distance
            y = size + math.sin(angle) * distance
            points.append((x, y))

        # Рисуем астероид
        pygame.draw.polygon(surface, (150, 150, 150), points)  # серый
        pygame.draw.polygon(surface, (100, 100, 100), points, 2)  # контур

        # Добавляем кратеры
        for _ in range(random.randint(2, 5)):
            crater_x = random.randint(size // 4, size * 3 // 2)
            crater_y = random.randint(size // 4, size * 3 // 2)
            crater_size = random.randint(size // 8, size // 4)
            pygame.draw.circle(surface, (120, 120, 120), (crater_x, crater_y), crater_size)

        self.original_image = surface
        self.update_image_rotation()

    def update(self):
        """Обновление состояния астероида"""
        self.angle += self.rotation_speed
        self.update_image_rotation()
        super().update()


class Explosion:
    """Класс анимации взрыва"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = EXPLOSION_DURATION
        self.max_radius = 30
        self.active = True

        # Попытка загрузить изображение взрыва
        self.explosion_images = []
        self.load_explosion_images()
        self.current_frame = 0

    def load_explosion_images(self):
        """Загрузка изображений для анимации взрыва"""
        try:
            # Попробуем загрузить последовательность кадров взрыва
            for i in range(1, 6):  # explosion1.png, explosion2.png, ...
                img_path = f"explosion{i}.png"
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    img = pygame.transform.scale(img, (60, 60))
                    self.explosion_images.append(img)
        except:
            self.explosion_images = []  # Будем использовать графику

    def update(self):
        """Обновление состояния взрыва"""
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
        else:
            # Обновление кадра анимации
            if self.explosion_images:
                progress = 1 - (self.timer / EXPLOSION_DURATION)
                self.current_frame = int(progress * (len(self.explosion_images) - 1))

    def draw(self, screen):
        """Отрисовка взрыва"""
        if self.explosion_images and 0 <= self.current_frame < len(self.explosion_images):
            # Рисуем кадр анимации
            img_rect = self.explosion_images[self.current_frame].get_rect(center=(self.x, self.y))
            screen.blit(self.explosion_images[self.current_frame], img_rect)
        else:
            # Графическое представление взрыва
            progress = 1 - (self.timer / EXPLOSION_DURATION)
            radius = int(self.max_radius * (1 - progress))

            if radius > 0:
                # Основной круг взрыва
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), radius)

                # Внешние частицы
                for i in range(8):
                    angle = 2 * math.pi * i / 8
                    particle_distance = radius * 1.5
                    particle_x = self.x + math.cos(angle) * particle_distance
                    particle_y = self.y + math.sin(angle) * particle_distance
                    particle_size = max(1, int(radius * 0.3))
                    pygame.draw.circle(screen, RED, (int(particle_x), int(particle_y)), particle_size)

# Пути к изображениям
BACKGROUND_IMAGE_PATH = "pictures/background.png"
SHIP_IMAGE_PATH = "pictures/ship.png"
SHIP_THRUST_IMAGE_PATH = "pictures/ship_thrust.png"
BULLET_IMAGE_PATH = "pictures/rocket.png"
ASTEROID_IMAGES = ["asteroid1.png", "asteroid2.png", "asteroid3.png"]
EXPLOSION_IMAGES = ["explosion1.png", "explosion2.png", "explosion3.png", "explosion4.png", "explosion5.png"]