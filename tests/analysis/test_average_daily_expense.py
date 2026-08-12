
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.analysis.financial import get_average_daily_expense


print()
print("========== AVERAGE DAILY EXPENSE TEST ==========")

result = get_average_daily_expense()

print()
print(f"Average daily expense: {result:.2f}")

print()
print("========================================")

if isinstance(result, (int, float)):
    print("AVERAGE DAILY EXPENSE TEST PASSED")
else:
    print("AVERAGE DAILY EXPENSE TEST FAILED")

    