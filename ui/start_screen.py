import customtkinter as ctk
from ui.calendar_view import CalendarView
from config import DB_NAME
import sqlite3
import config


class StartScreen:
    """Экран приветствия пользователя перед запуском адвент-календаря

    - Отображает персональное приветствие пользователя
    - Загружает текст приветствия из БД
    """

    def __init__(self, root, user_login):
        """Инициализация стартового экрана"""
        self.root = root
        self.user_login = user_login

        self.root.title("Адвент Календарь")
        config.window_centre_screen(root, 650, 550)
        self.root.resizable(False, False)

        self.greeting = self.load_greeting()

        self.label = ctk.CTkLabel(
            self.root,
            text=self.greeting,
            wraplength=600,
            justify="center",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label.pack(pady=(100, 50))

        self.start_button = ctk.CTkButton(
            self.root,
            text="ПРОДОЛЖИТЬ",
            command=self.start_calendar
        )
        self.start_button.pack(pady=20)

    def load_greeting(self):
        """Загрузка приветствия пользователя из БД"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT greeting FROM users WHERE login=?", (self.user_login,))
        data = cursor.fetchone()
        conn.close()
        return data[0] if data and data[0] else "Добро пожаловать!"

    def start_calendar(self):
        """Запуск основного экрана адвент-календаря"""
        for widget in self.root.winfo_children():
            widget.destroy()

        CalendarView(self.root, self.user_login)



