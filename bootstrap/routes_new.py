from flask import render_template, url_for, flash, redirect
from bootstrap import app, db, bcrypt
from bootstrap.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from bootstrap.models import User, Post
from flask_login import login_user, current_user # check login status
from flask_login import logout_user
from flask_login import login_required # restrict route to logged in users
from flask import request # http://127.0.0.1:5000/login?next=%2Faccount access the next parameter for redirecting users to account instead of the homepage to their account

# for photo uploads
import secrets
import os
# resizing the photo
from PIL import Image

# posts = [
# 	{
# 		'author':'Jane Doe',
# 		'title':'Blog post 1',
# 		'content':'First post content',
# 		'date_posted':'April 21, 2018',
# 	},
# 	{
# 		'author':'John Doe',
# 		'title':'Blog post 2',
# 		'content':'Second post content',
# 		'date_posted':'April 21, 2018',
# 	}
# ]

@app.route("/")
@app.route("/home")
def home():
	posts = Post.query.all()
	return render_template('home.html', title="Homepage", posts=posts)

@app.route("/about")
def about():
	return render_template('about.html', title="About")

@app.route("/bootstrap")
def bootstrap():
	return render_template('bootstrap.html', title="Bootstrap", posts=posts)

@app.route("/bumblebus")
def bumblebus():
	posts = Post.query.all()
	return render_template('bumblebus.html', title="Bootstrap", posts=posts)

@app.route("/register", methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Thanks for joining, {form.username.data}! You are now able to log in.', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title="Register", form=form)

@app.route("/login", methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data) # form.remember.data returns boolean
			# If the user is attempting to log in from /account page
			next_page = request.args.get('next') #request args is a dictionary, square bracket would throw error if key doesn't exist
			flash(f'Welcome back {form.email.data}!', 'success')
			return redirect(next_page) if next_page else redirect(url_for('home')) #turnery conditional
		else: 
			flash(f'Login Unsuccessful. Please check Email and Password', 'danger')
	return render_template('login.html', title="Login", form=form)

@app.route("/logout")
def logout():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	else:
		logout_user()
		return redirect(url_for('home'))


def save_profile_picture(form_picture):
	random_hex = secrets.token_hex(8)
	#f_name, f_ext = os.path.splitext(form_picture.filename)
	# a  variable to throw away, does not get ide error for unused variable
	_, filename_ext = os.path.splitext(form_picture.filename)
	picture_filename = random_hex + filename_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
	#form_picture.save(picture_path)

	#return picture_filename

	#The above works, below is to resize incoming photos
	output_size = (250,250)
	new_img = Image.open(form_picture)
	new_img.thumbnail(output_size)	

	new_img.save(picture_path)  

	return picture_filename


@app.route("/account", methods=['GET','POST'])
@login_required # need to tell where the login view is located.. inside init
def account():
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	form = UpdateAccountForm()

	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_profile_picture(form.picture.data)
			if current_user.image_file != 'default.jpg':
				previous_image = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
				os.remove(previous_image)
			current_user.image_file = picture_file
	
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash(f'Your account has been updated!', 'success')
		# POST-GET redirect pattern
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('account.html', title="Account", image_file=image_file, form=form)#, form=form)



def save_blog_picture(form_picture):
	random_hex = secrets.token_hex(8)
	#f_name, f_ext = os.path.splitext(form_picture.filename)
	# a  variable to throw away, does not get ide error for unused variable
	_, filename_ext = os.path.splitext(form_picture.filename)
	picture_filename = random_hex + filename_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
	
	output_size = (640,640)
	new_img = Image.open(form_picture)
	new_img.thumbnail(output_size)	

	new_img.save(picture_path)  

	return picture_filename


@app.route("/account", methods=['GET','POST'])
@login_required # need to tell where the login view is located.. inside init
def account():
	
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_blog_picture(form.picture.data)
			if current_user.image_file != 'default.jpg':
				previous_image = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
				os.remove(previous_image)
			current_user.image_file = picture_file
	
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash(f'Your account has been updated!', 'success')
		# POST-GET redirect pattern
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('account.html', title="Account", image_file=image_file, form=form)#, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def post_new():
	image_file = url_for('static', filename='blog_pics/' + current_user.image_file)
	
	form = PostForm()
	if form.validate_on_submit():
		if form.picture.data:
			thumbnail = save_blog_picture(form.picture.data)
			# if current_user.image_file != 'blog_default.jpg':
			# 	previous_image = os.path.join(app.root_path, 'static/blog_pics', current_user.image_file)
			# 	os.remove(previous_image)
			current_user.image_file = picture_file
			post = Post(title=form.title.data, content=form.content.data, author=current_user, image_file=form.picture.data, thumbnail=thumbnail)
		#post = Post(title=form.title.data, content=form.content.data, pinned=((False, True) [request.form.get('mycheckbox') == '1']))
		# use the backref of author instead of setting a user id
		else:
			post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		#current_user.username = form.title.data
		#current_user.username = form.content.data
		flash(f'Your post has been created!', 'success')
		# POST-GET redirect pattern
		return redirect(url_for('home'))
	
	return render_template('create_post.html', title="Create Post", form=form)#, form=form)






@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
	post = Post.query.get_or_404(post_id)

	form = PostForm()
	if form.validate_on_submit():	
		#post = Post(title=form.title.data, content=form.content.data, pinned=((False, True) [request.form.get('mycheckbox') == '1']))
		# use the backref of author instead of setting a user id
		post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		#current_user.username = form.title.data
		#current_user.username = form.content.data
		flash(f'Your post has been created!', 'success')
		# POST-GET redirect pattern
		return redirect(url_for('home'))
	
	return render_template('post.html', title=post.title, post=post)#, form=form)
