import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from database import db
from models import User, JobSeeker, Employer, Company, Job, Application, Category, ContactMessage

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def ensure_admin():
    if not current_user.is_admin:
        flash('Admin privileges required to access this portal.', 'danger')
        return redirect(url_for('main.index'))


@admin_bp.route('/dashboard')
def dashboard():
    total_users = User.query.count()
    total_seekers = JobSeeker.query.count()
    total_employers = Employer.query.count()
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(status='active').count()
    total_applications = Application.query.count()
    total_companies = Company.query.count()
    pending_messages = ContactMessage.query.filter_by(is_resolved=False).count()

    # Recent items
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(6).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(6).all()
    recent_applications = Application.query.order_by(Application.applied_at.desc()).limit(6).all()
    categories = Category.query.all()

    # Analytics for Chart.js
    # 1. Application status distribution
    status_stats = db.session.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
    status_map = {s: 0 for s in ['applied', 'under_review', 'shortlisted', 'interview', 'rejected', 'accepted']}
    for s, count in status_stats:
        status_map[s] = count

    # 2. Category job distribution
    raw_cat_stats = db.session.query(Category.name, func.count(Job.id))\
        .outerjoin(Job, Job.category_id == Category.id)\
        .group_by(Category.name).all()
    cat_stats = [[item[0], int(item[1])] for item in raw_cat_stats]

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_seekers=total_seekers,
        total_employers=total_employers,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_applications=total_applications,
        total_companies=total_companies,
        pending_messages=pending_messages,
        recent_jobs=recent_jobs,
        recent_users=recent_users,
        recent_applications=recent_applications,
        categories=categories,
        status_map=status_map,
        cat_stats=cat_stats
    )


@admin_bp.route('/users')
def manage_users():
    role_filter = request.args.get('role', '')
    query = User.query.order_by(User.created_at.desc())
    if role_filter:
        query = query.filter_by(role=role_filter)
    users = query.all()
    return render_template('admin/users.html', users=users, role_filter=role_filter)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
def toggle_user_status(user_id):
    if user_id == current_user.id:
        flash('You cannot deactivate your own admin account.', 'warning')
        return redirect(url_for('admin.dashboard'))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    state = 'activated' if user.is_active else 'deactivated'
    flash(f'User "{user.username}" has been {state}.', 'info')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/jobs')
def manage_jobs():
    status_filter = request.args.get('status', '')
    query = Job.query.order_by(Job.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    jobs = query.all()
    return render_template('admin/jobs.html', jobs=jobs, status_filter=status_filter)


@admin_bp.route('/jobs/<int:job_id>/status', methods=['POST'])
def update_job_status(job_id):
    job = Job.query.get_or_404(job_id)
    new_status = request.form.get('status', 'active')
    if new_status in {'active', 'closed', 'pending_approval'}:
        job.status = new_status
        db.session.commit()
        flash(f'Job status updated to "{new_status.title()}".', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job posting removed successfully.', 'info')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        action = request.form.get('action', 'create')
        if action == 'create':
            name = request.form.get('name', '').strip()
            slug = request.form.get('slug', '').strip().lower() or name.lower().replace(' ', '-')
            icon = request.form.get('icon', 'fa-briefcase').strip()
            description = request.form.get('description', '').strip()

            if name and not Category.query.filter_by(name=name).first():
                cat = Category(name=name, slug=slug, icon=icon, description=description)
                db.session.add(cat)
                db.session.commit()
                flash(f'Category "{name}" added successfully.', 'success')
            else:
                flash('Category already exists or invalid name.', 'danger')

        elif action == 'delete':
            cid = request.form.get('category_id', type=int)
            cat = Category.query.get(cid)
            if cat:
                db.session.delete(cat)
                db.session.commit()
                flash('Category deleted.', 'info')

        return redirect(url_for('admin.manage_categories'))

    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/messages')
def messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)


@admin_bp.route('/messages/<int:msg_id>/toggle-resolve', methods=['POST'])
def toggle_message_resolve(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_resolved = not msg.is_resolved
    db.session.commit()
    return redirect(url_for('admin.messages'))
