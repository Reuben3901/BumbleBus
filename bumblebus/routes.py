from flask import render_template, url_for, flash, redirect
from bumblebus import app, db, bcrypt
from bumblebus.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from bumblebus.models import User, Post
from flask_login import login_user, current_user # check login status
from flask_login import logout_user
from flask_login import login_required # restrict route to logged in users
from flask import request # http://127.0.0.1:5000/login?next=%2Faccount access the next parameter for redirecting users to account instead of the homepage to their account

# for photo uploads
import secrets
import os
# resizing the photo
from PIL import Image
from flask import abort
from flask import jsonify, request
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

blogpostcolor="background-color: #C6BE90;"
vlogpostcolor="background-color: #AAC6C3;"

@app.route("/")
def home():
	posts = Post.query.all()
	lastPinnedPost = None
	if len(posts) > 0:
		for post in posts:
			if post.published and post.postType == 'blog' and post.pinned == True:
				lastPinnedPost = post

	return render_template('bumblebus.html', title="Bumblebus", posts=posts, lastPinnedPost=lastPinnedPost, blogpostcolor=blogpostcolor, vlogpostcolor=vlogpostcolor )

@app.route("/bumblebus")
def bumblebus():
	return render_template('bumblebus.html', title="bumblebus", posts=posts)


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


def save_blog_image(form_picture):
	random_hex = secrets.token_hex(8)
	
	_, filename_ext = os.path.splitext(form_picture.filename)
	picture_filename = random_hex + filename_ext
	picture_path = os.path.join(app.root_path, 'static/blog_pics', picture_filename)
	form_picture.save(picture_path)
	print("blog_image saved")
	
	return picture_filename

def save_blog_thumbnail(form_picture):
	random_hex = secrets.token_hex(8)
	
	_, filename_ext = os.path.splitext(form_picture.filename)
	picture_filename = random_hex + filename_ext
	picture_path = os.path.join(app.root_path, 'static/blog_pics', picture_filename)
	
	output_size = (640,640)
	new_img = Image.open(form_picture)
	new_img.thumbnail(output_size)	
	new_img.save(picture_path)  
	print("thumnail saved")

	return picture_filename

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def post_new():

	form = PostForm()
	if form.validate_on_submit():
		if form.picture.data:
			image_file = save_blog_image(form.picture.data)
			thumbnail = save_blog_thumbnail(form.picture.data)
			# INCLUDE THIS IS THE UPDATE!!!!!!!!!!
			# if current_user.image_file != 'blog_default.jpg':
			# 	previous_image = os.path.join(app.root_path, 'static/blog_pics', current_user.image_file)
			# 	os.remove(previous_image)
			post = Post(title=form.title.data, content=form.content.data, summary=form.summary.data,
						author=current_user, image_file=image_file, thumbnail=thumbnail,
						pinned=form.pinned.data, postType=form.postType.data, published=form.published.data)
		#post = Post(title=form.title.data, content=form.content.data, pinned=((False, True) [request.form.get('mycheckbox') == '1']))
		# use the backref of author instead of setting a user id
		else:
			print("this is postType:", form.postType.data)
			print("this is title:", form.title.data)
			
			post = Post(title=form.title.data, content=form.content.data, summary=form.summary.data,
						author=current_user, pinned=form.pinned.data, postType=form.postType.data, published=form.published.data)
		db.session.add(post)
		db.session.commit()
		#current_user.username = form.title.data
		#current_user.username = form.content.data
		flash(f'Your post has been created!', 'success')
		# POST-GET redirect pattern
		return redirect(url_for('home'))
	elif request.method == 'GET':
		form.postType.data = 'blog'
	
	return render_template('create_post.html', title="Create Post", form=form, legend='Create A New Post')


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
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


@app.route("/postmd/<int:post_id>", methods=['GET', 'POST'])
def postmd(post_id):
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
	
	return render_template('post_markdown.html', title=post.title, post=post)#, form=form)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def post_update(post_id):
	post = Post.query.get_or_404(post_id)

	if post.author != current_user:
		abort(403)

	form = PostForm()

	if form.validate_on_submit():	
		#post = Post(title=form.title.data, content=form.content.data, pinned=((False, True) [request.form.get('mycheckbox') == '1']))
		# use the backref of author instead of setting a user id
		postType 	 = form.postType.data
		post.title 	 = form.title.data
		post.content = form.content.data
		post.summary = form.summary.data
		post.pinned  = form.pinned.data
		post.published  = form.published.data
		db.session.commit()
		#current_user.username = form.title.data
		#current_user.username = form.content.data
		flash(f'Your post has been updated!', 'success')
		# POST-GET redirect pattern
		return redirect(url_for('post', post_id=post.id))
	elif request.method == 'GET':
		form.postType.data = post.postType
		form.title.data    = post.title
		form.content.data  = post.content
		form.summary.data  = post.summary
		form.pinned.data   = post.pinned
		form.published.data   = post.published

		# Need to show if pinned is checked
	
	return render_template('create_post.html', title="Update Post", form=form, legend='Update Post') # Shares template with post_new

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def post_delete(post_id):
	post = Post.query.get_or_404(post_id)

	post = Post.query.get_or_404(post_id)

	if post.author != current_user:
		abort(403)

	db.session.delete(post)
	db.session.commit()
	flash(f'Your post has been Deleted!', 'success')
	return redirect(url_for('posts'))




@app.route("/posts/")
@login_required
def posts():
	posts = Post.query.all()
	return render_template('posts.html', title="All Posts", posts=posts)



@app.route("/interaction/")
def interaction():
	return render_template('interaction.html', title="All Posts")


# https://www.youtube.com/watch?v=vtiiO5I90Tc
@app.route("/interactive/")
def interactive():
	return render_template('interactive.html', title="All Posts")

@app.route("/background_process/")
def background_process():
	lang = request.args.get('proglang')
	if str(lang).lower() == 'python':
		return jsonify(result='You are wise!')
	else:
		return jsonify(result='Try again.')

# https://www.youtube.com/watch?v=vtiiO5I90Tc
@app.route("/dad/")
def dad():
	return render_template('dad.html', title="All Posts")


@app.route("/blog_photos_upload", methods=['GET', 'POST'])
@login_required
def blog_photos_upload(post_id):
	post = Post.query.get_or_404(post_id)
