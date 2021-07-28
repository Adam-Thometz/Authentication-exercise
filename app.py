from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterUserForm, LoginUserForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    """Brings user to register page"""
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Show registration form and allow user to sign up"""
    form = RegisterUserForm()
    if form.validate_on_submit():
        username = form.username.data,
        password = form.password.data,
        email = form.email.data,
        first_name = form.first_name.data,
        last_name = form.last_name.data
        
        new_user = User.register(username, password, email, first_name, last_name)
        
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken! Plase pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        flash(f'Account successfully created! Welcome {new_user.first_name} {new_user.last_name}!', 'success')
        return redirect('/secret')
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Log user in"""
    form = LoginUserForm()
    if form.validate_on_submit():
        username = form.username.data,
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back {user.username}!", "primary")
            session['user_id'] = user.id
            return redirect('/secret')
        else:
            form.username.errors = ['Invalid username/password']
    
    return render_template('login.html', form=form)

@app.route('/secret')
def show_secret():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect('/register')
    return 'You made it!'