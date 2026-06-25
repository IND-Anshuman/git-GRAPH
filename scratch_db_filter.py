import sqlite3

conn = sqlite3.connect('git_graph.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

print("Tables with rows > 0:")
for table in sorted(tables):
    try:
        cursor.execute(f"SELECT count(*) FROM {table}")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Table '{table}': {count} rows")
    except Exception as e:
        print(f"Error querying {table}: {e}")

conn.close()
