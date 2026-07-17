import sqlite3

conn = sqlite3.connect('expense.db')

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL
);
""")

cursor.execute("DELETE FROM expenses;")


fake_expenses = [
    (14.50, "2026-07-15", "Train ticket to Amsterdam", "Transport"),
    (4.20, "2026-07-16", "Morning Coffee", "Food"),
    (65.00, "2026-07-17", "Volleyball Tournament Fee", "Sports")
]

cursor.executemany("""
INSERT INTO expenses (amount, date, description, category) 
VALUES (?, ?, ?, ?);
""", fake_expenses)


conn.commit()


print("--- Current Database Contents ---")
cursor.execute("SELECT id, amount, date, description, category FROM expenses;")
rows = cursor.fetchall()

for row in rows:
    print(f"ID: {row[0]} | €{row[1]:.2f} | {row[2]} | {row[3]} ({row[4]})")


conn.close()