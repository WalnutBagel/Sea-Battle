import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, get_default_ships
from menu import draw_menu
from game import init_player_grid, generate_computer_ships, is_game_over, computer_turn, process_shot
from events import process_menu_events, process_game_events
from render import render_game


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Морской бой")
    clock = pygame.time.Clock()


    pygame.mixer.music.load('assets/sounds/background.mp3')
    pygame.mixer.music.set_volume(0.01)
    pygame.mixer.music.play(-1)

    computer_turn_delay = 1000  # Задержка в миллисекундах (2 секунда)
    computer_turn_timer = 0
    computer_move_ready = False  # Флаг, указывающий, что ход компьютера готов к выполнению

    left_grid_x, left_grid_y = 100, 200
    right_grid_x, right_grid_y = 600, 200
    grid_size = 10
    cell_size = 40

    SHIPS_TO_PLACE = get_default_ships()
    player_grid = init_player_grid(grid_size)
    computer_grid = generate_computer_ships(grid_size)

    in_menu = True
    running = True
    player_turn = True  # True - ход игрока, False - ход компьютера

    # Переменные для drag
    is_dragging = False
    start_cell = None
    current_cells = []

    while running:
        current_time = pygame.time.get_ticks()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if in_menu:
                in_menu = process_menu_events(event, mouse_x, mouse_y, in_menu)
            else:
                is_dragging, start_cell, current_cells, player_turn = process_game_events(
                    event, mouse_x, mouse_y,
                    left_grid_x, left_grid_y, right_grid_x, right_grid_y,
                    grid_size, cell_size, player_grid, computer_grid,
                    current_cells, is_dragging, start_cell, SHIPS_TO_PLACE,
                    player_turn
                )
                if not player_turn:
                    computer_turn_timer = current_time + computer_turn_delay
                    computer_move_ready = False

        # Ход компьютера
        if not in_menu and not player_turn and all(count == 0 for count in SHIPS_TO_PLACE.values()):
            if current_time >= computer_turn_timer:
                computer_cell = computer_turn(player_grid)
                if computer_cell:
                    hit = process_shot(player_grid, computer_cell)
                    player_turn = not hit  # Если компьютер попал, он ходит еще раз
                # Всегда обновляем таймер, даже если компьютер попал
                computer_turn_timer = current_time + computer_turn_delay

        screen.fill(BG_COLOR)
        if in_menu:
            draw_menu(screen)
        else:
            render_game(screen, left_grid_x, left_grid_y, right_grid_x, right_grid_y,
                        grid_size, cell_size, player_grid, computer_grid, current_cells, SHIPS_TO_PLACE)

            # Отображаем чей сейчас ход
            font = pygame.font.Font(None, 36)
            turn_text = "Ваш ход" if player_turn else "Ход компьютера"
            turn_label = font.render(turn_text, True, (255, 255, 255))
            screen.blit(turn_label, (SCREEN_WIDTH // 2 - turn_label.get_width() // 2, 50))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()