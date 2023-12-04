from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.sqlite'
app.config['SECRET_KEY'] = 'tiIpFuS!5AG6'
db = SQLAlchemy(app)
login_manager = LoginManager(app)