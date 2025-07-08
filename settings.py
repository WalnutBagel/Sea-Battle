# settings.py
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 800
BG_COLOR = (30, 30, 30) # Темно-серый фон
def get_default_ships():
    return {
        4: 1,  # один 4-палубный корабль
        3: 2,  # два 3-палубных
        2: 3,  # три 2-палубных
        1: 4   # четыре однопалубных
    }