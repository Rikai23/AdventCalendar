import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import config
import ui.login


class AdminPanel:
    """Админ-панель

    - Управление пользователями
    - Управление днями календаря
    - Добавление подарков
    - Редактирование дней
    - Загрузка данных из БД"""

    def __init__(self, root):
        """Инициализация окна админ-панели и элементов интерфейса

        - Создание всех UI-элементов интерфейса
        - разделы: управление пользователями и управление данными календаря
        - Первичная загрузка данных из БД"""

        self.root = root
        self.root.title(f'{config.APP_TITLE} - Админ-панель')
        config.window_centre_screen(root, 900, 900)
        self.root.resizable(False, False)

        self.selected_image_path = None

        #--------------ПОЛЬЗОВАТЕЛИ---------------
        self.section_users = ctk.CTkLabel(
            self.root,
            text='Управление пользователями',
            font = ctk.CTkFont(size=18, weight='bold')
        )
        self.section_users.pack(pady=(15, 10))

        self.login_entry = ctk.CTkEntry(master = self.root, placeholder_text='Логин')
        self.login_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(master=self.root, placeholder_text='Пароль', show='*')
        self.password_entry.pack(pady=5)

        self.total_days_entry = ctk.CTkEntry(master=self.root, placeholder_text='Количество дней календаря')
        self.total_days_entry.pack(pady=5)

        self.greeting_entry = ctk.CTkEntry(master=self.root, placeholder_text='Приветствие', width=300)
        self.greeting_entry.pack(pady=5)

        self.add_user_btn = ctk.CTkButton(master=self.root, text='Добавить пользователя', command=self.add_user)
        self.add_user_btn.pack(pady=5)

        self.delete_user_btn = ctk.CTkButton(master=self.root, text='Удалить пользователя', command=self.delete_user)
        self.delete_user_btn.pack(pady=5)

        self.user_list_label = ctk.CTkLabel(master=self.root, text='Список пользователей:')
        self.user_list_label.pack(pady=(10, 5))

        self.users_box = ctk.CTkTextbox(master = self.root, width = 550, height = 100)
        self.users_box.pack(pady=(0, 10))
        self.users_box.configure(state='disabled')

        # --------------ДНИ КАЛЕНДАРЯ---------------
        self.section_days = ctk.CTkLabel(
            self.root,
            text="Настройка дней календаря",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.section_days.pack(pady=(10, 10))

        self.day_selector = ctk.CTkOptionMenu(self.root, values=["Выберите день"])
        self.day_selector.pack(pady=5)

        self.password_hint_entry = ctk.CTkEntry(self.root, placeholder_text="Способ получения пароля")
        self.password_hint_entry.pack(pady=5)

        self.day_password_entry = ctk.CTkEntry(self.root, placeholder_text="Пароль дня")
        self.day_password_entry.pack(pady=5)

        self.gift_description_box = ctk.CTkTextbox(self.root, width=850, height=80)
        self.gift_description_box.pack(pady=5)
        self.gift_description_box.insert("0.0", "Описание подарка")

        self.image_label = ctk.CTkLabel(self.root, text="Картинка не выбрана")
        self.image_label.pack(pady=(5, 0))

        self.select_image_btn = ctk.CTkButton(self.root, text="Выбрать картинку", command=self.select_image)
        self.select_image_btn.pack(pady=5)

        self.save_day_btn = ctk.CTkButton(self.root, text="Сохранить данные дня", command=self.save_day_data)
        self.save_day_btn.pack(pady=(10, 20))

        # --------------ВЫЙТИ---------------
        self.logout_btn = ctk.CTkButton(
            self.root,
            text='Выйти',
            fg_color="red",
            hover_color='#aa0000',
            command=self.logout
        )
        self.logout_btn.pack(pady=(10, 20))

        # Первичная загрузка
        self.refresh_users()

    def add_user(self):
        """Добавление нового пользователя в БД
        - Создается запись в таблице users"""
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        greeting = self.greeting_entry.get().strip()
        total_days = self.total_days_entry.get().strip()

        if not login or not password or not total_days.isdigit():
            messagebox.showerror('Ошибка', 'Заполните все поля корректно')
        else:
            try:
                conn = sqlite3.connect(config.DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (login, password, greeting, total_days, current_days, last_open_time) VALUES (?, ?, ?, ?, ?, ?)',
                    (login, password, greeting, int(total_days), 0, None)
                )
                conn.commit()
                conn.close()
                messagebox.showinfo('Успешно', f'Пользователь {login} добавлен!')
                self.refresh_users()
                self.update_day_selector(int(total_days))

            except sqlite3.IntegrityError:
                messagebox.showerror('Ошибка', f'Пользователь {login} уже существует')


    def delete_user(self):
        """Удаление выбранного пользователя из БД"""
        login = self.login_entry.get().strip()
        if not login:
            messagebox.showerror('Ошибка', 'Введите логин для удаления!')
        else:
            conn = sqlite3.connect(config.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE login=?',(login,))
            cursor.execute('DELETE FROM gifts WHERE user_login=?', (login,))
            conn.commit()
            conn.close()
            messagebox.showinfo('Успешно', f'Пользователь {login} удален!')
            self.refresh_users()


    def refresh_users(self):
        """Обновление текстового поля со списком пользователей"""
        conn = sqlite3.connect(config.DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT login, total_days, current_days FROM users')
        users = cursor.fetchall()
        conn.close()

        #Разрешаем временное редактирование
        self.users_box.configure(state='normal')
        self.users_box.delete('0.0', 'end')

        if not users:
            self.users_box.insert('0.0', 'Нет пользователей')
        else:
            for user in users:
                self.users_box.insert('end', f'Логин {user[0]}, Дней {user[1]}, Текущий день: {user[2]}\n')

        #Запрещаем редактирование
        self.users_box.configure(state='disabled')


    def update_day_selector(self, total_days):
        """Обновление списка дней календаря"""
        values = [f"ДЕНЬ {i}" for i in range(1, total_days + 1)]
        self.day_selector.configure(values=values)
        if values:
            self.day_selector.set(values[0])

    def select_image(self):
        """Выбор изображения подарка"""
        path = filedialog.askopenfilename(
            title="Выбор изображения",
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if path:
            with open(path, "rb") as f:
                self.selected_image_bytes = f.read()
            self.image_label.configure(text=path.split("/")[-1])

    def save_day_data(self):
        """охранение данных дня календаря"""
        login = self.login_entry.get().strip()
        day_text = self.day_selector.get()

        if not login or "ДЕНЬ" not in day_text:
            messagebox.showerror("Ошибка", "Выберите пользователя и день")
            return

        day_number = int(day_text.split(" ")[1])

        password_hint = self.password_hint_entry.get().strip()
        day_password = self.day_password_entry.get().strip()
        gift_description = self.gift_description_box.get("0.0", "end").strip()
        image_path = self.selected_image_path

        conn = sqlite3.connect(config.DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM gifts WHERE user_login=? AND day_number=?",
            (login, day_number)
        )
        exists = cursor.fetchone()

        image_bytes = self.selected_image_bytes

        if exists and image_bytes is None:
            cursor.execute('SELECT gift_image FROM gifts WHERE user_login=? AND day_number=?', (login, day_number))
            image_bytes = cursor.fetchone()[0]

        if not exists and not image_bytes:
            messagebox.showerror('Ошибка', 'Выберите изображение для нового подарка')
            conn.close()
            return

        if exists:
            cursor.execute("""
                UPDATE gifts SET
                    password_hint=?,
                    day_password=?,
                    gift_description=?,
                    gift_image=?
                WHERE user_login=? AND day_number=?
            """, (password_hint, day_password, gift_description, image_bytes, login, day_number))
        else:
            cursor.execute("""
                INSERT INTO gifts (
                    user_login, day_number,
                    password_hint, day_password,
                    gift_description, gift_image
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (login, day_number, password_hint, day_password, gift_description, image_bytes))

        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", f"Данные для {day_text} сохранены")


    def logout(self):
        """ыход из админ-панели и возврат в окно логина"""
        for widget in self.root.winfo_children():
            widget.destroy()
        ui.login.LoginWindow(self.root)



