from dataclasses import dataclass, field
import json
from pathlib import Path

from expenses import Expense, Expenses


@dataclass
class Person:
    name: str = "Person"
    incomes: dict[str, float] = field(default_factory=dict)
    expenses: Expenses = field(default_factory=Expenses)

    def add_income(self, title: str, amount: float) -> None:
        self.incomes[title] = self.incomes.get(title, 0) + amount

    def add_expense(self, expense: Expense) -> None:
        self.expenses.append(expense)

    def total_income(self) -> float:
        return sum(self.incomes.values())

    def total_expenses(self) -> float:
        return sum(expense.amount for expense in self.expenses)

    def to_flows(self) -> list[tuple[str, str, float]]:
        flows: list[tuple[str, str, float]] = []

        income_remaining: list[list[float | str]] = [
            [f"{self.name} {income_title}", float(income_amount)]
            for income_title, income_amount in self.incomes.items()
        ]

        for expense in sorted(self.expenses, key=lambda item: item.priority):
            expense_node = f"{self.name} {expense.title}"
            remaining_expense = float(expense.amount)

            for income_item in income_remaining:
                income_node = str(income_item[0])
                available_income = float(income_item[1])
                if remaining_expense <= 0:
                    break

                portion = min(available_income, remaining_expense)
                if portion <= 0:
                    continue

                flows.append((income_node, expense_node, portion))
                income_item[1] = available_income - portion
                remaining_expense -= portion

            if remaining_expense > 0 and income_remaining:
                fallback_income_node = str(income_remaining[0][0])
                flows.append((fallback_income_node, expense_node, remaining_expense))

        return flows


def load_persons_from_file(file_path: str = "persons.json") -> list[Person]:
    content = json.loads(Path(file_path).read_text(encoding="utf-8"))

    persons: list[Person] = []
    for person_item in content.get("persons", []):
        person = Person(name=person_item.get("name", "Person"))

        incomes = person_item.get("incomes", {})
        for title, amount in incomes.items():
            person.add_income(title, float(amount))

        expenses = person_item.get("expenses", [])
        for expense_item in expenses:
            person.add_expense(
                Expense(
                    title=expense_item.get("title", "Expense"),
                    description=expense_item.get("description", ""),
                    amount=float(expense_item.get("amount", 0)),
                    priority=int(expense_item.get("priority", 999)),
                    category=expense_item.get("category", "living"),
                )
            )

        persons.append(person)

    return persons
