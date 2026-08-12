import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.analysis.financial import (
    get_expense_category_percentages,
)


print()
print("========== EXPENSE CATEGORY PERCENTAGES TEST ==========")

result = get_expense_category_percentages()

print()
print("Category percentages:")

for category, percentage in result.items():
    print(f"{category}: {percentage:.2f}%")

print()
print("========================================")

if isinstance(result, dict):
    print("EXPENSE CATEGORY PERCENTAGES TEST PASSED")
else:
    print("EXPENSE CATEGORY PERCENTAGES TEST FAILED")
    