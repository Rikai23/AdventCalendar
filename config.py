DB_NAME = 'advent_calendar.db'

#Администратор
ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = 'admin123'

#Тайминги
DAY_INTERVAL_HOURS = 24

#Название приложения
APP_TITLE = 'Адвент календарь'

#Тема окна
UI_APPEARANCE_MODE = 'dark'

#Цветовая тема кнопок
UI_COLOR_THEME = 'blue'

def window_centre_screen(root, width=300, height=250):
    """Расположение окна tkinter по центру экрана"""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    root.geometry("%dx%d+%d+%d" % (width, height, x, y))