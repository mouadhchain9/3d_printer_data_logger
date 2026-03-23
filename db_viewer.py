import sqlite3

conn = sqlite3.connect("telemetry.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM telemetry ORDER BY id ASC LIMIT 100")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
