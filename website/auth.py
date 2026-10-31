from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from website.model import User, Contacts
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        valid_password = False
        if user:
            try:
                valid_password = check_password_hash(
                    user.password, password or '')
            except ValueError:
                valid_password = user.password == password
                if valid_password:
                    user.password = generate_password_hash(password)
                    db.session.commit()
        if valid_password:
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.contactpage'))
        else:
            flash('Invalid email or password.', category='error')
    return render_template("signin.html")


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        phoneNumber = request.form.get('phoneNumber', '').strip()
        user = User.query.filter(or_(
            User.email == email, User.username == username, User.phoneNumber == phoneNumber)).first()
        if not all((username, email, password, phoneNumber)):
            flash('All fields are required.', category='error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters.', category='error')
        if user:
            flash(
                'That username, email, or phone number is already registered.', category='error')
        elif all((username, email, password, phoneNumber)) and len(password) >= 8:
            new_user = User(username=username, phoneNumber=phoneNumber,
                            email=email, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('views.contactpage'))
    return render_template("signup.html", user=current_user)
