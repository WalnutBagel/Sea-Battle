import pygame
from game import draw_grid, draw_ships, can_place_ship, count_remaining_ships
from settings import *



def draw_ships_list(screen, ships_dict, position, show_zero=True):
    """
    ships_dict: словарь {размер: количество}
    show_zero: показывать ли корабли с количеством 0
    """
    font = pygame.font.Font(None, 30)
    x, y = position
    line_height = 30
    # Получаем все размеры кораблей и сортируем от большего к меньшему
    # sorted() возвращает новый список, reverse=True — по убыванию
    ship_sizes = sorted(ships_dict.keys(), reverse=True)
    
    for ship_size in ship_sizes:
        count = ships_dict.get(ship_size, 0)  # Если ключа нет - берём 0
        
        # Если кораблей 0 и show_zero=False - пропускаем эту строку
        if count == 0 and not show_zero:
            continue
            
        text = f"{ship_size}-палубный: {count}"
        
        # Красим в красный, если кораблей не осталось
        color = (255, 100, 100) if count == 0 else (255, 255, 255)
        
        label = font.render(text, True, color)
        screen.blit(label, (x, y))
        y += line_height

def draw_game_over(screen, player_wins):
    font = pygame.font.Font(None, 74)
    text = "Вы победили!" if player_wins else "Компьютер победил!"
    color = (0, 255, 0) if player_wins else (255, 0, 0)
    label = font.render(text, True, color)
    screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, SCREEN_HEIGHT // 2 - label.get_height() // 2))

def draw_exit_confirm(screen, message="Выйти в главное меню?"):
    """Рисует полупрозрачное окно подтверждения"""
    # Полупрозрачный фон
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Окно
    box_w, box_h = 400, 200
    box_x = SCREEN_WIDTH // 2 - box_w // 2
    box_y = SCREEN_HEIGHT // 2 - box_h // 2
    pygame.draw.rect(screen, (50, 50, 70), (box_x, box_y, box_w, box_h), border_radius=15)
    pygame.draw.rect(screen, (150, 150, 200), (box_x, box_y, box_w, box_h), 3, border_radius=15)
    
    font_large = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
    
    # Текст вопроса
    text = font_large.render(message, True, (255, 255, 255))
    screen.blit(text, (box_x + box_w//2 - text.get_width()//2, box_y + 40))
    
    # Кнопки
    mouse = pygame.mouse.get_pos()
    
    # Кнопка "Да"
    yes_rect = pygame.Rect(box_x + 50, box_y + 120, 120, 50)
    yes_color = (255, 100, 100) if yes_rect.collidepoint(mouse) else (200, 50, 50)
    pygame.draw.rect(screen, yes_color, yes_rect, border_radius=10)
    yes_text = font_small.render("Да", True, (255, 255, 255))
    screen.blit(yes_text, (yes_rect.x + 45, yes_rect.y + 12))
    
    # Кнопка "Нет"
    no_rect = pygame.Rect(box_x + 230, box_y + 120, 120, 50)
    no_color = (100, 255, 100) if no_rect.collidepoint(mouse) else (50, 200, 50)
    pygame.draw.rect(screen, no_color, no_rect, border_radius=10)
    no_text = font_small.render("Нет", True, (255, 255, 255))
    screen.blit(no_text, (no_rect.x + 40, no_rect.y + 12))
    
    return yes_rect, no_rect


def render_game(screen, left_grid_x, left_grid_y, right_grid_x, right_grid_y,grid_size,
                cell_size, player_grid, computer_grid, current_cells, ships_to_place, animations, game_phase):
    # здесь позже будет игровая логикa
    # Рисуем сетки
    draw_grid(screen, left_grid_x, left_grid_y, grid_size=10, player="Игрок")
    draw_grid(screen, right_grid_x, right_grid_y, grid_size=10, player="Компьютер")
    draw_ships(screen, player_grid, left_grid_x, left_grid_y, grid_size, cell_size)
    draw_ships(screen, computer_grid, right_grid_x, right_grid_y, grid_size, cell_size)
    # --- Выбор данных для списка кораблей ---
    if game_phase == "placing":
        # Фаза расстановки: показываем, что осталось поставить игроку
        ships_info = ships_to_place
        list_title = "Осталось поставить:"
        list_pos = (left_grid_x, left_grid_y + grid_size * cell_size + 20)
    else:
        # Фаза боя: показываем, сколько кораблей осталось у противника
        ships_info = count_remaining_ships(computer_grid)
        list_title = "Корабли противника:"
        list_pos = (right_grid_x, right_grid_y + grid_size * cell_size + 20)  # Справа, под сеткой компьютера
    
    # Рисуем заголовок списка
    font = pygame.font.Font(None, 30)
    title_label = font.render(list_title, True, (255, 255, 0))  # Жёлтый заголовок
    screen.blit(title_label, list_pos)
    
    # Рисуем сам список (сдвиг на 30 пикселей вниз от заголовка)
    draw_ships_list(screen, ships_info, (list_pos[0], list_pos[1] + 30), show_zero=True)

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

    # Кнопка "Меню" в правом верхнем углу
    menu_btn = pygame.Rect(SCREEN_WIDTH - 70, 10, 60, 40)
    mouse_pos = pygame.mouse.get_pos()
    btn_color = (255, 100, 100) if menu_btn.collidepoint(mouse_pos) else (200, 50, 50)
    pygame.draw.rect(screen, btn_color, menu_btn, border_radius=8)
    font = pygame.font.Font(None, 36)
    btn_text = font.render("☰", True, (255, 255, 255))
    screen.blit(btn_text, (menu_btn.x + 18, menu_btn.y + 5))

    for anim in animations:
        anim.draw(screen)
        anim.update()