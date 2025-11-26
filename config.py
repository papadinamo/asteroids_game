"""
Конфигурационные параметры игры Астероиды
"""

# Размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)

# Параметры корабля
SHIP_SPEED = 0.2
SHIP_ROTATION_SPEED = 3
SHIP_ACCELERATION = 0.1
SHIP_FRICTION = 0.98
SHIP_SIZE = 20

# Параметры ракет
BULLET_SPEED = 7
BULLET_LIFETIME = 60  # в кадрах
BULLET_SIZE = 3

# Параметры астероидов
ASTEROID_MIN_SPEED = 1
ASTEROID_MAX_SPEED = 3
ASTEROID_MIN_ROTATION = -2
ASTEROID_MAX_ROTATION = 2
ASTEROID_MIN_SIZE = 20
ASTEROID_MAX_SIZE = 50
ASTEROID_SPAWN_RATE = 60  # кадры между появлениями

# Игровые параметры
INITIAL_LIVES = 3
INITIAL_SCORE = 0
EXPLOSION_DURATION = 20  # в кадрах

# Заголовки и тексты
GAME_TITLE = "АСТЕРОИДЫ"
START_TEXT = "Щелкните для начала игры"
GAME_OVER_TEXT = "ИГРА ОКОНЧЕНА"
SCORE_TEXT = "Очки: "
LIVES_TEXT = "Жизни: "