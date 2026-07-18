import sqlite3
import sys


def init_db():
    conn = sqlite3.connect('expense.db')
    cursor = conn.cursor()

    # 1. Create the table safely (Uses INTEGER for cents to avoid floating-point bugs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        amount_cents INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL
    );
    """)

    # Check if user added the '--seed' flag in the terminal
    if "--seed" in sys.argv:
        print("⚠️ Seeding flag detected. Wiping existing rows and injecting fake data...")

        # Destructive actions are now locked behind the flag safely!
        cursor.execute("DELETE FROM expenses;")

        # Amounts are stored as exact integer counts of cents (€14.50 -> 1450)
        fake_expenses = [
            (1450, "2026-07-15", "Train ticket to Amsterdam", "Transport"),
            (420, "2026-07-16", "Morning Coffee", "Food"),
            (6500, "2026-07-17", "Volleyball Tournament Fee", "Sports")
        ]

        cursor.executemany("""
        INSERT INTO expenses (amount_cents, date, description, category) 
        VALUES (?, ?, ?, ?);
        """, fake_expenses)

        conn.commit()
        print("✅ Database successfully seeded.")
    else:
        print("🛡️ Table verified or created successfully. No data was altered.")

    # Show database status securely
    print("\n--- Current Database Contents ---")
    cursor.execute("SELECT id, amount_cents, date, description, category FROM expenses;")
    rows = cursor.fetchall()

    if not rows:
        print("[Database is currently empty]")
    for row in rows:
        # Format integer cents back into display euros (€)
        euros = row[1] / 100
        print(f"ID: {row[0]} | €{euros:.2f} | {row[2]} | {row[3]} ({row[4]})")

    conn.close()


if __name__ == "__main__":
    init_db()