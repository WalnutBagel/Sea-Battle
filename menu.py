import pygame


def draw_menu(screen, show_random_button=True):
    font = pygame.font.Font(None, 74)
    title = font.render("МОРСКОЙ БОЙ", True, (255, 255, 255))

    # Координаты кнопок
    buttons = {
        'start': pygame.Rect(200, 300, 500, 50),
        'quit': pygame.Rect(200, 400, 500, 50)
    }

    mouse_pos = pygame.mouse.get_pos()

    # Цвета кнопок
    colors = {
        'start': (255, 255, 255) if buttons['start'].collidepoint(mouse_pos) else (200, 200, 200),
        'quit': (255, 255, 255) if buttons['quit'].collidepoint(mouse_pos) else (200, 200, 200)
    }

    # Отрисовка
    screen.blit(title, (200, 100))
    screen.blit(font.render('Начать игру', True, colors['start']), (200, 300))
    screen.blit(font.render('Выйти', True, colors['quit']), (200, 440))


