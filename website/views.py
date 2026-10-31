from functools import wraps
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from .model import Contacts, User
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/contactpage')
@login_required
def contactpage():
    contacts = Contacts.query.filter_by(owner_id=current_user.id).order_by(Contacts.name).all()
    return render_template("contactpage.html", contacts=contacts)


@views.route('/contacts/add', methods=['POST'])
@login_required
def add_contact():
    name = request.form.get('name', '').strip()
    phone_number = request.form.get('phoneNumber', '').strip()
    email = request.form.get('email', '').strip().lower()
    if not all((name, phone_number, email)):
        flash('Name, phone number, and email are required.', 'error')
    else:
        db.session.add(Contacts(name=name, phoneNumber=phone_number, email=email, owner_id=current_user.id))
        db.session.commit()
        flash('Contact added.', 'success')
    return redirect(url_for('views.contactpage'))


@views.route('/contacts/<int:contact_id>/edit', methods=['POST'])
@login_required
def edit_contact(contact_id):
    contact = Contacts.query.filter_by(id=contact_id, owner_id=current_user.id).first_or_404()
    contact.name = request.form.get('name', '').strip()
    contact.phoneNumber = request.form.get('phoneNumber', '').strip()
    contact.email = request.form.get('email', '').strip().lower()
    if not all((contact.name, contact.phoneNumber, contact.email)):
        db.session.rollback()
        flash('Name, phone number, and email are required.', 'error')
    else:
        db.session.commit()
        flash('Contact updated.', 'success')
    return redirect(url_for('views.contactpage'))


@views.route('/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact = Contacts.query.filter_by(id=contact_id, owner_id=current_user.id).first_or_404()
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted.', 'success')
    return redirect(url_for('views.contactpage'))
