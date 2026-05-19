import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, get_default_ships
from menu import draw_menu
from game import init_player_grid, generate_computer_ships, computer_turn, process_shot, is_game_over, shot_animations
from events import process_menu_events, process_game_events
from render import render_game, draw_exit_confirm

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Морской бой!!!')
    clock = pygame.time.Clock()

    # звуки
    pygame.mixer.music.load('assets/sounds/fon.mp3')
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)

    # задержка
    computer_turn_delay = 800
    computer_turn_timer = 0
    computer_move_ready = False

    # координаты сеток
    left_grid_x, left_grid_y = 100, 200  # Левый игрок
    right_grid_x, right_grid_y = 600, 200
    grid_size = 10
    cell_size = 40
    SHIPS_TO_PLACE = get_default_ships()

    player_grid = init_player_grid(grid_size)
    computer_grid = generate_computer_ships(grid_size)

    in_menu = True
    game_phase = "placing"  # Возможные значения: "placing" (расстановка), "battle" (бой)
    running = True
    player_turn = True
    show_enemy_ships = False

    # Флаг: показывать ли окно подтверждения выхода
    show_exit_confirm = False

    is_dragging = False
    start_cell = None
    current_cells = []
    while running:
        current_time = pygame.time.get_ticks()
        mouse_x, mouse_y = pygame.mouse.get_pos()  # Обновляем позицию мыши
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if in_menu:
                in_menu = process_menu_events(
                    event,
                    mouse_x,
                    mouse_y,
                    in_menu,
                )
            else:
                if not show_exit_confirm:
                    is_dragging, start_cell, current_cells, player_turn, game_phase, show_enemy_ships = process_game_events(
                    event, mouse_x, mouse_y, left_grid_x, left_grid_y, right_grid_x,
                    right_grid_y, grid_size, cell_size, player_grid, computer_grid,
                    current_cells, is_dragging, start_cell, SHIPS_TO_PLACE, player_turn, game_phase, show_enemy_ships)
                if not player_turn:
                    computer_turn_timer = current_time + computer_turn_delay
                    computer_move_ready = False
                # === Обработка выхода в меню (ESC или кнопка ☰) ===
                if not show_exit_confirm and game_phase == "battle":
                    if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or \
                       (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 
                        pygame.Rect(SCREEN_WIDTH - 70, 10, 60, 40).collidepoint(mouse_x, mouse_y)):
                        show_exit_confirm = True
                
                # === Обработка кликов по окну подтверждения (только логика, без отрисовки!) ===
                if show_exit_confirm:
                    # Получаем координаты кнопок из draw_exit_confirm (без отрисовки)
                    yes_rect = pygame.Rect(SCREEN_WIDTH//2 - 175, SCREEN_HEIGHT//2 + 20, 120, 50)
                    no_rect = pygame.Rect(SCREEN_WIDTH//2 + 55, SCREEN_HEIGHT//2 + 20, 120, 50)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if yes_rect.collidepoint(mouse_x, mouse_y):
                            in_menu = True
                            show_exit_confirm = False
                            player_grid = init_player_grid(grid_size)
                            computer_grid = generate_computer_ships(grid_size)
                            SHIPS_TO_PLACE = get_default_ships()
                            game_phase = "placing"
                            player_turn = True
                            is_dragging = False
                            start_cell = None
                            current_cells = []
                        elif no_rect.collidepoint(mouse_x, mouse_y):
                            show_exit_confirm = False

        # ход компьютера
        if not in_menu and game_phase == "battle" and not player_turn:
            if current_time >= computer_turn_timer:
                computer_cell = computer_turn(player_grid)
                if computer_cell:
                    hit = process_shot(
                        player_grid,
                        computer_cell,
                        left_grid_x,  # координаты сетки игрока
                        left_grid_y,
                        cell_size
                    )
                    player_turn = not hit
                computer_turn_timer = computer_turn_delay + current_time
        # отрисовываем экран
        screen.fill(BG_COLOR)# заливка фона
        if in_menu:
            draw_menu(screen)
        else:
            render_game(screen, left_grid_x, left_grid_y, right_grid_x,
                        right_grid_y, grid_size, cell_size, player_grid, computer_grid, 
                        current_cells, SHIPS_TO_PLACE, shot_animations, game_phase, show_enemy_ships)
            shot_animations[:] = [a for a in shot_animations if a.active]
            
            if show_exit_confirm:
                draw_exit_confirm(screen, "Выйти в меню?\nИгра завершится.")
            # === Проверка окончания игры ===
            if game_phase == "battle":
                if is_game_over(computer_grid) or is_game_over(player_grid):
                    # Игра закончилась — сразу в главное меню
                    in_menu = True
                    # Сброс игры для следующего запуска
                    player_grid = init_player_grid(grid_size)
                    computer_grid = generate_computer_ships(grid_size)
                    SHIPS_TO_PLACE = get_default_ships()
                    game_phase = "placing"
                    player_turn = True
                    is_dragging = False
                    start_cell = None
                    current_cells = []
            # Показываем "Ваш ход" только в бою и когда не показываем подтверждение выхода
            if game_phase == "battle" and not show_exit_confirm:
                font = pygame.font.Font(None, 36)
                turn_text = 'Ваш ход.' if player_turn else 'Ход компьютера.'
                turn_label = font.render(turn_text, True, (255, 255, 255))
                screen.blit(turn_label, (SCREEN_WIDTH//2 - turn_label.get_width()//2, 50))


        pygame.display.flip() # Обновление экрана
        clock.tick(60) # Ограничение FPS

    pygame.quit()

if __name__ == "__main__":
    main()