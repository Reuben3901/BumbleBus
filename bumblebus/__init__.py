from flask import Flask #, render_template, url_for, flash, redirect

# ORM - Object Relational Mapper - Easy to use object-oriented way
# SQL alchemy can connect to sqlite and postgres
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# Handles all of the sessions in the background for us
from flask_login import LoginManager

# Import forms from forms.py
#from forms import RegistrationForm, LoginForm

from flaskext.markdown import Markdown

# Flask Database Migration
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


app = Flask(__name__)

#import secrets
#secrets.token_hex(16)
app.config['SECRET_KEY'] = 'd404c8c527aecbcd7686323785ef2bc5'


# /// - relative path from currrent file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# login view for @login_required decorator in routes
# function name of the route
login_manager.login_view = 'login'
# Styles the please log in to access this page message
login_manager.login_message_category = 'info'

Markdown(app)

migrate = Migrate(app,db) #Initializing migrate.
manager = Manager(app)
manager.add_command('db',MigrateCommand)

from bumblebus import routes

	