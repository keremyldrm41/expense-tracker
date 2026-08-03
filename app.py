import sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("expense.db")
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
        amount_raw = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"]
        category = request.form["category"]

        amount_cents = round(float(amount_raw) * 100)

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

        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/about")
def about_expense():
    return "About expense-tracker!"

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    conn = get_db_connection()
    expense = conn.execute(
        'SELECT * FROM expenses WHERE id = ?', (id,)
    ).fetchone()

    if expense is None:
        conn.close()
        abort(404)

    if request.method == 'POST':
        amount_raw = request.form['amount']
        date = request.form['date']
        description = request.form['description']
        category = request.form['category']

        amount_cents = round(float(amount_raw) * 100)

        conn.execute(
            '''
            UPDATE expenses
            SET amount_cents = ?, date = ?, description = ?, category = ?
            WHERE id = ?
            ''',
            (amount_cents, date, description, category, id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('index'))


    conn.close()
    return render_template('edit.html', expense=expense)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()

    if expense is None:
        conn.close()
        abort(404)

    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.template_filter("euros")
def cents_to_euros(cents):
    return f"€{cents / 100:.2f}"


if __name__ == "__main__":
    app.run(debug=True)