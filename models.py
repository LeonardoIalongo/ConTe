from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Many-to-Many relationship for shared expenses
shared_expenses = db.Table(
    "shared_expenses",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("expense_id", db.Integer, db.ForeignKey("expense.id")),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    expenses_paid = db.relationship("Expense", backref="paid_by")


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    shared_with = db.relationship(
        "User", secondary=shared_expenses, backref="shared_expenses"
    )
