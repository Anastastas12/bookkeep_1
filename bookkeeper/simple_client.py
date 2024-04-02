from datetime import datetime
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.utils import read_tree

cat_repo = MemoryRepository[Category]()
exp_repo = MemoryRepository[Expense]()

cats = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()

Category.create_from_tree(read_tree(cats), cat_repo)

def print_expenses_by_day(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    expenses = exp_repo.get_expenses_by_day(date)
    print(*expenses, sep='\n')

def print_expenses_by_month(year_month_str):
    year, month = map(int, year_month_str.split('-'))
    expenses = exp_repo.get_expenses_by_month(year, month)
    print(*expenses, sep='\n')

def print_expenses_by_year(year_str):
    year = int(year_str)
    expenses = exp_repo.get_expenses_by_year(year)
    print(*expenses, sep='\n')

while True:
    try:
        cmd = input('$> ')
    except EOFError:
        break
    if not cmd:
        continue
    if cmd == 'категории':
        print(*cat_repo.get_all(), sep='\n')
    elif cmd == 'расходы':
        print(*exp_repo.get_all(), sep='\n')
    elif cmd[0].isdecimal():
        amount, name = cmd.split(maxsplit=1)
        try:
            cat = cat_repo.get_all({'name': name})[0]
        except IndexError:
            print(f'категория {name} не найдена')
            continue
        exp = Expense(int(amount), cat.pk)
        exp_repo.add(exp)
        print(exp)
    elif cmd.startswith('расходы_день'):
        _, date_str = cmd.split(maxsplit=1)
        print_expenses_by_day(date_str)
    elif cmd.startswith('расходы_месяц'):
        _, year_month_str = cmd.split(maxsplit=1)
        print_expenses_by_month(year_month_str)
    elif cmd.startswith('расходы_год'):
        _, year_str = cmd.split(maxsplit=1)
        print_expenses_by_year(year_str)
