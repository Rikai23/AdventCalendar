import sqlite3

from ui.login import LoginWindow
from config import DB_NAME
import customtkinter as ctk


def init_db():
    """Инициализация БД приложения
    - Подключается к SQLite БД
    - Создается БД, если его не существует
    - Создются необходимые таблицы
    - Подготовка структуры хранения данных для приложения

    Исп. при каждом запуске приложения как этап инициализации системы"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    #------------USERS-------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE,
        password TEXT,
        greeting TEXT,
        total_days INTEGER,
        current_days INTEGER,
        last_open_time TEXT
    )
    """)

    # ------------GIFTS-------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_login TEXT,
        day_number INTEGER,
        
        password_hint TEXT,
        day_password TEXT,
        
        gift_description TEXT,
        gift_image BLOB 
    )
    """)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    """Точка входа в приложение
    
    - Инициализация БД
    - Создание главного окна Tkinter
    - Запуск окна логина
    - Запуск главного цикла GUI-приложения"""
    init_db()
    root = ctk.CTk()
    LoginWindow(root)
    root.mainloop()