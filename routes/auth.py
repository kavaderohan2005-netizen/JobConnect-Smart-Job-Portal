import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models import User, JobSeeker, Employer, Company

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_user_dashboard(current_user)

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()  # can be email or username
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not identifier or not password:
            flash('Please provide both username/email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter(
            (User.email == identifier.lower()) | (User.username == identifier)
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'warning')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.display_name}!', 'success')
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect_user_dashboard(user)
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    """Convenience 1-click login for testing Seeker, Employer, and Admin."""
    role_map = {
        'seeker': 'seeker@jobconnect.com',
        'employer': 'employer@jobconnect.com',
        'admin': 'admin@jobconnect.com'
    }
    email = role_map.get(role)
    if not email:
        flash('Invalid demo role.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash(f'Demo account for {role} not found. Please run seed_data.py.', 'warning')
        return redirect(url_for('auth.login'))

    login_user(user, remember=True)
    flash(f'Logged in via Demo as {user.display_name} ({role.title()})', 'info')
    return redirect_user_dashboard(user)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_user_dashboard(current_user)

    if request.method == 'POST':
        role = request.form.get('role', 'job_seeker')
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()

        # Validation
        if not full_name or not username or not email or not password:
            flash('Please fill in all mandatory fields.', 'danger')
            return render_template('auth/register.html', role=role)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', role=role)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html', role=role)

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html', role=role)

        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please log in.', 'danger')
            return render_template('auth/register.html', role=role)

        # Create user
        user = User(
            username=username,
            email=email,
            role=role,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == 'job_seeker':
            headline = request.form.get('headline', '')
            location = request.form.get('location', '')
            skills = request.form.get('skills', '')
            seeker = JobSeeker(
                user_id=user.id,
                full_name=full_name,
                phone=phone,
                headline=headline,
                location=location,
                skills=skills
            )
            db.session.add(seeker)

        elif role == 'employer':
            company_name = request.form.get('company_name', '').strip()
            designation = request.form.get('designation', 'HR Recruiter').strip()
            
            # Find or create company
            company = None
            if company_name:
                company = Company.query.filter_by(name=company_name).first()
                if not company:
                    company = Company(
                        name=company_name,
                        location=request.form.get('company_location', 'Bengaluru, India'),
                        industry=request.form.get('industry', 'Information Technology')
                    )
                    db.session.add(company)
                    db.session.flush()

            employer = Employer(
                user_id=user.id,
                company_id=company.id if company else None,
                full_name=full_name,
                designation=designation,
                phone=phone
            )
            db.session.add(employer)

        db.session.commit()
        login_user(user)
        flash(f'Account created successfully! Welcome to JobConnect, {full_name}.', 'success')
        return redirect_user_dashboard(user)

    return render_template('auth/register.html', role=request.args.get('role', 'job_seeker'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))


def redirect_user_dashboard(user):
    if user.is_admin:
        return redirect(url_for('admin.dashboard'))
    elif user.is_employer:
        return redirect(url_for('employer.dashboard'))
    else:
        return redirect(url_for('seeker.dashboard'))
