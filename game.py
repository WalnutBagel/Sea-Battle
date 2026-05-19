import pygame
import random
from settings import get_default_ships

pygame.mixer.init()
pygame.mixer.music.set_volume(0.2)

shot_sound = pygame.mixer.Sound('assets/sounds/shot.mp3')
destroy_sound = pygame.mixer.Sound('assets/sounds/explosive.mp3')
plux_sound = pygame.mixer.Sound('assets/sounds/promax.mp3')
ship_sound = pygame.mixer.Sound('assets/sounds/ship.mp3')

shot_sound.set_volume(0.1)
destroy_sound.set_volume(0.4)
plux_sound.set_volume(0.1)



class ShotAnimation:
    def __init__(self, x, y, is_hit):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 50 if is_hit else 30  # Увеличиваем радиус
        self.color = (255, 50, 50) if is_hit else (180, 180, 255)  # Яркие цвета
        self.alpha = 255  # Добавляем прозрачность
        self.active = True

    def update(self):
        self.radius += 1  # Ускоряем анимацию
        self.alpha -= 5  # Постепенное исчезновение
        if self.radius > self.max_radius or self.alpha <= 0:
            self.active = False

    def draw(self, screen):
        if self.active:
            # Создаем поверхность с прозрачностью
            surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(
                surface,
                (*self.color, self.alpha),  # RGB + Alpha
                (self.radius, self.radius),
                self.radius,
                3  # Толщина линии
            )
            screen.blit(surface, (self.x - self.radius, self.y - self.radius))

# Глобальный список анимаций (добавить после класса)
shot_animations = []

def draw_grid(screen, x, y, player='Player', grid_size=10, cell_size=40):
    # символы
    title_font = pygame.font.Font(None, 45)  # шрифт для заголовка`
    letter_font = pygame.font.Font(None, 30)  # шрифт для букв и чисел
    letters = "АБВГДЕЖЗИК"
    numbers = [str(i + 1) for i in range(grid_size)]

    # Заголовок игрока
    title = title_font.render(player, True, (255, 255, 255))
    screen.blit(title, (x + (grid_size * cell_size) // 2 - title.get_width() // 2, y - 80))

    # отрисовка сетки
    for row in range(grid_size):
        for col in range(grid_size):
            rect = pygame.Rect(x + col * cell_size, y + row * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)

            # буквы
            if col == 0:
                letter = letter_font.render(letters[row], True, (255, 255, 255))
                screen.blit(letter, (x - 30, y + cell_size * row + cell_size // 4))

            # цифры
            if row == 0:
                number = letter_font.render(numbers[col], True, (255, 255, 255))
                screen.blit(number, (x + cell_size * col + cell_size // 4, y - 30))

def get_cell(x, y, grid_x, grid_y, grid_size, cell_size):
    col = (x - grid_x) // cell_size
    row = (y - grid_y) // cell_size
    if 0 <= col < grid_size and 0 <= row < grid_size:
        return row, col
    return None

def highlight_cell(screen, highlighted_cell, grid_x, grid_y, cell_size, color=(0, 255, 0)):
    if highlighted_cell:
        row, col = highlighted_cell
        rect_x = grid_x + col * cell_size
        rect_y = grid_y + row * cell_size
        rect = pygame.Rect(rect_x, rect_y, cell_size, cell_size)
        pygame.draw.rect(screen, color, rect, 2)

def init_player_grid(size=10):
    # Создает двумерный массив для хранения состояния клеток (0 - пусто, 1 - корабль)
    return [[0 for _ in range(size)] for _ in range(size)]

def generate_computer_ships(grid_size=10):
    grid = init_player_grid(grid_size)
    ships_to_place = get_default_ships()
    generate_random_ships(grid, ships_to_place, grid_size)  # Используем общую функцию
    return grid

def generate_random_ships(grid, ships_to_place, grid_size=10):
    """Универсальная функция для генерации кораблей"""
    # Сброс счетчика кораблей
    ships_to_place.update(get_default_ships())  # Восстанавливаем исходное количество
    # Очистка сетки
    for row in range(grid_size):
        for col in range(grid_size):
            grid[row][col] = 0

    # Используем ту же логику, что и для компьютера
    ships = []
    for ship_size, count in ships_to_place.items():
        ships.extend([ship_size] * count)

    for ship_size in ships:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            attempts += 1
            orientation = random.randint(0, 1)
            if orientation == 0:  # Горизонтально
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - ship_size)
                cells = [(row, col + i) for i in range(ship_size)]
            else:  # Вертикально
                col = random.randint(0, grid_size - 1)
                row = random.randint(0, grid_size - ship_size)
                cells = [(row + i, col) for i in range(ship_size)]

            if can_place_ship(grid, cells):
                for (r, c) in cells:
                    grid[r][c] = 1
                placed = True

    # Обнуление счетчика
    for size in ships_to_place:
        ships_to_place[size] = 0



def handle_player_click(cell, player_grid):
    if cell is None:
        return
    row, col = cell
    if player_grid[row][col] == 0:
        player_grid[row][col] = 1
    else:
        player_grid[row][col] = 0

def draw_ships(screen, player_grid, grid_x, grid_y, grid_size, cell_size=40, show_ships=True):
    for row in range(grid_size):
        for col in range(grid_size):
            rect_x = grid_x + col * cell_size
            rect_y = grid_y + row * cell_size
            rect = pygame.Rect(rect_x, rect_y, cell_size, cell_size)
            if player_grid[row][col] == 1 and show_ships:
                pygame.draw.rect(screen, (0, 255, 0), rect)
            elif player_grid[row][col] == 3:
                pygame.draw.rect(screen, (255, 0, 0), rect)
            elif player_grid[row][col] == 2:
                pygame.draw.circle(screen, (255, 255, 255), (rect_x + cell_size//2, rect_y + cell_size//2),
                             cell_size//3)

def can_place_ship(player_grid, ship_cells):
    """
        Проверяет, можно ли поставить корабль на указанный список клеток ship_cells.
        Корабль не должен касаться другого корабля (включая диагонали).
    """
    for (r,c) in ship_cells:
        # перебираем все 8 соседних клеток
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                # Если соседняя клетка входит в выбранный отрезок, её можно игнорировать
                if (nr, nc) in ship_cells:
                    continue
                if 0 <= nr < len(player_grid) and 0 <= nc < len(player_grid[0]):
                    if player_grid[nr][nc] == 1:
                        return False
    return True

def find_ship(player_grid, start):
    rows = len(player_grid)
    cols = len(player_grid[0]) if rows > 0 else 0
    ship_cells = set()
    to_visit = [start]
    while to_visit:
        r, c = to_visit.pop()
        if (r, c) in ship_cells:
            continue
        if player_grid[r][c] in (1, 3):
            ship_cells.add((r, c))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4 направления
                nr, nc = r + dr, c + dc  # Новые координаты

                if 0 <= nr < rows and 0 <= nc < cols:  # Если в пределах сетки
                    to_visit.append((nr, nc))  # Добавляем в очередь
    return ship_cells


def process_shot(grid, cell, grid_x, grid_y, cell_size):
    global shot_animations  # доступ к списку анимаций

    if cell is None:
        return False

    row, col = cell
    hit = False

    # Координаты для анимации (центр клетки)
    anim_x = grid_x + col * cell_size + cell_size // 2
    anim_y = grid_y + row * cell_size + cell_size // 2

    # Логика обработки выстрела
    if grid[row][col] == 1:
        grid[row][col] = 3  # попадание
        ship_cells = find_ship(grid, cell)
        is_ship_destroyed = all(grid[r][c] == 3 for (r, c) in ship_cells)

        if is_ship_destroyed:
            mark_surrounding_cells(grid, ship_cells)
            destroy_sound.play()
        else:
            shot_sound.play()
        hit = True

    elif grid[row][col] == 0:
        grid[row][col] = 2  # промах
        plux_sound.play()
        hit = False

    # Добавляем анимацию ВНЕ ЗАВИСИМОСТИ ОТ РЕЗУЛЬТАТА
    shot_animations.append(ShotAnimation(anim_x, anim_y, hit))

    return hit

def mark_surrounding_cells(grid, ships_cells):
    for (r, c) in ships_cells:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    if grid[nr][nc] == 0:  # Только пустые клетки
                        grid[nr][nc] = 2
    return grid


def computer_turn(player_grid):
    targets = []
    # Собираем все возможные цели вокруг подбитых клеток (3)
    for r in range(len(player_grid)):
        for c in range(len(player_grid[0])):
            if player_grid[r][c] == 3:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < len(player_grid) and
                            0 <= nc < len(player_grid[0]) and
                            player_grid[nr][nc] in (0, 1)):
                        targets.append((nr, nc))

    # Удаляем дубликаты целей
    targets = list(set(targets))

    if targets:
        return random.choice(targets)

    # Собираем все доступные клетки через списковое включение
    empty_cells = [
        (r, c)
        for r in range(len(player_grid))
        for c in range(len(player_grid[0]))
        if player_grid[r][c] in (0, 1)
    ]

    return random.choice(empty_cells) if empty_cells else None

def is_game_over(grid):
    """Проверяет, остались ли неподбитые корабли (значение 1)."""
    for row in grid:
        if 1 in row:
            return False
    return True



def count_remaining_ships(grid):
    """
    Подсчитывает количество кораблей, у которых есть хотя бы одна неповрежденная клетка (1).
    Возвращает словарь {размер_корабля: количество}.
    """
    grid_size = len(grid)
    visited = set()
    ships_count = {}

    for r in range(grid_size):
        for c in range(grid_size):
            # Если клетка часть корабля и мы её еще не считали
            if grid[r][c] in (1, 3) and (r, c) not in visited:
                # Находим весь корабль
                ship_cells = find_ship(grid, (r, c))
                visited.update(ship_cells)
                
                # Проверяем, есть ли живые клетки (1)
                # Если все клетки 3 - корабль убит, не считаем его
                if any(grid[r][c] == 1 for (r, c) in ship_cells):
                    size = len(ship_cells)
                    ships_count[size] = ships_count.get(size, 0) + 1
                    
    return ships_count
    