import pygame
import random
from settings import get_default_ships


pygame.mixer.init()
pygame.mixer.music.set_volume(0.2)

shot_sound = pygame.mixer.Sound('assets/sounds/shot.mp3')
miss_sound = pygame.mixer.Sound('assets/sounds/mimo.mp3')
destroy_sound = pygame.mixer.Sound('assets/sounds/ship_destroy.mp3')

shot_sound.set_volume(0.1)
miss_sound.set_volume(0.1)
destroy_sound.set_volume(0.1)

def init_player_grid(size=10):
    """Создает двумерный массив для хранения состояния клеток (0 - пусто, 1 - корабль, 2 - промах, 3 - попадание)"""
    return [[0 for _ in range(size)] for _ in range(size)]

def is_game_over(grid):
    """Проверяет, остались ли неподбитые корабли"""
    for row in grid:
        if 1 in row:  # Если есть хотя бы один неподбитый корабль
            return False
    return True


def computer_turn(player_grid):
    """Улучшенный ИИ: сначала добивает раненые корабли"""
    # 1. Проверить, есть ли подбитые, но не уничтоженные корабли
    for r in range(len(player_grid)):
        for c in range(len(player_grid[0])):
            if player_grid[r][c] == 3:  # Попадание
                # Проверить соседние клетки
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(player_grid) and 0 <= nc < len(player_grid[0]):
                        if player_grid[nr][nc] in (0, 1):
                            return nr, nc

    # 2. Если нет - случайный выстрел
    empty_cells = []
    for r in range(len(player_grid)):
        for c in range(len(player_grid[0])):
            if player_grid[r][c] in (0, 1):
                empty_cells.append((r, c))

    return random.choice(empty_cells) if empty_cells else None


def mark_surrounding_cells(grid, ship_cells):
    """Помечает клетки вокруг уничтоженного корабля как промахи (2)."""
    for (r, c) in ship_cells:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    if grid[nr][nc] == 0:  # Только пустые клетки
                        grid[nr][nc] = 2
    return grid


def generate_computer_ships(grid_size=10):
    """
    Генерирует случайную расстановку кораблей для компьютера.
    Использует ships_to_place из settings.py для соответствия правилам.
    """

    grid = init_player_grid(grid_size)
    ships_to_place = get_default_ships()  # Получаем стандартный набор кораблей

    # Преобразуем словарь в список кораблей (например, {4:1, 3:2} -> [4, 3, 3])
    ships = []
    for ship_size, count in ships_to_place.items():
        ships.extend([ship_size] * count)

    for ship_size in ships:
        placed = False
        attempts = 0
        max_attempts = 100

        while not placed and attempts < max_attempts:
            attempts += 1
            orientation = random.randint(0, 1)  # 0 - горизонтально, 1 - вертикально
            if orientation == 0:
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - ship_size)
                ship_cells = [(row, col + i) for i in range(ship_size)]
            else:
                row = random.randint(0, grid_size - ship_size)
                col = random.randint(0, grid_size - 1)
                ship_cells = [(row + i, col) for i in range(ship_size)]

            if can_place_ship(grid, ship_cells):
                for (r, c) in ship_cells:
                    grid[r][c] = 1
                placed = True

        if not placed:
            print(f"Не удалось разместить {ship_size}-палубный корабль!")

    return grid


def process_shot(grid, cell):
    if cell is None:
        return False

    row, col = cell
    if grid[row][col] == 1:  # Попадание
        grid[row][col] = 3
        ship_cells = find_ship(grid, cell)

        is_ship_destroyed = all(grid[r][c] == 3 for (r, c) in ship_cells)

        if is_ship_destroyed:
            destroy_sound.play()
            mark_surrounding_cells(grid, ship_cells)
        else:
            shot_sound.play()
        return True  # Попадание - ход остается у текущего игрока

    elif grid[row][col] == 0:  # Промах
        grid[row][col] = 2
        miss_sound.play()
        return False  # Промах - ход переходит другому игроку

    return False  # Если уже стреляли сюда


def handle_player_click(cell, player_grid):
    """Обрабатывает клик по клетке: ставит или убирает 'корабль'.
       row, col = cell
       Если в player_grid[row][col] было 0, ставим 1;
       Если было 1, убираем (ставим 0).
    """
    if cell is None:
        return
    row, col = cell
    if player_grid[row][col] == 0:
        player_grid[row][col] = 1
    else:
        player_grid[row][col] = 0


def draw_ships(screen, player_grid, grid_x, grid_y, grid_size, cell_size=40):
    """Рисует состояние клеток:
    - зеленый: корабль (1)
    - красный: попадание (3)
    - белый кружок: промах (2)
    """
    rows = len(player_grid)
    cols = len(player_grid[0]) if rows > 0 else 0
    for r in range(rows):
        for c in range(cols):
            rect_x = grid_x + c * cell_size
            rect_y = grid_y + r * cell_size
            rect = pygame.Rect(rect_x, rect_y, cell_size, cell_size)

            if player_grid[r][c] == 1:  # Корабль
                pygame.draw.rect(screen, (0, 255, 0), rect)
            elif player_grid[r][c] == 3:  # Попадание
                pygame.draw.rect(screen, (255, 0, 0), rect)
            elif player_grid[r][c] == 2:  # Промах
                pygame.draw.circle(screen, (255, 255, 255),
                                   (rect_x + cell_size // 2, rect_y + cell_size // 2),
                                   cell_size // 3)



def highlight_cell(screen, highlighted_cell, grid_x, grid_y, cell_size, color=(0, 255, 0)):
    """Подсвечивает клетку на сетке."""
    if highlighted_cell:
        row, col = highlighted_cell
        rect_x = grid_x + col * cell_size
        rect_y = grid_y + row * cell_size
        rect = pygame.Rect(rect_x, rect_y, cell_size, cell_size)
        pygame.draw.rect(screen, color, rect, 2)



def get_cell(x, y, grid_x, grid_y, grid_size, cell_size):
    """Получает координаты клетки на основе клика"""
    col = (x - grid_x) // cell_size
    row = (y - grid_y) // cell_size

    if 0 <= col < grid_size and 0 <= row < grid_size:
        return row, col
    return None




def can_place_ship(player_grid, ship_cells):
    """
        Проверяет, можно ли поставить корабль на указанный список клеток ship_cells.
        Корабль не должен касаться другого корабля (включая диагонали).
        """
    for (r, c) in ship_cells:
        # Перебираем все 8 соседних клеток (включая диагонали)
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
    """
    Возвращает все клетки корабля, включая подбитые (значения 1 и 3).
    """
    rows = len(player_grid)
    cols = len(player_grid[0]) if rows > 0 else 0
    ship_cells = set()
    to_visit = [start]
    while to_visit:
        r, c = to_visit.pop()
        if (r, c) in ship_cells:
            continue
        if player_grid[r][c] in (1, 3):  # Ищем и корабли, и попадания
            ship_cells.add((r, c))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    to_visit.append((nr, nc))
    return ship_cells


def draw_grid(screen, x, y, grid_size=10, cell_size=40, player="Player"):
    font = pygame.font.Font(None, 30)
    letters = "ABCDEFGHIJ"
    numbers = [str(i + 1) for i in range(grid_size)]

    # Заголовок игрока
    title = font.render(player, True, (255, 255, 255))
    screen.blit(title, (x + (grid_size * cell_size) // 2 - title.get_width() // 2, y - 60))

    # Отрисовка сетки
    for row in range(grid_size):
        for col in range(grid_size):
            rect = pygame.Rect(x + col * cell_size, y + row * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)

            # Буквы (строки)
            if col == 0:
                letter = font.render(letters[row], True, (255, 255, 255))
                screen.blit(letter, (x - 30, y + row * cell_size + cell_size // 4))

            # Цифры (столбцы)
            if row == 0:
                number = font.render(numbers[col], True, (255, 255, 255))
                screen.blit(number, (x + col * cell_size + cell_size // 4, y - 30))



