import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, abort
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from database import db
from models import Employer, Company, Job, Category, Application, Notification, Resume

employer_bp = Blueprint('employer', __name__, url_prefix='/employer')

@employer_bp.before_request
@login_required
def ensure_employer():
    if not current_user.is_employer and not current_user.is_admin:
        flash('Access restricted to Employers and Recruiters.', 'warning')
        return redirect(url_for('main.index'))


@employer_bp.route('/dashboard')
def dashboard():
    emp = current_user.employer_profile
    if not emp:
        # Auto-create profile if missing
        emp = Employer(user_id=current_user.id, full_name=current_user.username)
        db.session.add(emp)
        db.session.commit()

    # Job metrics
    jobs = emp.jobs.all()
    job_ids = [j.id for j in jobs]

    total_jobs = len(jobs)
    active_jobs = sum(1 for j in jobs if j.status == 'active')
    closed_jobs = sum(1 for j in jobs if j.status == 'closed')

    # Application metrics
    if job_ids:
        all_apps = Application.query.filter(Application.job_id.in_(job_ids))
        total_applicants = all_apps.count()
        shortlisted_count = all_apps.filter_by(status='shortlisted').count()
        interview_count = all_apps.filter_by(status='interview').count()
        recent_applicants = all_apps.order_by(Application.applied_at.desc()).limit(6).all()
        
        # Monthly application chart data (last 6 months)
        status_counts = {
            'Applied': all_apps.filter_by(status='applied').count(),
            'Under Review': all_apps.filter_by(status='under_review').count(),
            'Shortlisted': shortlisted_count,
            'Interview': interview_count,
            'Accepted': all_apps.filter_by(status='accepted').count(),
            'Rejected': all_apps.filter_by(status='rejected').count(),
        }
    else:
        total_applicants = 0
        shortlisted_count = 0
        interview_count = 0
        recent_applicants = []
        status_counts = {'Applied': 0, 'Under Review': 0, 'Shortlisted': 0, 'Interview': 0, 'Accepted': 0, 'Rejected': 0}

    return render_template(
        'employer/dashboard.html',
        employer=emp,
        jobs=jobs[:5],
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        closed_jobs=closed_jobs,
        total_applicants=total_applicants,
        shortlisted_count=shortlisted_count,
        interview_count=interview_count,
        recent_applicants=recent_applicants,
        status_counts=status_counts
    )


@employer_bp.route('/jobs')
def my_jobs():
    emp = current_user.employer_profile
    if not emp:
        return redirect(url_for('employer.dashboard'))

    jobs = emp.jobs.order_by(Job.created_at.desc()).all()
    return render_template('jobs/my_jobs.html', jobs=jobs)


@employer_bp.route('/post-job', methods=['GET', 'POST'])
def post_job():
    emp = current_user.employer_profile
    if not emp:
        return redirect(url_for('employer.dashboard'))

    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id', type=int)
        job_type = request.form.get('job_type', 'Full-time')
        work_mode = request.form.get('work_mode', 'Hybrid')
        experience_level = request.form.get('experience_level', 'Mid Level')
        min_salary = request.form.get('min_salary', type=int) or 0
        max_salary = request.form.get('max_salary', type=int) or 0
        location = request.form.get('location', '').strip()
        skills_required = request.form.get('skills_required', '').strip()
        openings = request.form.get('openings', type=int) or 1
        deadline_str = request.form.get('deadline', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        benefits = request.form.get('benefits', '').strip()

        # Validation
        if not title or not description or not location:
            flash('Please fill in Job Title, Description, and Location.', 'danger')
            return render_template('jobs/post_job.html', categories=categories, job=None)

        deadline_val = None
        if deadline_str:
            try:
                deadline_val = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Company check
        company_id = emp.company_id
        if not company_id:
            # Create a company or use default
            company = Company(name=f"{emp.full_name}'s Enterprise", location=location)
            db.session.add(company)
            db.session.flush()
            emp.company_id = company.id
            company_id = company.id

        job = Job(
            employer_id=emp.id,
            company_id=company_id,
            category_id=category_id,
            title=title,
            job_type=job_type,
            work_mode=work_mode,
            experience_level=experience_level,
            min_salary=min_salary,
            max_salary=max_salary,
            location=location,
            skills_required=skills_required,
            openings=openings,
            deadline=deadline_val,
            description=description,
            requirements=requirements,
            benefits=benefits,
            status='active'
        )
        db.session.add(job)
        db.session.commit()

        flash(f'Job opening "{title}" has been successfully posted!', 'success')
        return redirect(url_for('employer.my_jobs'))

    return render_template('jobs/post_job.html', categories=categories, job=None)


@employer_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    emp = current_user.employer_profile
    job = Job.query.filter_by(id=job_id, employer_id=emp.id).first_or_404()
    categories = Category.query.all()

    if request.method == 'POST':
        job.title = request.form.get('title', '').strip()
        job.category_id = request.form.get('category_id', type=int)
        job.job_type = request.form.get('job_type', 'Full-time')
        job.work_mode = request.form.get('work_mode', 'Hybrid')
        job.experience_level = request.form.get('experience_level', 'Mid Level')
        job.min_salary = request.form.get('min_salary', type=int) or 0
        job.max_salary = request.form.get('max_salary', type=int) or 0
        job.location = request.form.get('location', '').strip()
        job.skills_required = request.form.get('skills_required', '').strip()
        job.openings = request.form.get('openings', type=int) or 1
        job.status = request.form.get('status', 'active')
        
        deadline_str = request.form.get('deadline', '').strip()
        if deadline_str:
            try:
                job.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        job.description = request.form.get('description', '').strip()
        job.requirements = request.form.get('requirements', '').strip()
        job.benefits = request.form.get('benefits', '').strip()

        db.session.commit()
        flash(f'Job opening "{job.title}" updated successfully!', 'success')
        return redirect(url_for('employer.my_jobs'))

    return render_template('jobs/post_job.html', categories=categories, job=job)


@employer_bp.route('/jobs/<int:job_id>/toggle-status', methods=['POST'])
def toggle_status(job_id):
    emp = current_user.employer_profile
    job = Job.query.filter_by(id=job_id, employer_id=emp.id).first_or_404()
    job.status = 'closed' if job.status == 'active' else 'active'
    db.session.commit()
    flash(f'Job status changed to {job.status.title()}.', 'info')
    return redirect(url_for('employer.my_jobs'))


@employer_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    emp = current_user.employer_profile
    job = Job.query.filter_by(id=job_id, employer_id=emp.id).first_or_404()
    title = job.title
    db.session.delete(job)
    db.session.commit()
    flash(f'Job posting "{title}" deleted permanently.', 'info')
    return redirect(url_for('employer.my_jobs'))


@employer_bp.route('/applications')
def all_applicants():
    emp = current_user.employer_profile
    jobs = emp.jobs.all()
    job_ids = [j.id for j in jobs]

    selected_job_id = request.args.get('job_id', type=int)
    status_filter = request.args.get('status', '')

    query = Application.query.filter(Application.job_id.in_(job_ids))
    if selected_job_id:
        query = query.filter_by(job_id=selected_job_id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    applicants = query.order_by(Application.applied_at.desc()).all()
    return render_template(
        'employer/applicants.html',
        applicants=applicants,
        jobs=jobs,
        selected_job_id=selected_job_id,
        current_status=status_filter
    )


@employer_bp.route('/jobs/<int:job_id>/applicants')
def view_applicants(job_id):
    emp = current_user.employer_profile
    job = Job.query.filter_by(id=job_id, employer_id=emp.id).first_or_404()
    status_filter = request.args.get('status', '')

    query = job.applications
    if status_filter:
        query = query.filter_by(status=status_filter)

    applicants = query.order_by(Application.applied_at.desc()).all()
    return render_template(
        'employer/applicants.html',
        applicants=applicants,
        jobs=[job],
        selected_job_id=job.id,
        current_status=status_filter,
        single_job=job
    )


@employer_bp.route('/applications/<int:app_id>/status', methods=['POST'])
def update_application_status(app_id):
    emp = current_user.employer_profile
    app = Application.query.get_or_404(app_id)

    # Permission check
    if app.job.employer_id != emp.id and not current_user.is_admin:
        abort(403)

    new_status = request.form.get('status')
    notes = request.form.get('recruiter_notes', '').strip()

    valid_statuses = {'applied', 'under_review', 'shortlisted', 'interview', 'rejected', 'accepted'}
    if new_status in valid_statuses:
        app.status = new_status
        if notes:
            app.recruiter_notes = notes

        # Notify seeker
        notif = Notification(
            user_id=app.seeker.user_id,
            title="Application Status Updated",
            message=f"Your application status for {app.job.title} has been updated to: {app.status_label}.",
            link=url_for('seeker.applications')
        )
        db.session.add(notif)
        db.session.commit()
        flash(f'Candidate status updated to "{app.status_label}".', 'success')
    else:
        flash('Invalid status provided.', 'danger')

    return redirect(request.referrer or url_for('employer.all_applicants'))


@employer_bp.route('/company-profile', methods=['GET', 'POST'])
def company_profile():
    emp = current_user.employer_profile
    company = emp.company

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        website = request.form.get('website', '').strip()
        location = request.form.get('location', '').strip()
        industry = request.form.get('industry', '').strip()
        company_size = request.form.get('company_size', '').strip()
        founded_year = request.form.get('founded_year', type=int)
        description = request.form.get('description', '').strip()

        if not company:
            company = Company(name=name)
            db.session.add(company)
            db.session.flush()
            emp.company_id = company.id

        company.name = name
        company.website = website
        company.location = location
        company.industry = industry
        company.company_size = company_size
        company.founded_year = founded_year
        company.description = description

        db.session.commit()
        flash('Company details updated successfully!', 'success')
        return redirect(url_for('employer.company_profile'))

    return render_template('employer/company_profile.html', company=company, is_public=False)
