from extensions import db
from flask_login import UserMixin
from layers.exceptions import DomainError

class User(UserMixin, db.Model):
    try:
        __tablename__ = 'users'
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(100), unique=True, nullable=False)
        password = db.Column(db.String(200), nullable=False)
        user_type = db.Column(db.String(50))
        pass
    except Exception as e:
        raise DomainError from e
