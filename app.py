import sqlite3
from flask import Flask, render_template

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("expense.db")
    # Setting row_factory lets us access columns by name (e.g., row['category'])
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db_connection()
    # Fetch all expense rows from the database
    expenses = conn.execute(
        "SELECT id, amount_cents, date, description, category FROM expenses"
    ).fetchall()
    conn.close()

    # Pass the database rows to the HTML template as a keyword argument
    return render_template("index.html", expenses=expenses)


@app.route("/about")
def about_expense():
    return "About expense-tracker!"

@app.template_filter('euros')
def cents_to_euros(cents):
    return f"€{cents / 100:.2f}"

if __name__ == "__main__":
    app.run(debug=True)