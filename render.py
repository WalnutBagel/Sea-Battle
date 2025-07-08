import pygame
from game import draw_grid, draw_ships, can_place_ship




def draw_ships_list(screen, ships_to_place, position):
    """
    Отрисовывает список оставшихся кораблей.
    position — координаты (x, y) для верхней левой части списка.
    """
    font = pygame.font.Font(None, 30)
    x, y = position
    line_height = 30
    for ship_size in sorted(ships_to_place.keys(), reverse=True):
        count = ships_to_place[ship_size]
        text = f"{ship_size}-палубный: {count}"
        label = font.render(text, True, (255, 255, 255))
        screen.blit(label, (x, y))
        y += line_height


def render_game(screen, left_grid_x, left_grid_y, right_grid_x, right_grid_y, grid_size, cell_size, player_grid, computer_grid,
                current_cells, ships_to_place):
    draw_grid(screen, left_grid_x, left_grid_y, grid_size, cell_size, player="Игрок")
    draw_grid(screen, right_grid_x, right_grid_y, grid_size, cell_size, player="Компьютер")
    draw_ships(screen, player_grid, left_grid_x, left_grid_y, grid_size, cell_size)
    draw_ships(screen, computer_grid, right_grid_x, right_grid_y, grid_size, cell_size)
    draw_ships_list(screen, ships_to_place, (left_grid_x, left_grid_y + grid_size * cell_size + 20))

    # Определяем цвет подсветки
    intersect = any(player_grid[r][c] == 1 for (r, c) in current_cells)

    if intersect or (current_cells and not can_place_ship(player_grid, current_cells)):
        highlight_color = (255, 0, 0)
    else:
        highlight_color = (255, 255, 0)

    for (r, c) in current_cells:
        rect_x = left_grid_x + c * cell_size
        rect_y = left_grid_y + r * cell_size
        rect = pygame.Rect(rect_x, rect_y, cell_size, cell_size)
        pygame.draw.rect(screen, highlight_color, rect, 2)