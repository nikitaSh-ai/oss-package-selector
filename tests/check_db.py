import sqlite3

conn = sqlite3.connect("data/raw_packages.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM packages")
rows = cursor.fetchall()

col_names = [desc[0] for desc in cursor.description]
print("Columns:", col_names)
print("---")
for row in rows:
    print(row)

conn.close()