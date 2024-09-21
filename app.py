from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Expense, ArchivedExpense
import shutil
import os
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "some_secret_key"
db.init_app(app)

BACKUP_FOLDER = "backup/"  # Folder to store backups


@app.before_request
def create_tables():
    db.create_all()
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)  # Create backup folder if it doesn't exist


@app.route("/")
def index():
    users = User.query.all()
    expenses = Expense.query.filter_by(deleted=False).all()
    return render_template("index.html", users=users, expenses=expenses)


# Adding a user
@app.route("/add_user", methods=["POST"])
def add_user():
    name = request.form["name"]
    if name:
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
    return redirect(url_for("index"))


# Adding an expense
@app.route("/add_expense", methods=["POST"])
def add_expense():
    description = request.form["description"]
    amount = request.form["amount"]
    paid_by_id = request.form["paid_by"]
    shared_with_ids = request.form.getlist("shared_with")

    if description and amount and paid_by_id:
        amount = float(amount)
        paid_by = User.query.get(paid_by_id)
        new_expense = Expense(description=description, amount=amount, paid_by=paid_by)
        db.session.add(new_expense)
        db.session.commit()

        for user_id in shared_with_ids:
            user = User.query.get(user_id)
            new_expense.shared_with.append(user)

        db.session.commit()

    return redirect(url_for("index"))


# Soft delete an expense
@app.route("/delete_expense/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense:
        archive_expense(expense)  # Archive the expense before deletion
        expense.deleted = True
        db.session.commit()
    return redirect(url_for("index"))


# Archive expense data before making changes
def archive_expense(expense):
    archived = ArchivedExpense(
        original_expense_id=expense.id,
        description=expense.description,
        amount=expense.amount,
        paid_by_id=expense.paid_by_id,
        version=expense.version,
    )
    db.session.add(archived)
    expense.version += 1
    db.session.commit()


# Create a backup of the SQLite database
@app.route("/backup", methods=["GET"])
def backup():
    try:
        backup_filename = f'{BACKUP_FOLDER}expenses_backup_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.db'
        shutil.copy("expenses.db", backup_filename)
        flash(f"Backup created: {backup_filename}", "success")
    except Exception as e:
        flash(f"Error creating backup: {str(e)}", "danger")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
