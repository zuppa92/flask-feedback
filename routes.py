from flask import render_template, url_for, flash, redirect, request, session
from app import app, db, bcrypt
from forms import RegistrationForm, LoginForm, FeedbackForm
from models import User, Feedback
from utils import login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            if existing_user.username == form.username.data:
                flash('Username already exists. Please choose a different one.', 'danger')
            if existing_user.email == form.email.data:
                flash('Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        session['username'] = user.username
        return redirect(url_for('user_profile', username=user.username))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['username'] = user.username
            flash('You have been logged in!', 'success')
            return redirect(url_for('user_profile', username=user.username))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route("/users/<username>")
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if session['username'] != username:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('home'))
    feedbacks = Feedback.query.filter_by(username=username).all()
    return render_template('user_profile.html', user=user, feedbacks=feedbacks)

@app.route("/users/<username>/delete", methods=['POST'])
@login_required
def delete_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if session['username'] != username:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('home'))
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('home'))

@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
@login_required
def add_feedback(username):
    if session['username'] != username:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('home'))
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(
            title=form.title.data,
            content=form.content.data,
            username=username
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback added!', 'success')
        return redirect(url_for('user_profile', username=username))
    return render_template('new_feedback.html', form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=['GET', 'POST'])
@login_required
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if session['username'] != feedback.username:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('home'))
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash('Feedback updated!', 'success')
        return redirect(url_for('user_profile', username=feedback.username))
    elif request.method == 'GET':
        form.title.data = feedback.title
        form.content.data = feedback.content
    return render_template('edit_feedback.html', form=form)

@app.route("/feedback/<int:feedback_id>/delete", methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if session['username'] != feedback.username:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('home'))
    db.session.delete(feedback)
    db.session.commit()
    flash('Feedback deleted!', 'success')
    return redirect(url_for('user_profile', username=feedback.username))
