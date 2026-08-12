
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="personal_finance_ai",
        port=3306
    )