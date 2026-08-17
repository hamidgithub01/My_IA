from database.connection import get_connection

c = get_connection()
cur = c.cursor()

cur.execute("SHOW TABLES")
tables = [row[0] for row in cur.fetchall()]

for table in tables:
    print("\n" + "=" * 80)
    print(table)
    print("=" * 80)

    cur.execute(f"SHOW CREATE TABLE {table}")
    row = cur.fetchone()
    print(row[1])

cur.close()
c.close()
