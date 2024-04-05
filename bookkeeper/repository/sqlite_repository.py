import sqlite3
from typing import Any, TypeVar
from datetime import datetime, timedelta
from bookkeeper.repository.abstract_repository import AbstractRepository, Model
from bookkeeper.models import Budget, Category, Expense

T = TypeVar('T', bound=Model)

class SqliteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий с базой данных SQLite.
    """
    def __init__(self, db_name: str) -> None:
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_expenses_table()  # Добавляем вызов метода для создания таблицы

    def create_expenses_table(self) -> None:
        """
        Создание таблицы expenses.
        """
        query = """
        CREATE TABLE IF NOT EXISTS expenses (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            expense_date TEXT
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def add(self, obj: T) -> int:
        if isinstance(obj, Budget):
            query = "INSERT INTO budgets (amount, start_date, end_date) VALUES (?, ?, ?)"
            self.cursor.execute(query, (obj.amount, obj.start_date, obj.end_date))
        elif isinstance(obj, Category):
            query = "INSERT INTO categories (name, parent, pk) VALUES (?, ?, ?)"
            self.cursor.execute(query, (obj.name, obj.parent, obj.pk))
        elif isinstance(obj, Expense):
            query = "INSERT INTO expenses (amount, category, expense_date) VALUES (?, ?, ?)"
            self.cursor.execute(query, (obj.amount, obj.category, obj.expense_date))
        self.conn.commit()
        return obj.pk

    def get(self, pk: int) -> T | None:
        if isinstance(self.model_type, Budget):
            table_name = "budgets"
        elif isinstance(self.model_type, Category):
            table_name = "categories"
        elif isinstance(self.model_type, Expense):
            table_name = "expenses"
        else:
            raise ValueError("Unsupported model type")

        query = f"SELECT * FROM {table_name} WHERE pk = ?"
        self.cursor.execute(query, (pk,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        # Возвращаем объект модели с данными из строки
        return self.model_type(*row)

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        if isinstance(T, Budget):
            table_name = "budgets"
        elif isinstance(T, Category):
            table_name = "categories"
        elif isinstance(T, Expense):
            table_name = "expenses"
        else:
            raise ValueError("Unsupported model type")

        if where is None:
            query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
        else:
            condition = " AND ".join([f"{key} = ?" for key in where.keys()])
            query = f"SELECT * FROM {table_name} WHERE {condition}"
            self.cursor.execute(query, tuple(where.values()))

        rows = self.cursor.fetchall()
        # Convert each row to the appropriate model type and return as a list
        return [T(*row) for row in rows]

    def update(self, obj: T) -> None:
        if isinstance(T, Budget):
            table_name = "budgets"
        elif isinstance(T, Category):
            table_name = "categories"
        elif isinstance(T, Expense):
            table_name = "expenses"
        else:
            raise ValueError("Unsupported model type")

        if not hasattr(obj, "pk") or obj.pk == 0:
            raise ValueError("Object must have a valid primary key")

        fields = ", ".join([f"{key} = ?" for key in obj.__dict__.keys() if key != "pk"])
        query = f"UPDATE {table_name} SET {fields} WHERE pk = ?"
        values = tuple(obj.__dict__.values()) + (obj.pk,)
        self.cursor.execute(query, values)
        self.conn.commit()

    def delete(self, pk: int) -> None:
        if isinstance(T, Budget):
            table_name = "budgets"
        elif isinstance(T, Category):
            table_name = "categories"
        elif isinstance(T, Expense):
            table_name = "expenses"
        else:
            raise ValueError("Unsupported model type")

        query = f"DELETE FROM {table_name} WHERE pk = ?"
        self.cursor.execute(query, (pk,))
        self.conn.commit()

    def get_expenses_by_day(self, date: datetime) -> list[Expense]:
        """
        Получить все расходы за указанный день.

        Parameters
        ----------
        date : datetime
            Дата, за которую нужно получить расходы.

        Returns
        -------
        list[Expense]
            Список расходов за указанный день.
        """
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        query = "SELECT amount, category, date FROM expenses WHERE date BETWEEN ? AND ?"
        self.cursor.execute(query, (start_of_day, end_of_day))
        rows = self.cursor.fetchall()
        return [Expense(*row) for row in rows] # [row[1:] for row in rows]  #

    def get_expenses_by_month(self, year: int, month: int) -> list[Expense]:
        """
        Получить все расходы за указанный месяц и год.

        Parameters
        ----------
        year : int
            Год.
        month : int
            Месяц.

        Returns
        -------
        list[Expense]
            Список расходов за указанный месяц и год.
        """
    
        start_of_month = datetime(year, month, 1)
        end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1))
        query = "SELECT * FROM expenses WHERE date BETWEEN ? AND ?"
        self.cursor.execute(query, (start_of_month, end_of_month))
        rows = self.cursor.fetchall()
        return [Expense(*row) for row in rows]

    def get_expenses_by_week(self) -> list[Expense]:
        """
        Получить все расходы за текущую неделю.

        Returns
        -------
        list[Expense]
            Список расходов за текущую неделю.
        """
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        query = "SELECT * FROM expenses WHERE date BETWEEN ? AND ?"
        self.cursor.execute(query, (start_of_week, end_of_week))
        rows = self.cursor.fetchall()
        # Преобразование строковых значений amount в числа типа float
        expenses = [Expense(row[0], row[1], float(row[2]), row[3]) for row in rows]
        return expenses


