import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import current_user, login_required
from sqlalchemy import or_, desc, asc
from werkzeug.utils import secure_filename
from database import db
from models import Job, Category, Company, Application, SavedJob, JobSeeker, Resume, ContactMessage, Notification

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Metrics for hero counter
    total_jobs = Job.query.filter_by(status='active').count()
    total_companies = Company.query.count()
    total_candidates = JobSeeker.query.count()
    total_applications = Application.query.count()

    # Featured categories with job counts
    categories = Category.query.all()
    categories_with_count = []
    for cat in categories:
        count = Job.query.filter_by(category_id=cat.id, status='active').count()
        categories_with_count.append({
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug,
            'icon': cat.icon,
            'description': cat.description,
            'job_count': count
        })
    categories_with_count.sort(key=lambda x: x['job_count'], reverse=True)

    # Featured / Recent Jobs
    recent_jobs = Job.query.filter_by(status='active').order_by(desc(Job.created_at)).limit(6).all()

    # Top hiring companies
    top_companies = Company.query.limit(8).all()

    # User saved jobs ids for quick heart active status
    saved_job_ids = set()
    if current_user.is_authenticated:
        saved_job_ids = {s.job_id for s in current_user.saved_jobs}

    return render_template(
        'index.html',
        total_jobs=total_jobs,
        total_companies=total_companies,
        total_candidates=total_candidates,
        total_applications=total_applications,
        categories=categories_with_count[:8],
        recent_jobs=recent_jobs,
        top_companies=top_companies,
        saved_job_ids=saved_job_ids
    )


@main_bp.route('/jobs')
def search():
    q = request.args.get('q', '').strip()
    location = request.args.get('location', '').strip()
    category_slug = request.args.get('category', '').strip()
    job_type = request.args.get('job_type', '').strip()
    work_mode = request.args.get('work_mode', '').strip()
    experience = request.args.get('experience', '').strip()
    min_sal_val = request.args.get('min_salary', type=int)
    sort_by = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Base query for active jobs
    query = Job.query.filter(Job.status == 'active')

    # Keyword filter: title, description, skills_required, company name
    if q:
        query = query.join(Company).filter(
            or_(
                Job.title.ilike(f'%{q}%'),
                Job.skills_required.ilike(f'%{q}%'),
                Job.description.ilike(f'%{q}%'),
                Company.name.ilike(f'%{q}%')
            )
        )

    # Location filter
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))

    # Category filter
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter(Job.category_id == cat.id)

    # Job Type filter
    if job_type:
        query = query.filter(Job.job_type == job_type)

    # Work Mode filter
    if work_mode:
        query = query.filter(Job.work_mode == work_mode)

    # Experience level filter
    if experience:
        query = query.filter(Job.experience_level == experience)

    # Minimum salary filter
    if min_sal_val and min_sal_val > 0:
        query = query.filter(Job.max_salary >= min_sal_val)

    # Sorting
    if sort_by == 'salary_high':
        query = query.order_by(desc(Job.max_salary))
    elif sort_by == 'salary_low':
        query = query.order_by(asc(Job.min_salary))
    elif sort_by == 'oldest':
        query = query.order_by(asc(Job.created_at))
    else:  # 'newest' default
        query = query.order_by(desc(Job.created_at))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    jobs = pagination.items

    # Saved jobs IDs for authenticated users
    saved_job_ids = set()
    if current_user.is_authenticated:
        saved_job_ids = {s.job_id for s in current_user.saved_jobs}

    categories = Category.query.all()
    all_locations = ["Bengaluru", "Hyderabad", "Pune", "Mumbai", "Gurgaon", "Noida", "Remote"]

    return render_template(
        'jobs/search.html',
        jobs=jobs,
        pagination=pagination,
        q=q,
        location=location,
        selected_category=category_slug,
        job_type=job_type,
        work_mode=work_mode,
        experience=experience,
        min_salary=min_sal_val or 0,
        sort_by=sort_by,
        categories=categories,
        locations=all_locations,
        saved_job_ids=saved_job_ids,
        total_results=pagination.total
    )


@main_bp.route('/jobs/<int:job_id>')
def job_details(job_id):
    job = Job.query.get_or_404(job_id)

    # Increment view count
    job.views_count += 1
    db.session.commit()

    # Check if current user has already applied or saved
    has_applied = False
    existing_application = None
    is_saved = False

    if current_user.is_authenticated:
        if current_user.is_seeker and current_user.seeker_profile:
            existing_application = Application.query.filter_by(
                job_id=job.id,
                seeker_id=current_user.seeker_profile.id
            ).first()
            has_applied = bool(existing_application)
        
        is_saved = bool(SavedJob.query.filter_by(user_id=current_user.id, job_id=job.id).first())

    # Fetch similar jobs (same category or company)
    similar_jobs = Job.query.filter(
        Job.id != job.id,
        Job.status == 'active',
        or_(Job.category_id == job.category_id, Job.location == job.location)
    ).limit(3).all()

    # User resumes for quick apply modal
    user_resumes = []
    if current_user.is_authenticated and current_user.is_seeker and current_user.seeker_profile:
        user_resumes = current_user.seeker_profile.resumes.order_by(desc(Resume.is_primary)).all()

    return render_template(
        'jobs/details.html',
        job=job,
        has_applied=has_applied,
        application=existing_application,
        is_saved=is_saved,
        similar_jobs=similar_jobs,
        user_resumes=user_resumes
    )


@main_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    if not current_user.is_seeker:
        flash('Only Job Seekers can apply for jobs.', 'warning')
        return redirect(url_for('main.job_details', job_id=job_id))

    job = Job.query.get_or_404(job_id)
    seeker = current_user.seeker_profile

    if not seeker:
        flash('Please complete your profile before applying.', 'warning')
        return redirect(url_for('seeker.profile'))

    # Check for duplicate application
    existing = Application.query.filter_by(job_id=job.id, seeker_id=seeker.id).first()
    if existing:
        flash('You have already submitted an application for this position.', 'info')
        return redirect(url_for('main.job_details', job_id=job.id))

    resume_id = request.form.get('resume_id', type=int)
    cover_letter = request.form.get('cover_letter', '').strip()

    # Check if a new file was uploaded directly in the apply modal
    uploaded_file = request.files.get('resume_file')
    if uploaded_file and uploaded_file.filename:
        filename = secure_filename(uploaded_file.filename)
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in current_app.config['ALLOWED_EXTENSIONS']:
            flash('Invalid file format. Please upload PDF or DOCX.', 'danger')
            return redirect(url_for('main.job_details', job_id=job.id))

        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        stored_name = f"resume_{seeker.id}_{timestamp}_{filename}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_name)
        uploaded_file.save(save_path)
        file_size = os.path.getsize(save_path)

        new_res = Resume(
            seeker_id=seeker.id,
            original_filename=filename,
            stored_filename=stored_name,
            file_path=f"uploads/resumes/{stored_name}",
            file_size=file_size,
            is_primary=False
        )
        db.session.add(new_res)
        db.session.flush()
        resume_id = new_res.id

    # If still no resume, pick seeker's primary resume
    if not resume_id and seeker.primary_resume:
        resume_id = seeker.primary_resume.id

    application = Application(
        job_id=job.id,
        seeker_id=seeker.id,
        resume_id=resume_id,
        cover_letter=cover_letter,
        status='applied'
    )
    db.session.add(application)

    # Notify employer
    employer_user = job.employer.user
    notification = Notification(
        user_id=employer_user.id,
        title="New Application Received",
        message=f"{seeker.full_name} has applied for {job.title}",
        link=url_for('employer.view_applicants', job_id=job.id)
    )
    db.session.add(notification)

    db.session.commit()
    flash('Congratulations! Your application has been submitted successfully.', 'success')
    return redirect(url_for('seeker.applications'))


@main_bp.route('/jobs/<int:job_id>/save', methods=['POST'])
@login_required
def toggle_save_job(job_id):
    job = Job.query.get_or_404(job_id)
    saved = SavedJob.query.filter_by(user_id=current_user.id, job_id=job.id).first()

    if saved:
        db.session.delete(saved)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'unsaved', 'message': 'Job removed from saved list.'})
        flash('Job removed from your saved list.', 'info')
    else:
        new_save = SavedJob(user_id=current_user.id, job_id=job.id)
        db.session.add(new_save)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'saved', 'message': 'Job saved successfully!'})
        flash('Job added to your saved list!', 'success')

    return redirect(request.referrer or url_for('main.job_details', job_id=job.id))


@main_bp.route('/companies/<int:company_id>')
def company_profile(company_id):
    company = Company.query.get_or_404(company_id)
    active_jobs = Job.query.filter_by(company_id=company.id, status='active').all()
    return render_template('employer/company_profile.html', company=company, active_jobs=active_jobs, is_public=True)


@main_bp.route('/about')
def about():
    total_jobs = Job.query.count()
    total_companies = Company.query.count()
    total_seekers = JobSeeker.query.count()
    return render_template(
        'pages/about.html',
        total_jobs=total_jobs,
        total_companies=total_companies,
        total_seekers=total_seekers
    )


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not subject or not message:
            flash('All fields are required. Please check your form.', 'danger')
            return render_template('pages/contact.html')

        msg = ContactMessage(name=name, email=email, subject=subject, message=message)
        db.session.add(msg)
        db.session.commit()

        flash('Thank you for reaching out! Our team will respond to your inquiry shortly.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('pages/contact.html')


@main_bp.route('/notifications/mark-read/<int:nid>', methods=['POST'])
@login_required
def mark_notification_read(nid):
    notif = Notification.query.filter_by(id=nid, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True})
