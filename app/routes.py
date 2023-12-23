from flask import (render_template, url_for, flash,
                   redirect)
from flask_login import login_user, logout_user, current_user, login_required

from app import app, bcrypt, db
from app.models import User, Post
from app.forms import RegistrationForm, LoginForm


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
                return redirect(url_for('home'))
            flash(f'Login Failed', 'danger')           
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
     logout_user()
     return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
     return render_template('account.html', title='Account')
