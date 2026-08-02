import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("expense.db")
    # Setting row_factory lets us access columns by name (e.g., row['category'])
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db_connection()
    expenses = conn.execute(
        """
        SELECT id, amount_cents, date, description, category 
        FROM expenses 
        ORDER BY date DESC, id DESC
        """
    ).fetchall()
    conn.close()
    return render_template("index.html", expenses=expenses)


@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        # 1. Extract raw form values using the HTML <input name="..."> keys
        amount_raw = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"]
        category = request.form["category"]

        # 2. Convert raw Euro string (e.g., "4.20") safely to Integer Cents (420)
        amount_cents = round(float(amount_raw) * 100)

        # 3. Securely insert into database using parameterized query (?) to prevent SQL injection
        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO expenses (amount_cents, date, description, category)
            VALUES (?, ?, ?, ?)
            """,
            (amount_cents, date, description, category),
        )
        conn.commit()
        conn.close()

        # 4. Redirect user back to the home page ('index' is the function name for route '/')
        return redirect(url_for("index"))

    # If HTTP method is GET, simply display the form page
    return render_template("add.html")


@app.route("/about")
def about_expense():
    return "About expense-tracker!"


@app.template_filter("euros")
def cents_to_euros(cents):
    return f"€{cents / 100:.2f}"


if __name__ == "__main__":
    app.run(debug=True)