import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.models import Expense

class PersonalFinanceApp:
    def __init__(self, root, repository):
        self.root = root
        self.root.title("Контроль личных финансов")

        self.repository = repository
        repository = SqliteRepository('personal_finance.db')

        # Создание базы данных SQLite
        self.conn = sqlite3.connect('personal_finance.db')
        self.cursor = self.conn.cursor()
        self.create_table()

        # Создание элементов интерфейса
        self.category_label = tk.Label(root, text="Категория:")
        self.category_combobox = ttk.Combobox(root, values=["Продукты", "Одежда", "Хозтовары", "Прочее"])
        self.amount_label = tk.Label(root, text="Сумма:")
        self.amount_entry = tk.Entry(root)
        self.add_button = tk.Button(root, text="Добавить", command=self.add_expense)

        # Создание таблицы для вывода данных из базы данных
        self.tree_frame = ttk.Frame(root)
        self.tree_frame.grid(row=3, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree = ttk.Treeview(self.tree_frame, columns=("Категория", "Сумма", "Дата"), yscrollcommand=self.tree_scrollbar.set)
        self.tree_scrollbar.config(command=self.tree.yview)

        self.tree_scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("#0", text="")
        self.tree.heading("#1", text="Категория")
        self.tree.heading("#2", text="Сумма")
        self.tree.heading("#3", text="Дата")

        # Задаем ширину столбцов
        self.tree.column("#0", width=0)  # Установка нулевой ширины столбца для номера
        self.tree.column("#1", width=150)
        self.tree.column("#2", width=100)
        self.tree.column("#3", width=150)

        # Создание кнопки удаления записи
        self.delete_button = tk.Button(root, text="Удалить", command=self.delete_expense)

        # Заполнение таблицы данными из базы данных
        self.show_expenses()

        # Размещение элементов интерфейса с помощью сетки
        self.category_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.category_combobox.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.amount_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.amount_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        self.add_button.grid(row=2, columnspan=2, sticky="ew", padx=10, pady=10)
        self.delete_button.grid(row=4, columnspan=2, sticky="ew", padx=10, pady=10)

        # Метки для отображения сумм расходов за день, неделю и месяц
        self.daily_expenses_label = tk.Label(root, text="Расходы за день:")
        self.daily_expenses_value = tk.Label(root, text="")
        self.weekly_expenses_label = tk.Label(root, text="Расходы за неделю:")
        self.weekly_expenses_value = tk.Label(root, text="")
        self.monthly_expenses_label = tk.Label(root, text="Расходы за месяц:")
        self.monthly_expenses_value = tk.Label(root, text="")

        # Размещение меток на интерфейсе
        self.daily_expenses_label.grid(row=5, column=0, sticky="e", padx=10, pady=10)
        self.daily_expenses_value.grid(row=5, column=1, sticky="w", padx=10, pady=10)
        self.weekly_expenses_label.grid(row=6, column=0, sticky="e", padx=10, pady=10)
        self.weekly_expenses_value.grid(row=6, column=1, sticky="w", padx=10, pady=10)
        self.monthly_expenses_label.grid(row=7, column=0, sticky="e", padx=10, pady=10)
        self.monthly_expenses_value.grid(row=7, column=1, sticky="w", padx=10, pady=10)

        # Настройка параметров расширения для объектов
        root.grid_rowconfigure(3, weight=1)  # Растягиваем таблицу при изменении размера окна по вертикали
        root.grid_columnconfigure(1, weight=1)  # Растягиваем таблицу при изменении размера окна по горизонтали

        # Вызов функций для отображения сумм расходов
        self.show_daily_expenses(repository)
        self.show_weekly_expenses(repository)
        self.show_monthly_expenses(repository)

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS expenses
                               (pk INTEGER PRIMARY KEY, category TEXT, amount REAL, date TEXT)''')
        self.conn.commit()

    def add_expense(self):
        category = self.category_combobox.get()
        amount = float(self.amount_entry.get())
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Формат даты соответствует заголовку "Дата" в Treeview
        self.cursor.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)", (category, amount, date))
        self.conn.commit()
        self.amount_entry.delete(0, tk.END)
        print("Расход успешно добавлен.")
        self.show_expenses()  # Перезагрузка данных в таблице после добавления

        # Обновление сумм расходов за день, неделю и месяц
        self.show_daily_expenses(self.repository)
        self.show_weekly_expenses(self.repository)
        self.show_monthly_expenses(self.repository)

    def delete_expense(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_id = self.tree.item(selected_item)["text"]  # Получаем id записи из первого столбца
            self.cursor.execute("DELETE FROM expenses WHERE pk = ?", (item_id,))
            self.conn.commit()
            self.show_expenses()  # Перезагрузка данных в таблице после удаления
            self.show_daily_expenses(self.repository)  # Обновление суммы расходов за день
            self.show_weekly_expenses(self.repository)  # Обновление суммы расходов за неделю
            self.show_monthly_expenses(self.repository)  # Обновление суммы расходов за месяц
        else:
            print("Выберите запись для удаления.")

    def show_expenses(self):
        # Очистка таблицы перед загрузкой новых данных
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Получение данных из базы данных и загрузка их в таблицу
        self.cursor.execute("SELECT * FROM expenses")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=(row[1], row[2], row[3]))

    def show_daily_expenses(self, repository):
        today = datetime.now().date()
        expenses = repository.get_expenses_by_day(today)
        daily_expenses = sum(exp.amount for exp in expenses)
        self.daily_expenses_value.config(text=str(daily_expenses))

    def show_weekly_expenses(self, repository):
        expenses = repository.get_expenses_by_week()
        weekly_expenses = sum(exp.amount for exp in expenses)  # Преобразование в числа
        self.weekly_expenses_value.config(text=str(weekly_expenses))

    def show_monthly_expenses(self, repository):
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        expenses = repository.get_expenses_by_month(start_of_month.year, start_of_month.month)
        monthly_expenses = sum(exp.amount for exp in expenses)
        self.monthly_expenses_value.config(text=str(monthly_expenses))

if __name__ == "__main__":
    root = tk.Tk()
    repository = SqliteRepository('personal_finance.db')
    app = PersonalFinanceApp(root, repository)
    root.mainloop()
