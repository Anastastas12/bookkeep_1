"""
Описан класс, представляющий расходную операцию
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Expense:
    """
    Расходная операция.
    amount - сумма
    category - id категории расходов
    expense_date - дата расхода
    added_date - дата добавления в бд
    comment - комментарий
    pk - id записи в базе данных
    """

    def __init__(self, pk: int = 0, amount: float = 0.0, category: str = '', expense_date: str = ''):

        self.pk = pk
        self.amount = amount
        self.category = category
        self.expense_date = expense_date
