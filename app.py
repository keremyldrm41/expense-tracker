import sqlite3
import calendar
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

@app.route("/summary")
def summary():
    selected_year = request.args.get("year")
    selected_month = request.args.get("month")

    conn = get_db_connection()

    years = conn.execute(
        """
        SELECT DISTINCT strftime('%Y', date) as year 
        FROM expenses 
        ORDER BY year DESC
    """
    ).fetchall()
    years_list = [row["year"] for row in years if row["year"]]

    if not selected_year and years_list:
        selected_year = years_list[0]

    months_data = []
    month_expenses = []
    category_totals = []
    selected_month_name = ""
    month_total_cents = 0

    if selected_year:
        months_raw = conn.execute(
            """
            SELECT 
                strftime('%m', date) as month_num,
                SUM(amount_cents) as total_cents
            FROM expenses
            WHERE strftime('%Y', date) = ?
            GROUP BY month_num
            ORDER BY month_num ASC
        """,
            (selected_year,),
        ).fetchall()

        for row in months_raw:
            m_num = row["month_num"]
            months_data.append(
                {
                    "num": m_num,
                    "name": calendar.month_name[int(m_num)],
                    "total_cents": row["total_cents"],
                }
            )

        if selected_month:
            selected_month_name = calendar.month_name[int(selected_month)]

            month_expenses = conn.execute(
                """
                SELECT id, amount_cents, date, description, category 
                FROM expenses 
                WHERE strftime('%Y-%m', date) = ?
                ORDER BY date DESC, id DESC
            """,
                (f"{selected_year}-{selected_month}",),
            ).fetchall()

            category_totals = conn.execute(
                """
                SELECT category, SUM(amount_cents) as total_cents
                FROM expenses
                WHERE strftime('%Y-%m', date) = ?
                GROUP BY category
                ORDER BY total_cents DESC
            """,
                (f"{selected_year}-{selected_month}",),
            ).fetchall()

            month_total_cents = sum(row["total_cents"] for row in category_totals)

    conn.close()

    return render_template(
        "summary.html",
        years=years_list,
        selected_year=selected_year,
        selected_month=selected_month,
        selected_month_name=selected_month_name,
        months_data=months_data,
        expenses=month_expenses,
        category_totals=category_totals,
        month_total_cents=month_total_cents,
    )

if __name__ == "__main__":
    app.run(debug=True)