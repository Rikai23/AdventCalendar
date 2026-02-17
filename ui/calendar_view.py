from io import BytesIO

import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta
from PIL import Image

import config

class CalendarView:
    """Пользовательский интерфейс адвент-календаря

    - Управление логикой дней
    - Отображение текущего дня
    - Контроль таймера
    - Ввод пароля дня
    - Отображение подарка
    - Сохранение прогресса пользователя"""

    def __init__(self, root, user_login):
        """Инициализация пользовательского адвент-календаря

        - Загрузка данных пользователя из БД
        - Определение текущего дня
        - Восстановление таймера
        - Построение UI
        """
        self.root = root
        self.user_login = user_login

        self.root.title(f'{config.APP_TITLE} - {user_login} ')
        config.window_centre_screen(root, 1000, 850)
        self.root.resizable(False, False)

        self.selected_day_widgets = []

        self.load_user_data()

        # --------------UI---------------
        self.progress_frame = ctk.CTkFrame(self.root)
        self.progress_frame.pack(pady=20, fill="x", padx=20)

        self.day_label = ctk.CTkLabel(
            master = self.root,
            text = '',
            font = ctk.CTkFont(size=26, weight='bold')
        )
        self.day_label.pack(pady=(20, 10))

        self.hint_label = ctk.CTkLabel(
            self.root,
            text="",
            font=ctk.CTkFont(size=14),
            wraplength=700,
            justify="center"
        )
        self.hint_label.pack(pady=(5, 10))

        self.password_entry = ctk.CTkEntry(
            master=self.root,
            placeholder_text="Введите пароль дня",
            width=250
        )
        self.password_entry.pack(pady=10)

        self.action_button = ctk.CTkButton(
            master=self.root,
            text='Далее',
            command=self.check_password
        )
        self.action_button.pack(pady=10)

        self.timer_label = ctk.CTkLabel(
            master=self.root,
            text='',
            font=ctk.CTkFont(size=14)
        )
        self.timer_label.pack(pady=(10, 10))

        # --------------ПОДАРОК---------------
        self.gift_frame = ctk.CTkFrame(self.root)
        self.gift_frame.pack(pady=(20, 10), fill="both", expand=True)

        self.gift_text = ctk.CTkLabel(
            self.gift_frame,
            text="",
            wraplength=700,
            justify="center",
            font=ctk.CTkFont(size=15)
        )
        self.gift_text.pack(pady=10)

        self.gift_image_label = ctk.CTkLabel(self.gift_frame, text="")
        self.gift_image_label.pack(pady=10)

        self.receive_button = ctk.CTkButton(
            self.gift_frame,
            text="ПОЛУЧЕН",
            command=self.confirm_received
        )

        self.gift_frame.pack_forget()

        self.create_progress_days()

        self.update_day_state()


    def load_user_data(self):
        """Загрузка данных пользователя из БД

        Загружается:
        - Приветствие, общее кол-во дней
        - Текущий день
        - Время последнего открытия подарка"""
        conn = sqlite3.connect(config.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT greeting, total_days, current_days, last_open_time FROM users WHERE login=?',
            (self.user_login,)
        )
        data = cursor.fetchone()
        conn.close()

        self.greeting = data[0]
        self.total_days = data[1]
        self.current_days = data[2]
        self.last_open_time = data[3]


    def load_day_data(self):
        """Загрузка данных текущего дня из БД"""
        conn = sqlite3.connect(config.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT password_hint, day_password, gift_description, gift_image
            FROM gifts
            WHERE user_login=? AND day_number=?
            """, (self.user_login, self.current_days + 1))

        data = cursor.fetchone()
        conn.close()

        print(f'DEBUG = {type(data[3])}')

        return data

    def save_user_state(self):
        """Сохранение состояния пользователя в БД"""
        conn = sqlite3.connect(config.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET current_days=?, last_open_time=? WHERE login=?',
            (self.current_days, self.last_open_time, self.user_login)
        )
        conn.commit()
        conn.close()


    def update_day_state(self):
        """Логика управлением состояния календаря

        Определяется:
        - Завершен ли календарь
        - Доступен ли следующий день
        - Активен ли таймер ожидания
        - Доступен ли ввод пароля
        - Настроен ли день админом"""
        #Если календарь завершен
        if self.current_days >= self.total_days:
            self.day_label.configure(text='Календарь завершен🎉')
            self.hint_label.configure(text='Все подарки получены 🎁')
            self.action_button.configure(state='disabled')
            self.password_entry.configure(state="disabled")
            self.timer_label.configure(text='')
            return

        #Если есть таймер
        if self.last_open_time:
            last_time = datetime.fromisoformat(self.last_open_time)
            next_time = self.get_next_day_midnight(last_time)
            now = datetime.now()

            if now < next_time:
                #Таймер еще идет
                self.password_entry.pack_forget()
                self.action_button.pack_forget()
                self.gift_frame.pack_forget()
                self.day_label.configure(text=f'ДЕНЬ {self.current_days + 1}')
                self.hint_label.configure(text='Секундомер до следующего дня')
                self.show_timer(next_time)
                return

        day_data = self.load_day_data()
        if not day_data:
            self.hint_label.configure(text='Администратор еще не настроил этот день')
            self.action_button.configure(state='disabled')
            self.password_entry.configure(state="disabled")
            return

        self.password_hint, self.day_password, self.gift_description, self.gift_image_bytes = day_data

        self.day_label.configure(text=f'ДЕНЬ {self.current_days + 1}')
        self.hint_label.configure(text=self.password_hint)

        self.password_entry.pack(pady=10)
        self.password_entry.configure(state="normal")
        self.password_entry.delete(0, 'end')

        self.action_button.pack(pady=10)
        self.action_button.configure(state='normal')

        self.gift_frame.pack_forget()
        self.create_progress_days()

    def show_timer(self, target_time):
        """Отображение таймера до следующего дня

        Отсчитывает время до target_time в формате: ЧЧ:ММ:СС

        При завершении:
        - Сбрасывается last_open_time
        - Сохраняет состояние пользователя
        - Обновляет состояние календаря"""
        now = datetime.now()
        delta = target_time - now

        seconds = int(delta.total_seconds())

        if seconds <= 0:
            self.last_open_time = None
            self.save_user_state()
            self.update_day_state()
            return
        else:
            #Если календарь завершен
            if self.current_days >= self.total_days:
                self.day_label.configure(text='Календарь завершен🎉')
                self.hint_label.configure(text='Все подарки получены 🎁')
                self.action_button.configure(state='disabled')
                self.password_entry.configure(state="disabled")
                self.timer_label.configure(text='')
                return
            self.day_label.configure(text='')
            self.hint_label.configure(text='Секундомер до следующего дня')

        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60

        self.timer_label.configure(text=f"До следующего дня: {h:02}:{m:02}:{s:02}")
        self.root.after(1000, lambda: self.show_timer(target_time))

    def check_password(self):
        """Проверка пароля дня"""
        entered = self.password_entry.get().strip()
        if entered != self.day_password:
            messagebox.showerror("Ошибка", "Неверный пароль")
            return

        self.show_gift()

    def show_gift(self):
        """Отображение информации о подарке

        Выполняется:
        - Блокировка ввода пароля
        - Отображение списания подарка
        - Загрузку и отображения изображения
        - Отображение кнопки подтверждения получения"""
        self.password_entry.configure(state="disabled")
        self.action_button.configure(state="disabled")

        self.gift_text.configure(text=self.gift_description)

        if self.gift_image_bytes is not None:
            try:
                img = Image.open(BytesIO(self.gift_image_bytes))
                img = img.resize((300, 300))
                self.ctk_image = ctk.CTkImage(light_image=img, size=(300, 300))
                self.gift_image_label.configure(image=self.ctk_image, text="")
            except:
                self.gift_image_label.configure(text="Не удалось загрузить изображение")

        self.gift_frame.pack(pady=(10, 10))
        self.receive_button.pack(pady=10)

    def confirm_received(self):
        """Подтверждение получения подарка"""
        self.current_days += 1
        self.last_open_time = datetime.now().isoformat()
        self.save_user_state()

        self.password_entry.pack_forget()
        self.action_button.pack_forget()
        self.gift_frame.pack_forget()
        self.create_progress_days()
        next_midnight = self.get_next_day_midnight(datetime.now())
        self.show_timer(next_midnight)

    def create_progress_days(self):
        """Создание визуальной полосы прогоресса дней

        - прошедшие дни зеленые
        - текущий день оранжевый
        - будущие дни серые и заблокирвоанные"""
        for widget in self.progress_frame.winfo_children():
            widget.destroy()

        self.selected_day_widgets = []
        for i in range(1, self.total_days + 1):
            day_btn = ctk.CTkButton(
                self.progress_frame,
                text=str(i),
                width=40,
                height=40,
            )
            day_btn.pack(side="left", padx=5)

            if i < self.current_days + 1:
                day_btn.configure(fg_color="green")
            elif i == self.current_days + 1:
                day_btn.configure(fg_color="orange")
            else:
                day_btn.configure(fg_color="gray", state="disabled")

            self.selected_day_widgets.append(day_btn)

    def get_next_day_midnight(self, dt):
        """Возвращает datetime следующего дна в 00:00"""
        next_day = dt.date() + timedelta(days=1)
        return datetime.combine(next_day, datetime.min.time())


