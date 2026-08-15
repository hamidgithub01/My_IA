from database.connection import get_connection

connection = get_connection()

try:
    cursor = connection.cursor()

    cursor.execute(
        "ALTER TABLE model_history "
        "ADD COLUMN target_name VARCHAR(150) NULL "
        "AFTER algorithm"
    )

    connection.commit()

    print("target_name added successfully.")

finally:
    cursor.close()
    connection.close()