import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from database import db
from models import JobSeeker, Resume, Application, SavedJob, Job, Category

seeker_bp = Blueprint('seeker', __name__, url_prefix='/seeker')

@seeker_bp.before_request
@login_required
def ensure_seeker():
    if not current_user.is_seeker and not current_user.is_admin:
        flash('Access restricted to Job Seekers.', 'warning')
        return redirect(url_for('main.index'))


@seeker_bp.route('/dashboard')
def dashboard():
    seeker = current_user.seeker_profile
    if not seeker:
        # Auto-create profile if missing
        seeker = JobSeeker(user_id=current_user.id, full_name=current_user.username)
        db.session.add(seeker)
        db.session.commit()

    # Application metrics
    total_applied = seeker.applications.count()
    under_review = seeker.applications.filter_by(status='under_review').count()
    shortlisted = seeker.applications.filter_by(status='shortlisted').count()
    interviews = seeker.applications.filter_by(status='interview').count()
    rejected = seeker.applications.filter_by(status='rejected').count()
    saved_count = current_user.saved_jobs.count()

    # Recent applications
    recent_applications = seeker.applications.order_by(Application.applied_at.desc()).limit(5).all()

    # Recommended Jobs based on user skills
    user_skills = seeker.skills_list
    recommended_jobs = []
    if user_skills:
        # Match jobs having any user skill
        active_jobs = Job.query.filter_by(status='active').all()
        scored_jobs = []
        applied_job_ids = {a.job_id for a in seeker.applications}

        for j in active_jobs:
            if j.id in applied_job_ids:
                continue
            job_skills = [s.lower() for s in j.skills_list]
            matches = sum(1 for us in user_skills if any(us.lower() in js for js in job_skills))
            if matches > 0:
                scored_jobs.append((matches, j))

        scored_jobs.sort(key=lambda x: x[0], reverse=True)
        recommended_jobs = [j for _, j in scored_jobs[:4]]

    if not recommended_jobs:
        # Fallback to recent jobs
        recommended_jobs = Job.query.filter_by(status='active').order_by(Job.created_at.desc()).limit(4).all()

    return render_template(
        'seeker/dashboard.html',
        seeker=seeker,
        total_applied=total_applied,
        under_review=under_review,
        shortlisted=shortlisted,
        interviews=interviews,
        rejected=rejected,
        saved_count=saved_count,
        recent_applications=recent_applications,
        recommended_jobs=recommended_jobs
    )


@seeker_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    seeker = current_user.seeker_profile
    if not seeker:
        seeker = JobSeeker(user_id=current_user.id, full_name=current_user.username)
        db.session.add(seeker)
        db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action', 'update_basic')

        if action == 'update_basic':
            seeker.full_name = request.form.get('full_name', '').strip()
            seeker.headline = request.form.get('headline', '').strip()
            seeker.phone = request.form.get('phone', '').strip()
            seeker.location = request.form.get('location', '').strip()
            seeker.bio = request.form.get('bio', '').strip()
            seeker.skills = request.form.get('skills', '').strip()
            seeker.experience_years = float(request.form.get('experience_years') or 0)
            seeker.current_company = request.form.get('current_company', '').strip()
            seeker.current_salary = request.form.get('current_salary', '').strip()
            seeker.expected_salary = request.form.get('expected_salary', '').strip()
            seeker.github_url = request.form.get('github_url', '').strip()
            seeker.linkedin_url = request.form.get('linkedin_url', '').strip()
            seeker.portfolio_url = request.form.get('portfolio_url', '').strip()
            flash('Profile information updated successfully!', 'success')

        elif action == 'add_experience':
            curr_exp = seeker.parsed_experience
            new_item = {
                'title': request.form.get('exp_title', '').strip(),
                'company': request.form.get('exp_company', '').strip(),
                'duration': request.form.get('exp_duration', '').strip(),
                'description': request.form.get('exp_description', '').strip()
            }
            if new_item['title'] and new_item['company']:
                curr_exp.insert(0, new_item)
                seeker.experience_data = json.dumps(curr_exp)
                flash('Experience added successfully!', 'success')

        elif action == 'delete_experience':
            idx = int(request.form.get('item_index', -1))
            curr_exp = seeker.parsed_experience
            if 0 <= idx < len(curr_exp):
                curr_exp.pop(idx)
                seeker.experience_data = json.dumps(curr_exp)
                flash('Experience entry deleted.', 'info')

        elif action == 'add_education':
            curr_edu = seeker.parsed_education
            new_item = {
                'degree': request.form.get('edu_degree', '').strip(),
                'institution': request.form.get('edu_institution', '').strip(),
                'year': request.form.get('edu_year', '').strip(),
                'score': request.form.get('edu_score', '').strip()
            }
            if new_item['degree'] and new_item['institution']:
                curr_edu.insert(0, new_item)
                seeker.education_data = json.dumps(curr_edu)
                flash('Education added successfully!', 'success')

        elif action == 'delete_education':
            idx = int(request.form.get('item_index', -1))
            curr_edu = seeker.parsed_education
            if 0 <= idx < len(curr_edu):
                curr_edu.pop(idx)
                seeker.education_data = json.dumps(curr_edu)
                flash('Education entry deleted.', 'info')

        elif action == 'add_project':
            curr_proj = seeker.parsed_projects
            new_item = {
                'title': request.form.get('proj_title', '').strip(),
                'tech': request.form.get('proj_tech', '').strip(),
                'link': request.form.get('proj_link', '').strip(),
                'summary': request.form.get('proj_summary', '').strip()
            }
            if new_item['title']:
                curr_proj.insert(0, new_item)
                seeker.projects_data = json.dumps(curr_proj)
                flash('Project added successfully!', 'success')

        elif action == 'delete_project':
            idx = int(request.form.get('item_index', -1))
            curr_proj = seeker.parsed_projects
            if 0 <= idx < len(curr_proj):
                curr_proj.pop(idx)
                seeker.projects_data = json.dumps(curr_proj)
                flash('Project entry deleted.', 'info')

        db.session.commit()
        return redirect(url_for('seeker.profile'))

    return render_template('seeker/profile.html', seeker=seeker)


@seeker_bp.route('/resume', methods=['GET', 'POST'])
def resume_manager():
    seeker = current_user.seeker_profile
    if not seeker:
        seeker = JobSeeker(user_id=current_user.id, full_name=current_user.username)
        db.session.add(seeker)
        db.session.commit()

    if request.method == 'POST':
        if 'resume_file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('seeker.resume_manager'))

        file = request.files['resume_file']
        if file.filename == '':
            flash('Please choose a file to upload.', 'danger')
            return redirect(url_for('seeker.resume_manager'))

        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in current_app.config['ALLOWED_EXTENSIONS']:
            flash('Only PDF, DOC, and DOCX files are permitted.', 'danger')
            return redirect(url_for('seeker.resume_manager'))

        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        stored_name = f"resume_{seeker.id}_{timestamp}_{filename}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_name)
        file.save(save_path)
        file_size = os.path.getsize(save_path)

        # If it's the first resume, make it primary
        is_first = seeker.resumes.count() == 0

        # Unmark existing primary if requested or if first
        make_primary = bool(request.form.get('is_primary')) or is_first
        if make_primary:
            Resume.query.filter_by(seeker_id=seeker.id).update({'is_primary': False})

        new_resume = Resume(
            seeker_id=seeker.id,
            original_filename=filename,
            stored_filename=stored_name,
            file_path=f"uploads/resumes/{stored_name}",
            file_size=file_size,
            is_primary=make_primary
        )
        db.session.add(new_resume)
        db.session.commit()

        flash(f'Resume "{filename}" uploaded successfully!', 'success')
        return redirect(url_for('seeker.resume_manager'))

    resumes = seeker.resumes.order_by(Resume.uploaded_at.desc()).all()
    return render_template('seeker/resume.html', seeker=seeker, resumes=resumes)


@seeker_bp.route('/resume/<int:resume_id>/set-primary', methods=['POST'])
def set_primary_resume(resume_id):
    seeker = current_user.seeker_profile
    res = Resume.query.filter_by(id=resume_id, seeker_id=seeker.id).first_or_404()
    Resume.query.filter_by(seeker_id=seeker.id).update({'is_primary': False})
    res.is_primary = True
    db.session.commit()
    flash(f'"{res.original_filename}" is now set as your primary resume.', 'success')
    return redirect(url_for('seeker.resume_manager'))


@seeker_bp.route('/resume/<int:resume_id>/delete', methods=['POST'])
def delete_resume(resume_id):
    seeker = current_user.seeker_profile
    res = Resume.query.filter_by(id=resume_id, seeker_id=seeker.id).first_or_404()
    
    # Try deleting physical file
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], res.stored_filename)
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except:
            pass

    db.session.delete(res)
    db.session.commit()
    flash('Resume removed successfully.', 'info')
    return redirect(url_for('seeker.resume_manager'))


@seeker_bp.route('/resume/<int:resume_id>/download')
def download_resume(resume_id):
    res = Resume.query.get_or_404(resume_id)
    # Check permissions: owner, or employer who received application, or admin
    is_owner = current_user.is_authenticated and current_user.is_seeker and res.seeker_id == current_user.seeker_profile.id
    is_admin = current_user.is_authenticated and current_user.is_admin
    is_authorized_employer = False
    if current_user.is_authenticated and current_user.is_employer and current_user.employer_profile:
        # Check if seeker applied to one of the employer's jobs
        emp_job_ids = [j.id for j in current_user.employer_profile.jobs]
        is_authorized_employer = Application.query.filter(
            Application.resume_id == res.id,
            Application.job_id.in_(emp_job_ids)
        ).first() is not None

    if not (is_owner or is_admin or is_authorized_employer):
        abort(403)

    folder = current_app.config['UPLOAD_FOLDER']
    full_path = os.path.join(folder, res.stored_filename)
    if not os.path.exists(full_path):
        flash('File is no longer available on server.', 'danger')
        return redirect(request.referrer or url_for('seeker.resume_manager'))

    return send_from_directory(
        directory=folder,
        path=res.stored_filename,
        as_attachment=True,
        download_name=res.original_filename
    )


@seeker_bp.route('/applications')
def applications():
    seeker = current_user.seeker_profile
    if not seeker:
        return redirect(url_for('seeker.profile'))

    status_filter = request.args.get('status', '')
    query = seeker.applications.order_by(Application.applied_at.desc())

    if status_filter:
        query = query.filter_by(status=status_filter)

    my_apps = query.all()
    return render_template('seeker/applications.html', applications=my_apps, current_filter=status_filter)


@seeker_bp.route('/applications/<int:app_id>/withdraw', methods=['POST'])
def withdraw_application(app_id):
    seeker = current_user.seeker_profile
    app = Application.query.filter_by(id=app_id, seeker_id=seeker.id).first_or_404()
    db.session.delete(app)
    db.session.commit()
    flash('Your application has been withdrawn.', 'info')
    return redirect(url_for('seeker.applications'))


@seeker_bp.route('/saved-jobs')
def saved_jobs():
    saved_items = current_user.saved_jobs.order_by(SavedJob.created_at.desc()).all()
    return render_template('seeker/saved_jobs.html', saved_items=saved_items)
