import sqlite3
import csv

# ==========================
# CONNECT DB
# ==========================
conn = sqlite3.connect("telemetry.db")
cursor = conn.cursor()

# ==========================
# FETCH DATA
# ==========================
cursor.execute("SELECT * FROM telemetry ORDER BY timestamp ASC")
rows = cursor.fetchall()

# Get column names
columns = [desc[0] for desc in cursor.description]

# ==========================
# WRITE CSV
# ==========================
with open("telemetry_export.csv", "w", newline="") as f:
    writer = csv.writer(f)

    # header
    writer.writerow(columns)

    # data
    writer.writerows(rows)

print(f"Exported {len(rows)} rows to telemetry_export.csv")

conn.close()
