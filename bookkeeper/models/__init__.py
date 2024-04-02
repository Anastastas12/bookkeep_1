from dataclasses import dataclass

@dataclass
class Budget:
    amount: float
    start_date: str
    end_date: str
    pk: int = 0

@dataclass
class Category:
    name: str
    parent: int | None = None
    pk: int = 0

@dataclass
class Expense:
    amount: float
    category: int
    expense_date: str
    pk: int = 0