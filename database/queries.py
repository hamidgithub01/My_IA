
from database.connection import get_connection

# =========================================================
# TABLE COUNTS
# =========================================================

def get_table_count(table_name):
    allowed_tables = {
        "days",
        "expenses",
        "income",
        "events",
        "budgets",
        "settings",
        "activities",
        "goals",
        "health_records",
        "model_history",
        "plans",
        "prediction_feedback",
        "recurring",
        "travel",
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
        "activities",
        "goals",
        "health_records",
        "model_history",
        "plans",
        "prediction_feedback",
        "recurring",
        "travel",
    ]
    
    return {
        table: get_table_count(table)
        for table in tables
    }

# =========================================================
# DAYS QUERIES
# =========================================================

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

# =========================================================
# EXPENSES QUERIES
# =========================================================

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

# =========================================================
# INCOME QUERIES
# =========================================================

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

# =========================================================
# EVENTS QUERIES
# =========================================================

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

# =========================================================
# BUDGETS QUERIES
# =========================================================

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

# =========================================================
# SETTINGS QUERIES
# =========================================================

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

# =========================================================
# TRAVEL QUERIES
# =========================================================

def get_all_travel():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM travel
            ORDER BY Start_Date DESC, Travel_ID DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_travel_by_id(travel_id):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM travel
            WHERE Travel_ID = %s
        """, (travel_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def add_travel(
    start_date,
    end_date,
    destination,
    purpose,
    transport,
    planned,
    actual,
    expected_cost,
    actual_cost,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO travel (
                Start_Date,
                End_Date,
                Destination,
                Purpose,
                Transport,
                Planned,
                Actual,
                Expected_Cost,
                Actual_Cost,
                Notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            start_date,
            end_date,
            destination,
            purpose,
            transport,
            planned,
            actual,
            expected_cost,
            actual_cost,
            notes,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def update_travel(
    travel_id,
    start_date,
    end_date,
    destination,
    purpose,
    transport,
    planned,
    actual,
    expected_cost,
    actual_cost,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE travel
            SET
                Start_Date = %s,
                End_Date = %s,
                Destination = %s,
                Purpose = %s,
                Transport = %s,
                Planned = %s,
                Actual = %s,
                Expected_Cost = %s,
                Actual_Cost = %s,
                Notes = %s
            WHERE Travel_ID = %s
        """, (
            start_date,
            end_date,
            destination,
            purpose,
            transport,
            planned,
            actual,
            expected_cost,
            actual_cost,
            notes,
            travel_id,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_travel(travel_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM travel
            WHERE Travel_ID = %s
        """, (travel_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# =========================================================
# HEALTH RECORDS QUERIES
# =========================================================

def get_all_health_records():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM health_records
            ORDER BY Date DESC, Health_ID DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_health_record_by_id(health_id):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM health_records
            WHERE Health_ID = %s
        """, (health_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def get_health_record_by_date(date):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM health_records
            WHERE Date = %s
        """, (date,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def add_health_record(
    date,
    health_status,
    energy_level,
    symptoms,
    severity,
    treatment,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO health_records (
                Date,
                Health_Status,
                Energy_Level,
                Symptoms,
                Severity,
                Treatment,
                Notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            date,
            health_status,
            energy_level,
            symptoms,
            severity,
            treatment,
            notes,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def update_health_record(
    health_id,
    date,
    health_status,
    energy_level,
    symptoms,
    severity,
    treatment,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE health_records
            SET
                Date = %s,
                Health_Status = %s,
                Energy_Level = %s,
                Symptoms = %s,
                Severity = %s,
                Treatment = %s,
                Notes = %s
            WHERE Health_ID = %s
        """, (
            date,
            health_status,
            energy_level,
            symptoms,
            severity,
            treatment,
            notes,
            health_id,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_health_record(health_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM health_records
            WHERE Health_ID = %s
        """, (health_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# =========================================================
# ACTIVITIES QUERIES
# =========================================================

def get_all_activities():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM activities
            ORDER BY Date DESC, Activity_ID DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_activity_by_id(activity_id):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM activities
            WHERE Activity_ID = %s
        """, (activity_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def add_activity(
    date,
    activity_type,
    duration_minutes,
    planned,
    actual,
    location,
    cost,
    people_count,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO activities (
                Date,
                Activity_Type,
                Duration_Minutes,
                Planned,
                Actual,
                Location,
                Cost,
                People_Count,
                Notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            date,
            activity_type,
            duration_minutes,
            planned,
            actual,
            location,
            cost,
            people_count,
            notes,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def update_activity(
    activity_id,
    date,
    activity_type,
    duration_minutes,
    planned,
    actual,
    location,
    cost,
    people_count,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE activities
            SET
                Date = %s,
                Activity_Type = %s,
                Duration_Minutes = %s,
                Planned = %s,
                Actual = %s,
                Location = %s,
                Cost = %s,
                People_Count = %s,
                Notes = %s
            WHERE Activity_ID = %s
        """, (
            date,
            activity_type,
            duration_minutes,
            planned,
            actual,
            location,
            cost,
            people_count,
            notes,
            activity_id,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_activity(activity_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM activities
            WHERE Activity_ID = %s
        """, (activity_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# =========================================================
# PLANS QUERIES
# =========================================================

def get_all_plans():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM plans
            ORDER BY Plan_Date DESC, Plan_ID DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_plan_by_id(plan_id):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM plans
            WHERE Plan_ID = %s
        """, (plan_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def add_plan(
    plan_date,
    plan_type,
    title,
    expected_cost,
    duration_days,
    importance,
    status,
    actual_date,
    actual_cost,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO plans (
                Plan_Date,
                Plan_Type,
                Title,
                Expected_Cost,
                Duration_Days,
                Importance,
                Status,
                Actual_Date,
                Actual_Cost,
                Notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            plan_date,
            plan_type,
            title,
            expected_cost,
            duration_days,
            importance,
            status,
            actual_date,
            actual_cost,
            notes,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def update_plan(
    plan_id,
    plan_date,
    plan_type,
    title,
    expected_cost,
    duration_days,
    importance,
    status,
    actual_date,
    actual_cost,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE plans
            SET
                Plan_Date = %s,
                Plan_Type = %s,
                Title = %s,
                Expected_Cost = %s,
                Duration_Days = %s,
                Importance = %s,
                Status = %s,
                Actual_Date = %s,
                Actual_Cost = %s,
                Notes = %s
            WHERE Plan_ID = %s
        """, (
            plan_date,
            plan_type,
            title,
            expected_cost,
            duration_days,
            importance,
            status,
            actual_date,
            actual_cost,
            notes,
            plan_id,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_plan(plan_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM plans
            WHERE Plan_ID = %s
        """, (plan_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# =========================================================
# GOALS QUERIES
# =========================================================

def get_all_goals():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM goals
            ORDER BY Target_Date ASC, Goal_ID DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_goal_by_id(goal_id):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM goals
            WHERE Goal_ID = %s
        """, (goal_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def add_goal(
    goal_name,
    target_amount,
    current_amount,
    target_date,
    priority,
    status,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO goals (
                Goal_Name,
                Target_Amount,
                Current_Amount,
                Target_Date,
                Priority,
                Status,
                Notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            goal_name,
            target_amount,
            current_amount,
            target_date,
            priority,
            status,
            notes,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def update_goal(
    goal_id,
    goal_name,
    target_amount,
    current_amount,
    target_date,
    priority,
    status,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE goals
            SET
                Goal_Name = %s,
                Target_Amount = %s,
                Current_Amount = %s,
                Target_Date = %s,
                Priority = %s,
                Status = %s,
                Notes = %s
            WHERE Goal_ID = %s
        """, (
            goal_name,
            target_amount,
            current_amount,
            target_date,
            priority,
            status,
            notes,
            goal_id,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_goal(goal_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM goals
            WHERE Goal_ID = %s
        """, (goal_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# =========================================================
# RECURRING QUERIES
# =========================================================

def get_all_recurring():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM recurring
            ORDER BY Start_Date DESC, Recurring_ID DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_recurring_by_id(recurring_id):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM recurring
            WHERE Recurring_ID = %s
        """, (recurring_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def add_recurring(
    name,
    recurring_type,
    category,
    amount,
    frequency,
    day_of_month,
    day_of_week,
    start_date,
    end_date,
    is_active,
    is_fixed_amount,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO recurring (
                Name,
                Type,
                Category,
                Amount,
                Frequency,
                Day_Of_Month,
                Day_Of_Week,
                Start_Date,
                End_Date,
                Is_Active,
                Is_Fixed_Amount,
                Notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            recurring_type,
            category,
            amount,
            frequency,
            day_of_month,
            day_of_week,
            start_date,
            end_date,
            is_active,
            is_fixed_amount,
            notes,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def update_recurring(
    recurring_id,
    name,
    recurring_type,
    category,
    amount,
    frequency,
    day_of_month,
    day_of_week,
    start_date,
    end_date,
    is_active,
    is_fixed_amount,
    notes,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE recurring
            SET
                Name = %s,
                Type = %s,
                Category = %s,
                Amount = %s,
                Frequency = %s,
                Day_Of_Month = %s,
                Day_Of_Week = %s,
                Start_Date = %s,
                End_Date = %s,
                Is_Active = %s,
                Is_Fixed_Amount = %s,
                Notes = %s
            WHERE Recurring_ID = %s
        """, (
            name,
            recurring_type,
            category,
            amount,
            frequency,
            day_of_month,
            day_of_week,
            start_date,
            end_date,
            is_active,
            is_fixed_amount,
            notes,
            recurring_id,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_recurring(recurring_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM recurring
            WHERE Recurring_ID = %s
        """, (recurring_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# =========================================================
# MODEL HISTORY QUERIES
# =========================================================

def get_all_model_history():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM model_history
            ORDER BY trained_at DESC, id DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_latest_model_history():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM model_history
            ORDER BY trained_at DESC, id DESC
            LIMIT 1
        """)
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def add_model_history(
    trained_at,
    algorithm,
    training_rows,
    feature_names,
    coefficients,
    intercept,
    feature_means,
    feature_scales,
    mae,
    rmse,
    r_squared,
    reused_previous_state,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO model_history (
                trained_at,
                algorithm,
                training_rows,
                feature_names,
                coefficients,
                intercept,
                feature_means,
                feature_scales,
                mae,
                rmse,
                r_squared,
                reused_previous_state
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            trained_at,
            algorithm,
            training_rows,
            feature_names,
            coefficients,
            intercept,
            feature_means,
            feature_scales,
            mae,
            rmse,
            r_squared,
            reused_previous_state,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# =========================================================
# PREDICTION FEEDBACK QUERIES
# =========================================================

def get_all_prediction_feedback():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM prediction_feedback
            ORDER BY Prediction_Date DESC, Feedback_ID DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_prediction_feedback_by_id(feedback_id):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM prediction_feedback
            WHERE Feedback_ID = %s
        """, (feedback_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def add_prediction_feedback(
    prediction_date,
    target_name,
    predicted_value,
    actual_value,
    error_value,
    error_percentage,
    model_name,
    model_version,
):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO prediction_feedback (
                Prediction_Date,
                Target_Name,
                Predicted_Value,
                Actual_Value,
                Error_Value,
                Error_Percentage,
                Model_Name,
                Model_Version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            prediction_date,
            target_name,
            predicted_value,
            actual_value,
            error_value,
            error_percentage,
            model_name,
            model_version,
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_prediction_feedback(feedback_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM prediction_feedback
            WHERE Feedback_ID = %s
        """, (feedback_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# =========================================================
# SLEEP QUERIES
# =========================================================

def get_all_sleep_records():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM sleep
            ORDER BY Date DESC, Start_Time DESC, Sleep_ID DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_sleep_record_by_id(sleep_id):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM sleep
            WHERE Sleep_ID = %s
        """, (sleep_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def get_sleep_records_by_date(date):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM sleep
            WHERE Date = %s
            ORDER BY Start_Time ASC, Sleep_ID ASC
        """, (date,))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def add_sleep_record(
    date,
    start_time,
    end_time,
    duration_minutes,
    sleep_type,
    continuity,
    location,
    position,
    awakenings,
    sleep_quality,
    noise_level,
    light_level,
    temperature_level,
    comfort_level,
    stress_before_sleep,
    caffeine_before_sleep,
    screen_before_sleep,
    before_sleep_activity,
    dreams,
    notes,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO sleep (
                Date,
                Start_Time,
                End_Time,
                Duration_Minutes,
                Sleep_Type,
                Continuity,
                Location,
                Position,
                Awakenings,
                Sleep_Quality,
                Noise_Level,
                Light_Level,
                Temperature_Level,
                Comfort_Level,
                Stress_Before_Sleep,
                Caffeine_Before_Sleep,
                Screen_Before_Sleep,
                Before_Sleep_Activity,
                Dreams,
                Notes
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            date,
            start_time,
            end_time,
            duration_minutes,
            sleep_type,
            continuity,
            location,
            position,
            awakenings,
            sleep_quality,
            noise_level,
            light_level,
            temperature_level,
            comfort_level,
            stress_before_sleep,
            caffeine_before_sleep,
            screen_before_sleep,
            before_sleep_activity,
            dreams,
            notes,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def update_sleep_record(
    sleep_id,
    date,
    start_time,
    end_time,
    duration_minutes,
    sleep_type,
    continuity,
    location,
    position,
    awakenings,
    sleep_quality,
    noise_level,
    light_level,
    temperature_level,
    comfort_level,
    stress_before_sleep,
    caffeine_before_sleep,
    screen_before_sleep,
    before_sleep_activity,
    dreams,
    notes,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE sleep
            SET
                Date = %s,
                Start_Time = %s,
                End_Time = %s,
                Duration_Minutes = %s,
                Sleep_Type = %s,
                Continuity = %s,
                Location = %s,
                Position = %s,
                Awakenings = %s,
                Sleep_Quality = %s,
                Noise_Level = %s,
                Light_Level = %s,
                Temperature_Level = %s,
                Comfort_Level = %s,
                Stress_Before_Sleep = %s,
                Caffeine_Before_Sleep = %s,
                Screen_Before_Sleep = %s,
                Before_Sleep_Activity = %s,
                Dreams = %s,
                Notes = %s
            WHERE Sleep_ID = %s
        """, (
            date,
            start_time,
            end_time,
            duration_minutes,
            sleep_type,
            continuity,
            location,
            position,
            awakenings,
            sleep_quality,
            noise_level,
            light_level,
            temperature_level,
            comfort_level,
            stress_before_sleep,
            caffeine_before_sleep,
            screen_before_sleep,
            before_sleep_activity,
            dreams,
            notes,
            sleep_id,
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def delete_sleep_record(sleep_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM sleep
            WHERE Sleep_ID = %s
        """, (sleep_id,))

        connection.commit()

    finally:
        cursor.close()
        connection.close()