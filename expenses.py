from dataclasses import dataclass


MIN_EXPENSE_PRIORITY = 1
MAX_EXPENSE_PRIORITY = 3
EXPENSE_CATEGORIES = (
    "retirement",
    "housing",
    "living",
    "savings",
)
DEFAULT_EXPENSE_CATEGORY = "living"


@dataclass
class Expense:
    title: str
    description: str
    amount: float
    priority: int
    category: str = DEFAULT_EXPENSE_CATEGORY

    def __post_init__(self) -> None:
        self.amount = float(self.amount)
        parsed_priority = int(self.priority)
        self.priority = max(MIN_EXPENSE_PRIORITY, min(parsed_priority, MAX_EXPENSE_PRIORITY))
        normalized_category = str(self.category).strip().lower()
        if normalized_category not in EXPENSE_CATEGORIES:
            normalized_category = DEFAULT_EXPENSE_CATEGORY
        self.category = normalized_category


class Expenses(list[Expense]):
    def by_category(self, category: str) -> Expense:
        normalized_category = str(category).strip().lower()
        for expense in self:
            if expense.category == normalized_category:
                return expense
        raise AttributeError(f"No expense found for category '{normalized_category}'")

    @property
    def retirement(self) -> Expense:
        return self.by_category("retirement")

    @property
    def housing(self) -> Expense:
        return self.by_category("housing")

    @property
    def living(self) -> Expense:
        return self.by_category("living")

    @property
    def savings(self) -> Expense:
        return self.by_category("savings")

    def __getattr__(self, name: str) -> Expense:
        if name in EXPENSE_CATEGORIES:
            return self.by_category(name)
        raise AttributeError(name)