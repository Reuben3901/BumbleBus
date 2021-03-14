from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
# Used for validation purposes
from bootstrap.models import User
# Used to check if username has change since or form queries the db for emails that already exist
from flask_login import current_user
# FileAllowed allows us to control what type of files are allowed to be uploaded
from flask_wtf.file import FileField, FileAllowed

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')
	
	# Custom validation for validating usernames not in db before trying to create new account
	# def validate_field(self, field):
	# 	if True:
			# raise ValidationError('Validation Message')

	def validate_username(self, username):
		# None is return if no duplicate username
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		# None is return if no duplicate email
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')
	
	# def __init__(self, arg):
	# 	super(RegistrationForm, self).__init__()
	# 	self.arg = arg


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Photo', validators=[FileAllowed(['jpg','png'])])
	submit = SubmitField('Update')
	
	def validate_username(self, username):
		if username.data != current_user.username:
			# None is return if no duplicate username
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		if email.data != current_user.email:
			# None is return if no duplicate email
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
	postType = RadioField('Post Type', choices=[('blog','Text Blog'),('vlog','Video Blog')])
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	summary = TextAreaField('Summary (Pinned Posts)', validators=[DataRequired()])
	picture = FileField('Blog Photo', validators=[FileAllowed(['jpg','png'])])
	pinned = BooleanField('Pinned')
	published = BooleanField('Published')
	submit = SubmitField('Post')
