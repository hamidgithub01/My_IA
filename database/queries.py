from database.connection import get_connection


def get_table_count(table_name):
    allowed_tables = {
        "days",
        "expenses",
        "income",
        "events",
        "budgets",
        "settings",
    }

    if table_name not in allowed_tables:
        raise ValueError(f"Invalid table name: {table_name}")

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        connection.close()


def get_all_table_counts():
    tables = [
        "days",
        "expenses",
        "income",
        "events",
        "budgets",
        "settings",
    ]

    return {
        table: get_table_count(table)
        for table in tables
    }


# =========================
# DAYS QUERIES
# =========================

def get_all_days():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM days
            ORDER BY Date DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_day_by_date(day_date):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM days
            WHERE Date = %s
        """, (day_date,))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

def add_day(
    date,
    day_type,
    work_status,
    health_impact,
    travel,
    special_event,
    stress_level,
    notes,
    sleep_hours,
    social_activity,
    location,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO days (
                Date,
                Day_Type,
                Work_Status,
                Health_Impact,
                Travel,
                Special_Event,
                Stress_Level,
                Notes,
                Sleep_Hours,
                Social_Activity,
                Location
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            date,
            day_type,
            work_status,
            health_impact,
            travel,
            special_event,
            stress_level,
            notes,
            sleep_hours,
            social_activity,
            location,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def update_day(
    date,
    day_type,
    work_status,
    health_impact,
    travel,
    special_event,
    stress_level,
    notes,
    sleep_hours,
    social_activity,
    location,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE days
            SET
                Day_Type = %s,
                Work_Status = %s,
                Health_Impact = %s,
                Travel = %s,
                Special_Event = %s,
                Stress_Level = %s,
                Notes = %s,
                Sleep_Hours = %s,
                Social_Activity = %s,
                Location = %s
            WHERE Date = %s
        """, (
            day_type,
            work_status,
            health_impact,
            travel,
            special_event,
            stress_level,
            notes,
            sleep_hours,
            social_activity,
            location,
            date,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def delete_day(date):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM days
            WHERE Date = %s
        """, (date,))

        connection.commit()

    finally:
        cursor.close()
        connection.close()

# =========================
# EXPENSES QUERIES
# =========================

def get_all_expenses():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM expenses
            ORDER BY Date DESC, Time DESC, ID DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_expense_by_id(expense_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM expenses
            WHERE ID = %s
        """, (expense_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def add_expense(date, time, category, description, amount):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO expenses (
                Date,
                Time,
                Category,
                Description,
                Amount
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            date,
            time,
            category,
            description,
            amount,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def update_expense(
    expense_id,
    date,
    time,
    category,
    description,
    amount,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE expenses
            SET
                Date = %s,
                Time = %s,
                Category = %s,
                Description = %s,
                Amount = %s
            WHERE ID = %s
        """, (
            date,
            time,
            category,
            description,
            amount,
            expense_id,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def delete_expense(expense_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM expenses
            WHERE ID = %s
        """, (expense_id,))

        connection.commit()

    finally:
        cursor.close()
        connection.close()

# =========================
# INCOME QUERIES
# =========================

def get_all_income():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM income
            ORDER BY Date DESC, Time DESC, ID DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_income_by_id(income_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM income
            WHERE ID = %s
        """, (income_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def add_income(date, time, source, description, amount, income_type):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO income (
                Date,
                Time,
                Source,
                Description,
                Amount,
                Type
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            date,
            time,
            source,
            description,
            amount,
            income_type,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def update_income(
    income_id,
    date,
    time,
    source,
    description,
    amount,
    income_type,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE income
            SET
                Date = %s,
                Time = %s,
                Source = %s,
                Description = %s,
                Amount = %s,
                Type = %s
            WHERE ID = %s
        """, (
            date,
            time,
            source,
            description,
            amount,
            income_type,
            income_id,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def delete_income(income_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM income
            WHERE ID = %s
        """, (income_id,))

        connection.commit()

    finally:
        cursor.close()
        connection.close()

# =========================
# EVENTS QUERIES
# =========================

def get_all_events():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM events
            ORDER BY Date DESC, Time DESC, ID DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_event_by_id(event_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM events
            WHERE ID = %s
        """, (event_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def add_event(date, time, event_type, description):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO events (
                Date,
                Time,
                Event_Type,
                Description
            )
            VALUES (%s, %s, %s, %s)
        """, (
            date,
            time,
            event_type,
            description,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def update_event(
    event_id,
    date,
    time,
    event_type,
    description,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE events
            SET
                Date = %s,
                Time = %s,
                Event_Type = %s,
                Description = %s
            WHERE ID = %s
        """, (
            date,
            time,
            event_type,
            description,
            event_id,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def delete_event(event_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM events
            WHERE ID = %s
        """, (event_id,))

        connection.commit()

    finally:
        cursor.close()
        connection.close()

# =========================
# BUDGETS QUERIES
# =========================

def get_all_budgets():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM budgets
            ORDER BY Month DESC, Category ASC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_budget(month, category):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM budgets
            WHERE Month = %s
              AND Category = %s
        """, (month, category))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def add_budget(month, category, budget_limit, notes):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO budgets (
                Month,
                Category,
                `Limit`,
                Notes
            )
            VALUES (%s, %s, %s, %s)
        """, (
            month,
            category,
            budget_limit,
            notes,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def update_budget(month, category, budget_limit, notes):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE budgets
            SET
                `Limit` = %s,
                Notes = %s
            WHERE Month = %s
              AND Category = %s
        """, (
            budget_limit,
            notes,
            month,
            category,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def delete_budget(month, category):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM budgets
            WHERE Month = %s
              AND Category = %s
        """, (month, category))

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    # ==================================================
# SETTINGS QUERIES
# ==================================================

def get_all_settings():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM settings
            ORDER BY Setting ASC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_setting(setting):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM settings
            WHERE Setting = %s
        """, (setting,))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def add_setting(setting, value):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO settings (
                Setting,
                Value
            )
            VALUES (%s, %s)
        """, (
            setting,
            value,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def update_setting(setting, value):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE settings
            SET
                Value = %s
            WHERE Setting = %s
        """, (
            value,
            setting,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def delete_setting(setting):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM settings
            WHERE Setting = %s
        """, (setting,))

        connection.commit()

    finally:
        cursor.close()
        connection.close()