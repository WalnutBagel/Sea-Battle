import pygame
import sys
from game import get_cell, find_ship, can_place_ship, process_shot, computer_turn

click_sound = pygame.mixer.Sound('assets/sounds/click.mp3')
click_sound.set_volume(0.2)

def process_menu_events(event, mouse_x, mouse_y, in_menu):
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Проверяем координаты для кнопок "Начать игру" и "Выйти"
        if 200 <= mouse_x <= 600 and 300 <= mouse_y <= 350:
            click_sound.play()
            in_menu = False  # Начать игру
        elif 200 <= mouse_x <= 600 and 400 <= mouse_y <= 450:
            click_sound.play()
            pygame.quit()
            sys.exit()
    return in_menu


def process_game_events(event, mouse_x, mouse_y, left_grid_x, left_grid_y, right_grid_x, right_grid_y, grid_size, cell_size, player_grid, computer_grid, current_cells, is_dragging, start_cell, ships_to_place, player_turn):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Левый клик
            cell = get_cell(mouse_x, mouse_y, left_grid_x, left_grid_y, grid_size, cell_size)
            if cell:
                is_dragging = True
                start_cell = cell
                current_cells = [cell]
            # Проверяем, кликнули ли по правой сетке (выстрелы)
            else:
                cell = get_cell(mouse_x, mouse_y, right_grid_x, right_grid_y, grid_size, cell_size)
                if cell and all(count == 0 for count in ships_to_place.values()) and player_turn:
                    if computer_grid[cell[0]][cell[1]] in (0, 1):
                        hit = process_shot(computer_grid, cell)  # Всегда обрабатываем выстрел
                        player_turn = hit
                        if not hit:
                            # Если игрок промахнулся, ход переходит компьютеру
                            return is_dragging, start_cell, current_cells, False
                        # computer_cell = computer_turn(player_grid)  # Компьютер стреляет в любом случае
                        # if computer_cell:
                        #     process_shot(player_grid, computer_cell)

        elif event.button == 3:  # Правый клик - удаление корабля
            cell = get_cell(mouse_x, mouse_y, left_grid_x, left_grid_y, grid_size, cell_size)
            if cell:
                row, col = cell
                if player_grid[row][col] == 1:
                    ship_cells = find_ship(player_grid, cell)
                    ship_size = len(ship_cells)
                    for (r, c) in ship_cells:
                        player_grid[r][c] = 0
                    if ship_size in ships_to_place:
                        ships_to_place[ship_size] += 1
                    else:
                        ships_to_place[ship_size] = 1
                    print(f"Корабль размером {len(ship_cells)} удалён из клетки: {cell}")
    elif event.type == pygame.MOUSEMOTION and is_dragging:
        cell = get_cell(mouse_x, mouse_y, left_grid_x, left_grid_y, grid_size, cell_size)
        if cell and start_cell:
            row1, col1 = start_cell
            row2, col2 = cell
            dx = abs(col2 - col1)
            dy = abs(row2 - row1)
            current_cells = []
            if dx > dy:
                row2 = row1  # фиксируем горизонталь
                cmin, cmax = min(col1, col2), max(col1, col2)
                length = cmax - cmin + 1
                if length > 4:
                    if col2 >= col1:
                        cmax = col1 + 3
                    else:
                        cmin = col1 - 3
                for c in range(cmin, cmax + 1):
                    current_cells.append((row1, c))
            else:
                col2 = col1  # фиксируем вертикаль
                rmin, rmax = min(row1, row2), max(row1, row2)
                length = rmax - rmin + 1
                if length > 4:
                    if row2 >= row1:
                        rmax = row1 + 3
                    else:
                        rmin = row1 - 3
                for r in range(rmin, rmax + 1):
                    current_cells.append((r, col1))
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        if is_dragging:
            # Проверка пересечений и соседства
            intersect = False
            for (r, c) in current_cells:
                if player_grid[r][c] == 1:
                    intersect = True
                    break

            ship_size = len(current_cells)

            if not intersect and can_place_ship(player_grid, current_cells):
                if ship_size in ships_to_place and ships_to_place[ship_size] > 0:
                    for (r, c) in current_cells:
                        player_grid[r][c] = 1
                    ships_to_place[ship_size] -= 1
                else:
                    print("Нет доступных крааблей такого размера!")
            else:
                print("Невозможно поставить корабль: пересечение или нарушение соседства!")
            is_dragging = False
            start_cell = None
            current_cells = []

    return is_dragging, start_cell, current_cells, player_turn