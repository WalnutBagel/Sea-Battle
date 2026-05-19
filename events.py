import pygame
import sys
from game import get_cell, find_ship, can_place_ship, process_shot, generate_random_ships
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SHOW_ENEMY_TOGGLE_BUTTON

click_sound = pygame.mixer.Sound('assets/sounds/click.mp3')

def process_menu_events(event, mouse_x, mouse_y, in_menu):
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Начать игру
        if 200 <= mouse_x <= 700 and 300 <= mouse_y <= 350:
            click_sound.play()
            in_menu = False
        # Выход
        elif 200 <= mouse_x <= 700 and 400 <= mouse_y <= 450:
            click_sound.play()
            pygame.quit()
            sys.exit()
    return in_menu

def process_game_events(event, mouse_x, mouse_y, left_grid_x,left_grid_y, right_grid_x, right_grid_y, grid_size,
                        cell_size,player_grid, computer_grid, current_cells, is_dragging, start_cell
                        , ships_to_place, player_turn, game_phase, show_enemy_ships=False):
    # клик на сетку игрока
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Клик по кнопке "Случайная расстановка"
        if (50 <= mouse_x <= 350) and (50 <= mouse_y <= 90):
            if not all(count == 0 for count in ships_to_place.values()):
                generate_random_ships(player_grid, ships_to_place)
                print("Корабли переставлены!")
        # === КЛИК ПО КНОПКЕ "ПОКАЗАТЬ/СКРЫТЬ" (управляется настройкой) ===
        if SHOW_ENEMY_TOGGLE_BUTTON:
            if (SCREEN_WIDTH - 250 <= mouse_x <= SCREEN_WIDTH - 50) and (50 <= mouse_y <= 90):
                show_enemy_ships = not show_enemy_ships
                click_sound.play()
                print("Показ кораблей противника:", show_enemy_ships)
        if (game_phase == "placing"
                and all(count == 0 for count in ships_to_place.values())
                and event.type == pygame.MOUSEBUTTONDOWN
                and (SCREEN_WIDTH // 2 - 150 <= mouse_x <= SCREEN_WIDTH // 2 + 150)
                and (50 <= mouse_y <= 90)):
            game_phase = "battle"  # Переход в фазу боя
            click_sound.play()
            return is_dragging, start_cell, current_cells, player_turn, game_phase, show_enemy_ships
        if event.button == 1:  # Левый клик
            cell = get_cell(mouse_x, mouse_y, left_grid_x, left_grid_y, grid_size, cell_size)
            if cell:
                is_dragging = True
                start_cell = cell
                current_cells = [cell]
            else:
                cell = get_cell(mouse_x, mouse_y, right_grid_x, right_grid_y, grid_size, cell_size)
                if cell and game_phase == "battle" and player_turn:
                    if computer_grid[cell[0]][cell[1]] in (0, 1):
                        hit = process_shot(
                            computer_grid,
                            cell,
                            right_grid_x,  # передаем координаты сетки компьютера
                            right_grid_y,
                            cell_size  # из параметров функции
                        )
                        player_turn = hit
                        if not hit:
                            return is_dragging, start_cell, current_cells, False, game_phase, show_enemy_ships
                        # computer_cell = computer_turn(player_grid)
                        # if computer_cell:
                        #     process_shot(player_grid, computer_cell)
        elif event.button == 3:  # Правый клик - удаление корабля
            if game_phase != "placing":
                return is_dragging, start_cell, current_cells, player_turn, game_phase, show_enemy_ships
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
                row2 = row1
                c_min, c_max = min(col1, col2), max(col1, col2)
                length = c_max - c_min + 1
                if length > 4:
                    if col2 >= col1:
                        c_max = col1 + 3
                    else:
                        c_min = col1 - 3
                for c in range(c_min, c_max + 1):
                    current_cells.append((row1, c))
            else:
                col2 = col1
                r_min, r_max = min(row1, row2), max(row1, row2)
                length = r_max - r_min + 1
                if length > 4:
                    if row2 >= row1:
                        r_max = row1 + 3
                    else:
                        r_min = row1 - 3
                for r in range(r_min, r_max + 1):
                    current_cells.append((r, col1))

    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        if is_dragging:
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
                    print('Нет доступных кораблей такого размера.')
            else:
                print('Нельзя поставить корабль!!!')

            is_dragging = False
            start_cell = None
            current_cells = []
    return is_dragging, start_cell, current_cells, player_turn, game_phase, show_enemy_ships
