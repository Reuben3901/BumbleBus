from bumblebus import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader #expects 4 things: is_authenticated, is_active, is_anonymous, get_id; all provided by UserMixin
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	# table name is created automatically as "user"
	# We could create our own table names with a table name attribute
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	# backref adds author column to database
	# lazy loads the database as necessary in one go. Retrieves the posts from Post table
	# capital P Post references the class
	posts = db.relationship('Post', backref='author', lazy=True)
	role = db.Column(db.String(10), nullable=False, default='Subscriber')

	# Dunder method; magic methods
	def __repr__(self):
		return f"User('{self.username}','{self.email}','{self.image_file}')"

class Post(db.Model):
	# table name is created automatically as "user"
	id = db.Column(db.Integer, primary_key=True)
	postType = db.Column(db.String(4), nullable=False)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #pass in the function and not the current time; no parens
	content = db.Column(db.Text, nullable=False)
	summary = db.Column(db.Text, nullable=False)
	# lowercase u user.id references the table name and the column name
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	pinned = db.Column(db.Boolean, nullable=False, default=False)
	image_file = db.Column(db.String(20), nullable=False, default='blog_default.jpg')
	thumbnail = db.Column(db.String(20), nullable=False, default='blog_default.jpg')
	published = db.Column(db.Boolean, nullable=False, default=False)
	

	def __repr__(self):
		return f"Post('{self.title}','{self.date_posted}')"

