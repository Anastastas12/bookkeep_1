from dataclasses import dataclass

@dataclass
class Budget:
    amount: float
    start_date: str
    end_date: str
    pk: int = 0