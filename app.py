from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Expense

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.before_request
def create_tables():
    db.create_all()


@app.route("/")
def index():
    users = User.query.all()
    expenses = Expense.query.all()
    return render_template("index.html", users=users, expenses=expenses)


@app.route("/add_user", methods=["POST"])
def add_user():
    name = request.form["name"]
    if name:
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
    return redirect(url_for("index"))


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

        # Share the expense
        for user_id in shared_with_ids:
            user = User.query.get(user_id)
            new_expense.shared_with.append(user)

        db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
