from tkinter import messagebox
import sqlite3

import customtkinter as ctk
import config
from ui.admin_panel import AdminPanel
from ui.calendar_view import CalendarView
from ui.start_screen import StartScreen

ctk.set_appearance_mode(config.UI_APPEARANCE_MODE)
ctk.set_default_color_theme(config.UI_COLOR_THEME)

class LoginWindow:
    """Окно входа в приложения

    - Отображение формы авторизации
    - Обработка ввода логина и пароля
    - Определение роди пользователя (админ/пользователь)
    - маршрутизация пользователя в соответствующий интерфейс"""

    def __init__(self, root):
        """Инициализация окна входа в приложение

        Здесь:
        - Принимается главное окно Tkinter (root)
        - Настраиваются параметры окна (заголовок, размер, поведение)
        - Создаются все элементы интерфейса (Label, Entry, Button)
        - Настраиваются обработчики событий (кнопки, ввод)
        - формируется UI-структура экрана логина"""
        self.root = root

        self.root.title(config.APP_TITLE)
        config.window_centre_screen(root, 350, 250)
        self.root.resizable(False, False)

        self.title_label = ctk.CTkLabel(
            master = self.root,
            text = 'Вход в адвент-календарь',
            font = ctk.CTkFont(size=20, weight='bold')
        )
        self.title_label.pack(pady=(20,20))

        self.login_entry = ctk.CTkEntry(
            master = self.root,
            placeholder_text = 'Логин',
            width = 250
        )
        self.login_entry.pack(pady=(10,10))

        self.password_entry = ctk.CTkEntry(
            master = self.root,
            placeholder_text = 'Пароль',
            show = '*',
            width = 200
        )
        self.password_entry.pack(pady=(10,20))

        self.login_button = ctk.CTkButton(
            master = self.root,
            text = 'Войти',
            width = 200,
            command = self.login
        )
        self.login_button.pack(pady=(10,10))

    def login(self):
        """Обаботка попытки входа

        - Получаем введенные данные логина и пароля
        - Проверяем кто заходит админ или пользователь
        - Если админ, то открытие админ панели
        - Если пользователь, то поиск его в БД и в случае успеха открытие Адвент календаря
        - Если пользователь не найдет, показываем соответствующее сообщение"""

        login = self.login_entry.get()
        password = self.password_entry.get()

        if login == config.ADMIN_LOGIN and password == config.ADMIN_PASSWORD:
            messagebox.showinfo('Вход', 'Вы пошли как администратор')
            self.root.destroy()

            #Временная заглушка админ-панели
            admin_root = ctk.CTk()
            AdminPanel(admin_root)
            admin_root.mainloop()
        else:
            conn = sqlite3.connect(config.DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE login=? AND password=?',
                (login, password)
            )
            user = cursor.fetchone()
            conn.close()

            if user:
                messagebox.showinfo('Вход', 'Вход выполнен как пользователь')
                self.root.destroy()

                user_root = ctk.CTk()
                StartScreen(user_root, login)

                user_root.mainloop()
            else:
                messagebox.showerror('Ошибка', 'Неверный логин или пароль')

