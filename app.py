import os
import sqlite3
import calendar
import math
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify

from ai import CATEGORIES, suggest_category

app = Flask(__name__)

# The Dockerfile points this at a mounted volume so the data outlives the container
DB_PATH = os.environ.get("DB_PATH", "expense.db")

MAX_AMOUNT_EUROS = 1_000_000

MAX_DESCRIPTION_CHARS = 200


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_validated_form():
    amount_raw = request.form.get("amount", "")
    date = request.form.get("date", "")
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "")

    try:
        amount = float(amount_raw)
    except ValueError:
        abort(400)
    if not math.isfinite(amount):
        abort(400)
    if not 0 < amount <= MAX_AMOUNT_EUROS:
        abort(400)

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        abort(400)

    if not description:
        abort(400)

    if category not in CATEGORIES:
        abort(400)

    return round(amount * 100), date, description, category


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
        amount_cents, date, description, category = get_validated_form()

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

    return render_template("add.html", categories=CATEGORIES)


@app.route("/api/suggest-category", methods=["POST"])
def suggest_category_api():
    data = request.get_json(silent=True) or {}
    description = data.get("description", "")

    if not isinstance(description, str):
        return jsonify({"category": None})

    suggestion = suggest_category(description[:MAX_DESCRIPTION_CHARS])
    return jsonify({"category": suggestion})


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_expense(id):
    conn = get_db_connection()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?", (id,)
    ).fetchone()

    if expense is None:
        conn.close()
        abort(404)

    if request.method == "POST":
        amount_cents, date, description, category = get_validated_form()

        conn.execute(
            """
            UPDATE expenses
            SET amount_cents = ?, date = ?, description = ?, category = ?
            WHERE id = ?
            """,
            (amount_cents, date, description, category, id),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()
    return render_template("edit.html", expense=expense, categories=CATEGORIES)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_expense(id):
    conn = get_db_connection()
    expense = conn.execute("SELECT * FROM expenses WHERE id = ?", (id,)).fetchone()

    if expense is None:
        conn.close()
        abort(404)

    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.template_filter("euros")
def cents_to_euros(cents):
    return f"€{cents / 100:.2f}"


@app.route("/summary")
def summary():
    selected_year = request.args.get("year")
    selected_month = request.args.get("month")

    if selected_year:
        try:
            year_num = int(selected_year)
        except ValueError:
            abort(404)
        if not 1900 <= year_num <= 2999:
            abort(404)
        selected_year = str(year_num)

    if selected_month:
        try:
            month_num = int(selected_month)
        except ValueError:
            abort(404)          # catches "banana"
        if not 1 <= month_num <= 12:
            abort(404)          # catches 13, 0, -1
        selected_month = f"{month_num:02d}"

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
    # Safe defaults for a laptop: loopback only, debug off.
    # The Dockerfile sets FLASK_HOST=0.0.0.0 so the port mapping can reach the app;
    # debug is opt-in (FLASK_DEBUG=1) because the debugger lets anyone who can
    # reach the port run code on the server.
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host=host, debug=debug)