import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime

DB_NAME = 'parking_lot.db'

# Создание базы данных
def create_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            car_brand TEXT NOT NULL,
            license_plate TEXT NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            daily_rate REAL,
            monthly_rate REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Опционально: добавим тестового оператора, если таблица пустая
    cursor.execute('SELECT COUNT(*) FROM operators')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO operators (username, password) VALUES (?, ?)', ('admin', 'admin'))
    conn.commit()
    conn.close()

# Добавление клиента в базу данных
def add_client(name, phone, car_brand, license_plate, entry_time, exit_time, daily_rate, monthly_rate):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Приведём ставки к числам, если возможно
    try:
        daily_rate_val = float(daily_rate) if daily_rate not in (None, '') else None
    except ValueError:
        daily_rate_val = None
    try:
        monthly_rate_val = float(monthly_rate) if monthly_rate not in (None, '') else None
    except ValueError:
        monthly_rate_val = None

    cursor.execute('''
        INSERT INTO clients (name, phone, car_brand, license_plate, entry_time, exit_time, daily_rate, monthly_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, car_brand, license_plate, entry_time, exit_time, daily_rate_val, monthly_rate_val))
    conn.commit()
    conn.close()

# Получение всех клиентов
def get_clients():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    conn.close()
    return clients

# Удаление клиента по ID
def delete_client(client_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()

# Проверка учетных данных оператора
def check_credentials(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM operators WHERE username = ? AND password = ?', (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

# Получение информации о клиенте по гос номеру
def get_client_by_license_plate(license_plate):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT name, car_brand FROM clients WHERE license_plate = ?', (license_plate,))
    result = cursor.fetchone()
    conn.close()
    return result

# Основное окно приложения
def main():
    create_db()
    login_window()

def login_window():
    login = Toplevel()
    login.title("Вход оператора")
    login.resizable(False, False)

    Label(login, text="Имя пользователя").grid(row=0, column=0, padx=5, pady=5, sticky=E)
    Label(login, text="Пароль").grid(row=1, column=0, padx=5, pady=5, sticky=E)

    username_entry = Entry(login)
    password_entry = Entry(login, show='*')

    username_entry.grid(row=0, column=1, padx=5, pady=5)
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    def authenticate():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if check_credentials(username, password):
            login.destroy()
            login.master.destroy()  # Закрыть корневое пустое окно, если оно есть
            main_app(username)
        else:
            messagebox.showwarning("Ошибка", "Неверные учетные данные.")

    Button(login, text="Войти", command=authenticate).grid(row=2, column=1, padx=5, pady=10, sticky=E)

def main_app(operator):
    root = Tk()
    root.title(f"Авто стоянка - Оператор: {operator}")
    root.geometry("900x600")

    # Поля ввода
    Label(root, text="ФИО").grid(row=0, column=0, padx=5, pady=3, sticky=E)
    Label(root, text="Телефон").grid(row=1, column=0, padx=5, pady=3, sticky=E)
    Label(root, text="Марка авто").grid(row=2, column=0, padx=5, pady=3, sticky=E)
    Label(root, text="Гос номер").grid(row=3, column=0, padx=5, pady=3, sticky=E)
    Label(root, text="Время заезда").grid(row=4, column=0, padx=5, pady=3, sticky=E)
    Label(root, text="Время выезда").grid(row=5, column=0, padx=5, pady=3, sticky=E)
    Label(root, text="Оплата за сутки").grid(row=6, column=0, padx=5, pady=3, sticky=E)
    Label(root, text="Оплата за месяц").grid(row=7, column=0, padx=5, pady=3, sticky=E)

    name_entry = Entry(root)
    phone_entry = Entry(root)
    car_brand_entry = Entry(root)
    license_plate_entry = Entry(root)
    entry_time_entry = Entry(root)
    exit_time_entry = Entry(root)
    daily_rate_entry = Entry(root)
    monthly_rate_entry = Entry(root)

    name_entry.grid(row=0, column=1, padx=5, pady=3, sticky=W)
    phone_entry.grid(row=1, column=1, padx=5, pady=3, sticky=W)
    car_brand_entry.grid(row=2, column=1, padx=5, pady=3, sticky=W)
    license_plate_entry.grid(row=3, column=1, padx=5, pady=3, sticky=W)
    entry_time_entry.grid(row=4, column=1, padx=5, pady=3, sticky=W)
    exit_time_entry.grid(row=5, column=1, padx=5, pady=3, sticky=W)
    daily_rate_entry.grid(row=6, column=1, padx=5, pady=3, sticky=W)
    monthly_rate_entry.grid(row=7, column=1, padx=5, pady=3, sticky=W)

    # Календарь для выбора даты (раскомментируйте import и ниже строки, если установлен tkcalendar)
    def show_calendar():
        try:
            from tkcalendar import Calendar  # локальный импорт, чтобы не падало если нет пакета
        except ImportError:
            messagebox.showwarning("Ошибка", "tkcalendar не установлен. Установите через pip install tkcalendar")
            return

        calendar_window = Toplevel(root)
        calendar_window.title("Выбор даты")
        cal = Calendar(calendar_window, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        cal.pack(pady=20)

        def grab_date():
            selected_date = cal.get_date()
            monthly_rate_entry.delete(0, END)
            monthly_rate_entry.insert(0, selected_date)
            calendar_window.destroy()

        Button(calendar_window, text="Выбрать дату", command=grab_date).pack(pady=10)

    Button(root, text="Выбрать дату для оплаты за месяц", command=show_calendar).grid(row=8, column=1, padx=5, pady=5, sticky=W)

    # Автозаполнение полей при вводе гос номера
    def on_license_plate_change(*args):
        license_plate = license_plate_var.get().strip()
        if license_plate:
            client_info = get_client_by_license_plate(license_plate)
            if client_info:
                name_entry.delete(0, END)
                name_entry.insert(0, client_info[0])  # ФИО
                car_brand_entry.delete(0, END)
                car_brand_entry.insert(0, client_info[1])  # Марка авто

    # Привязка события к полю гос номера
    license_plate_var = StringVar()
    license_plate_var.trace_add("write", on_license_plate_change)
    license_plate_entry.config(textvariable=license_plate_var)

    # Кнопка добавления клиента
    def add_client_to_db():
        name = name_entry.get().strip()
        phone = phone_entry.get().strip()
        car_brand = car_brand_entry.get().strip()
        license_plate = license_plate_entry.get().strip()
        entry_time = entry_time_entry.get().strip()
        exit_time = exit_time_entry.get().strip()
        daily_rate = daily_rate_entry.get().strip()
        monthly_rate = monthly_rate_entry.get().strip()

        if name and phone and car_brand and license_plate and entry_time:
            add_client(name, phone, car_brand, license_plate, entry_time, exit_time, daily_rate, monthly_rate)
            messagebox.showinfo("Успех", "Клиент добавлен!")
            clear_entries()
            update_table()
        else:
            messagebox.showwarning("Ошибка", "Пожалуйста, заполните обязательные поля (ФИО, Телефон, Марка авто, Гос номер, Время заезда).")

    def clear_entries():
        name_entry.delete(0, END)
        phone_entry.delete(0, END)
        car_brand_entry.delete(0, END)
        license_plate_entry.delete(0, END)
        entry_time_entry.delete(0, END)
        exit_time_entry.delete(0, END)
        daily_rate_entry.delete(0, END)
        monthly_rate_entry.delete(0, END)

    Button(root, text="Добавить клиента", command=add_client_to_db).grid(row=9, column=1, padx=5, pady=8, sticky=W)

    # Таблица для отображения клиентов
    columns = ("ID", "ФИО", "Телефон", "Марка авто", "Гос номер", "Время заезда", "Время выезда", "Оплата за сутки", "Оплата за месяц")
    tree = ttk.Treeview(root, columns=columns, show='headings', height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor=W)
    tree.grid(row=10, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

    # Добавим скролл
    vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.grid(row=10, column=3, sticky='ns', padx=(0,10), pady=10)

    # Обновление таблицы
    def update_table():
        for row in tree.get_children():
            tree.delete(row)
        clients = get_clients()
        for client in clients:
            tree.insert("", "end", values=client)

    update_table()

    # Удаление клиента
    def delete_selected_client():
        selected_item = tree.selection()
        if selected_item:
            client_id = tree.item(selected_item[0])['values'][0]
            confirm = messagebox.askyesno("Подтвердите", "Удалить выбранного клиента?")
            if confirm:
                delete_client(client_id)
                update_table()
                messagebox.showinfo("Успех", "Клиент удален!")
        else:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите клиента для удаления.")

    Button(root, text="Удалить клиента", command=delete_selected_client).grid(row=11, column=1, padx=5, pady=5, sticky=W)

    # Разрешаем растягивание таблицы
    root.grid_rowconfigure(10, weight=1)
    root.grid_columnconfigure(2, weight=1)

    root.mainloop()

if __name__ == "__main__":
    # Создаем пустой корневой контейнер, чтобы Toplevel в login_window корректно работал
    base = Tk()
    base.withdraw()  # скрыть
    main()