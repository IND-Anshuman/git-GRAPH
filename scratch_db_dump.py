import sqlite3

conn = sqlite3.connect('git_graph.db')
cursor = conn.cursor()

def dump_table(table_name):
    print(f"\n--- DUMP OF {table_name} ---")
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [c[1] for c in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    print("Columns:", cols)
    for r in rows:
        print(dict(zip(cols, r)))

dump_table("repositories")
dump_table("capabilities")
dump_table("capability_candidates")

conn.close()
