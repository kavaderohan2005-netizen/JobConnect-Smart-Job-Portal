import json
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='job_seeker')  # 'job_seeker', 'employer', 'admin'
    is_active = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    seeker_profile = db.relationship('JobSeeker', backref='user', uselist=False, cascade='all, delete-orphan')
    employer_profile = db.relationship('Employer', backref='user', uselist=False, cascade='all, delete-orphan')
    saved_jobs = db.relationship('SavedJob', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_seeker(self):
        return self.role == 'job_seeker'

    @property
    def is_employer(self):
        return self.role == 'employer'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def display_name(self):
        if self.is_seeker and self.seeker_profile:
            return self.seeker_profile.full_name or self.username
        if self.is_employer and self.employer_profile:
            return self.employer_profile.full_name or self.username
        return self.username

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    logo = db.Column(db.String(255), default='default_company.png')
    website = db.Column(db.String(200))
    location = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    description = db.Column(db.Text)
    founded_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    employers = db.relationship('Employer', backref='company', lazy='dynamic')
    jobs = db.relationship('Job', backref='company', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Company {self.name}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(80), default='fa-briefcase')
    description = db.Column(db.Text)

    # Relationships
    jobs = db.relationship('Job', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class JobSeeker(db.Model):
    __tablename__ = 'job_seekers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    headline = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    github_url = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(200))
    portfolio_url = db.Column(db.String(200))
    skills = db.Column(db.Text)  # Comma-separated or string list
    experience_years = db.Column(db.Float, default=0.0)
    current_company = db.Column(db.String(120))
    current_salary = db.Column(db.String(50))
    expected_salary = db.Column(db.String(50))
    education_data = db.Column(db.Text, default='[]')   # JSON array
    experience_data = db.Column(db.Text, default='[]')  # JSON array
    projects_data = db.Column(db.Text, default='[]')    # JSON array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resumes = db.relationship('Resume', backref='seeker', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='seeker', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    @property
    def parsed_education(self):
        try:
            return json.loads(self.education_data or '[]')
        except:
            return []

    @property
    def parsed_experience(self):
        try:
            return json.loads(self.experience_data or '[]')
        except:
            return []

    @property
    def parsed_projects(self):
        try:
            return json.loads(self.projects_data or '[]')
        except:
            return []

    @property
    def profile_completion(self):
        score = 0
        if self.full_name: score += 15
        if self.headline: score += 10
        if self.phone: score += 10
        if self.location: score += 10
        if self.bio: score += 10
        if self.skills: score += 15
        if self.parsed_experience: score += 15
        if self.parsed_education: score += 10
        if self.resumes.first(): score += 15
        return min(score, 100)

    @property
    def primary_resume(self):
        return self.resumes.filter_by(is_primary=True).first() or self.resumes.first()


class Employer(db.Model):
    __tablename__ = 'employers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True)
    full_name = db.Column(db.String(120), nullable=False)
    designation = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    jobs = db.relationship('Job', backref='employer', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Employer {self.full_name}>'


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)
    job_type = db.Column(db.String(50), default='Full-time')  # Full-time, Part-time, Contract, Internship, Remote
    work_mode = db.Column(db.String(50), default='Hybrid')    # Remote, Hybrid, Onsite
    experience_level = db.Column(db.String(50), default='Mid Level') # Entry Level, Mid Level, Senior Level, Lead
    min_salary = db.Column(db.Integer, default=0) # Annual salary in INR
    max_salary = db.Column(db.Integer, default=0) # Annual salary in INR
    location = db.Column(db.String(100), nullable=False, index=True)
    skills_required = db.Column(db.Text) # Comma-separated
    openings = db.Column(db.Integer, default=1)
    status = db.Column(db.String(30), default='active') # 'active', 'closed', 'pending_approval'
    views_count = db.Column(db.Integer, default=0)
    deadline = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    saved_by = db.relationship('SavedJob', backref='job', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def skills_list(self):
        if not self.skills_required:
            return []
        return [s.strip() for s in self.skills_required.split(',') if s.strip()]

    @property
    def formatted_salary(self):
        if not self.min_salary and not self.max_salary:
            return 'Not Disclosed'
        
        def format_inr(val):
            if val >= 100000:
                lpa = val / 100000.0
                return f"₹{lpa:g} LPA"
            return f"₹{val:,}"

        if self.min_salary and self.max_salary:
            if self.min_salary == self.max_salary:
                return format_inr(self.min_salary)
            min_lpa = self.min_salary / 100000.0
            max_lpa = self.max_salary / 100000.0
            return f"₹{min_lpa:g} - {max_lpa:g} LPA"
        elif self.min_salary:
            return f"From {format_inr(self.min_salary)}"
        else:
            return f"Up to {format_inr(self.max_salary)}"

    @property
    def applications_count(self):
        return self.applications.count()

    def __repr__(self):
        return f'<Job {self.title}>'


class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    seeker_id = db.Column(db.Integer, db.ForeignKey('job_seekers.id', ondelete='CASCADE'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    file_size = db.Column(db.Integer, default=0) # in bytes
    is_primary = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='resume', lazy='dynamic')

    @property
    def formatted_size(self):
        kb = self.file_size / 1024.0
        if kb >= 1024:
            return f"{kb/1024.0:.1f} MB"
        return f"{kb:.0f} KB"

    def __repr__(self):
        return f'<Resume {self.original_filename}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    seeker_id = db.Column(db.Integer, db.ForeignKey('job_seekers.id', ondelete='CASCADE'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(30), default='applied') # 'applied', 'under_review', 'shortlisted', 'interview', 'rejected', 'accepted'
    recruiter_notes = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def status_badge_class(self):
        mapping = {
            'applied': 'bg-primary text-white',
            'under_review': 'bg-warning text-dark',
            'shortlisted': 'bg-info text-white',
            'interview': 'bg-purple text-white',
            'accepted': 'bg-success text-white',
            'rejected': 'bg-danger text-white'
        }
        return mapping.get(self.status, 'bg-secondary text-white')

    @property
    def status_label(self):
        labels = {
            'applied': 'Applied',
            'under_review': 'Under Review',
            'shortlisted': 'Shortlisted',
            'interview': 'Interview Scheduled',
            'accepted': 'Offer Extended / Accepted',
            'rejected': 'Rejected'
        }
        return labels.get(self.status, self.status.replace('_', ' ').title())

    def __repr__(self):
        return f'<Application Job:{self.job_id} Seeker:{self.seeker_id}>'


class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='uq_user_saved_job'),
    )


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
