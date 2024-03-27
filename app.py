from flask import Flask
from extensions import db
from layers.domain import User
from layers.extraction import insert_doctor_data
from layers.authorization import *


app = Flask(__name__)
app.secret_key = 'secret_key'
app.register_blueprint(auth_blueprint, url_prefix='')

password = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@localhost/layered_architecture'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    db.create_all()
    insert_doctor_data()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))