import pygame
from game import draw_grid, draw_ships, can_place_ship
from settings import *



def draw_ships_list(screen, ships_to_place, position):
    font = pygame.font.Font(None, 30)  # Стандартный шрифт
    x, y = position
    line_height = 30
    for ship_size in ships_to_place.keys():
        count = ships_to_place[ship_size]
        text = f"{ship_size}-палубный: {count}"
        label = font.render(text, True, (255, 255, 255))
        screen.blit(label, (x, y))
        y += line_height

def draw_game_over(screen, player_wins):
    font = pygame.font.Font(None, 74)
    text = "Вы победили!" if player_wins else "Компьютер победил!"
    color = (0, 255, 0) if player_wins else (255, 0, 0)
    label = font.render(text, True, color)
    screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, SCREEN_HEIGHT // 2 - label.get_height() // 2))

def render_game(screen, left_grid_x, left_grid_y, right_grid_x, right_grid_y,grid_size,
                cell_size, player_grid, computer_grid, current_cells, ships_to_place, animations, game_phase):
    # здесь позже будет игровая логикa
    # Рисуем сетки
    draw_grid(screen, left_grid_x, left_grid_y, grid_size=10, player="Игрок")
    draw_grid(screen, right_grid_x, right_grid_y, grid_size=10, player="Компьютер")
    draw_ships(screen, player_grid, left_grid_x, left_grid_y, grid_size, cell_size)
    draw_ships(screen, computer_grid, right_grid_x, right_grid_y, grid_size, cell_size)
    draw_ships_list(screen, ships_to_place, (left_grid_x, left_grid_y + grid_size * cell_size + 20))

    intersect = any(player_grid[r][c] == 1 for (r, c) in current_cells)

    if intersect or (current_cells and not can_place_ship(player_grid, current_cells)):
        highlight_color = (255, 0, 0)
    else:
        highlight_color = (255, 255, 0)

    if game_phase == "placing" and not all(count == 0 for count in ships_to_place.values()):
        btn_rect = pygame.Rect(50, 50, 300, 40)
        mouse_pos = pygame.mouse.get_pos()

        # Подсветка при наведении
        if btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (150, 220, 150), btn_rect)
        else:
            pygame.draw.rect(screen, (100, 200, 100), btn_rect)

        font = pygame.font.Font(None, 36)
        text = font.render("Случайная расстановка", True, (255, 255, 255))
        screen.blit(text, (60, 55))

    # Кнопка "Начать бой" (только если все корабли расставлены)
    if game_phase == "placing" and all(count == 0 for count in ships_to_place.values()):
        btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 50, 300, 40)  # Центр экрана сверху
        mouse_pos = pygame.mouse.get_pos()

        # Подсветка при наведении
        if btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (150, 220, 150), btn_rect)
        else:
            pygame.draw.rect(screen, (100, 200, 100), btn_rect)

        font = pygame.font.Font(None, 36)
        text = font.render("Начать бой!", True, (255, 255, 255))
        screen.blit(text, (btn_rect.x + 10, btn_rect.y + 5))

    # подсвечиваем current_cells
    for (r, c) in current_cells:
        rect_x = left_grid_x + c * cell_size
        rect_y = left_grid_y + r * cell_size

        rect = pygame.Rect(rect_x, rect_y, cell_size, cell_size)
        pygame.draw.rect(screen, highlight_color, rect, 2)

    for anim in animations:
        anim.draw(screen)
        anim.update()