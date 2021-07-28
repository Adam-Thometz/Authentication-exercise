from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterUserForm, LoginUserForm, FeedbackForm
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
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        new_user = User.register(username, password, email, first_name, last_name)
        
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken! Plase pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.username
        flash(f'Account successfully created! Welcome {new_user.first_name} {new_user.last_name}!', 'success')
        return redirect(f'/users/{new_user.username}')
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
            session['user_id'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
    
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user(username):
    if 'user_id' not in session or session['user_id'] != username:
        flash('Please login first', 'danger')
        return redirect('/login')
    user = User.query.get_or_404(username)
    user_feedback = Feedback.query.filter_by(username=username)
    return render_template('user.html', user=user, user_feedback=user_feedback)

@app.route('/users/<username>/delete')
def delete_user(username):
    if 'user_id' not in session or session['user_id'] != username:
        flash('Please login first', 'danger')
        return redirect('/login')
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'user_id' not in session or session['user_id'] != username:
        flash('Please login first', 'danger')
        return redirect('/login')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback added successfully!', 'success')
        return redirect(f'/users/{username}')
    return render_template('feedback-add.html', form=form)

@app.route('/feedback/<int:id>/update', methods=['GET', 'POST'])
def update_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    username = feedback.user.username
    if 'user_id' not in session or session['user_id'] != username:
        flash('Please login first', 'danger')
        return redirect('/login')
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        return redirect(f'/users/{username}')
    return render_template('feedback-edit.html', form=form)

@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    username = feedback.user.username
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/user/{username}')
    
@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Goodbye!", 'info')
    return redirect('/')