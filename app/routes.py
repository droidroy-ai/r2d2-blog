from flask import (render_template, url_for, flash,
                   redirect, request)
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from app import app, bcrypt, db
from app.models import User, Post
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm


posts = [
    {'author': 'Abhik Roy',
     'title': 'Blog 1',
     'content': 'Content ..',
     'date': 'Dec 1, 2023'},
    {'author': 'Jane Doe',
     'title': 'Blog 2',
     'content': 'Content 2 ..',
     'date': 'Dec 2, 2023'}
]

@app.route("/")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(password=form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            flash(f'Login Failed', 'danger')           
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
     logout_user()
     return redirect(url_for('home'))

def save_image(image):
    random_str = secrets.token_hex(8)
    file_name, file_ext = os.path.splitext(image.filename)
    image_filename = random_str + file_ext
    image_path = os.path.join(app.root_path, 'static/profile_pics', image_filename)
    image.save(image_path)
    return image_filename

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
     form = UpdateAccountForm()
     if form.validate_on_submit():
        if form.pic.data:
            pic_file = save_image(form.pic.data)
            current_user.image_file = pic_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Account is updated', 'success')
        return redirect(url_for('account'))
     elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email          
     image_file = url_for('static', 
                          filename='profile_pics/' + current_user.image_file)
     return render_template('account.html', title='Account', image_file=image_file, form=form)
