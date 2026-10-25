from database.connection import get_connection
from database.queries import get_all_table_counts


def load_data_page_data():
    """Load database record counts for the Data page."""
    counts = get_all_table_counts()

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM `sleep`")
        counts["sleep"] = cursor.fetchone()[0]
    finally:
        cursor.close()
        connection.close()

    return {
        "table_counts": counts,
        "total_records": sum(counts.values()),
        "expenses": counts.get("expenses", 0),
        "income": counts.get("income", 0),
    }
