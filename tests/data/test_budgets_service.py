from datetime import date
from services.data.budgets import (
    get_budgets,
    get_budget,
    add_budget,
    update_budget,
    delete_budget,
)


TEST_MONTH = date(2026, 8, 1)
TEST_CATEGORY = "ServiceTest"


print("\n========== BUDGET SERVICE TEST ==========")


# ============================================================
# ADD
# ============================================================

print("\n========== ADD TEST ==========")

# تنظيف أي اختبار سابق بنفس Month + Category
delete_budget(TEST_MONTH, TEST_CATEGORY)

add_budget(
    TEST_MONTH,
    TEST_CATEGORY,
    1000,
    "Service layer test",
)

budget = get_budget(TEST_MONTH, TEST_CATEGORY)

print(budget)

assert budget is not None, "ADD failed: budget was not found."

assert budget["Category"] == TEST_CATEGORY
assert float(budget["Limit"]) == 1000.00
assert budget["Notes"] == "Service layer test"

print("ADD: PASSED")


# ============================================================
# READ
# ============================================================

print("\n========== READ TEST ==========")

budgets = get_budgets()

assert budgets is not None, "READ failed: get_budgets() returned None."

print(f"Total budgets: {len(budgets)}")

found = any(
    budget["Month"] == TEST_MONTH
    and budget["Category"] == TEST_CATEGORY
    for budget in budgets
)

assert found, "READ failed: test budget was not found in all budgets."

print("READ: PASSED")


# ============================================================
# UPDATE
# ============================================================

print("\n========== UPDATE TEST ==========")

update_budget(
    TEST_MONTH,
    TEST_CATEGORY,
    1500.50,
    "Updated service test",
)

budget = get_budget(TEST_MONTH, TEST_CATEGORY)

print(budget)

assert budget is not None, "UPDATE failed: budget disappeared."

assert float(budget["Limit"]) == 1500.50
assert budget["Notes"] == "Updated service test"

print("UPDATE: PASSED")


# ============================================================
# DELETE
# ============================================================

print("\n========== DELETE TEST ==========")

delete_budget(TEST_MONTH, TEST_CATEGORY)

budget = get_budget(TEST_MONTH, TEST_CATEGORY)

print(budget)

assert budget is None, "DELETE failed: budget still exists."

print("DELETE: PASSED")


# ============================================================
# FINISHED
# ============================================================

print("\n========================================")
print("ALL BUDGET SERVICE TESTS PASSED")
print("========================================")