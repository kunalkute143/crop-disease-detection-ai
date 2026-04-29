# controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions.db import db
from app import bcrypt
import re

auth_bp = Blueprint('auth', __name__)

# Validation functions
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[\d\+\-\s]{10,15}$'
    return re.match(pattern, phone) is not None if phone else True

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        farm_location = request.form.get('farm_location', '').strip()
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        
        if not validate_email(email):
            errors.append('Please enter a valid email address')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if not full_name:
            errors.append('Full name is required')
        
        if phone and not validate_phone(phone):
            errors.append('Please enter a valid phone number')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', form_data=request.form)
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            phone=phone,
            farm_location=farm_location
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('🎉 Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            print(f"Registration error: {e}")
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        session['language'] = session.get('language', 'en')
        session['user_id'] = user.id
        session.permanent = True
        
        flash(f'👋 Welcome back, {user.full_name}!', 'success')
        
        # Redirect to next page if specified
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.full_name
    logout_user()
    session.clear()
    flash(f'👋 Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        farm_location = request.form.get('farm_location', '').strip()
        
        errors = []
        
        if not full_name:
            errors.append('Full name is required')
        
        if phone and not validate_phone(phone):
            errors.append('Please enter a valid phone number')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('auth.edit_profile'))
        
        current_user.full_name = full_name
        current_user.phone = phone
        current_user.farm_location = farm_location
        
        try:
            db.session.commit()
            flash('✅ Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    errors = []
    
    if not bcrypt.check_password_hash(current_user.password_hash, current_password):
        errors.append('Current password is incorrect')
    
    if len(new_password) < 6:
        errors.append('New password must be at least 6 characters long')
    
    if new_password != confirm_password:
        errors.append('New passwords do not match')
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('auth.profile'))
    
    current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    try:
        db.session.commit()
        flash('✅ Password changed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('auth.profile'))