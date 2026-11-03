import unittest
from app import create_app
from database import db
from models import User, Job, Application, Category, Company, JobSeeker, Employer

class JobConnectTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def login(self, email, password):
        return self.client.post('/login', data={
            'identifier': email,
            'password': password
        }, follow_redirects=True)

    def test_01_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'JobConnect', response.data)
        self.assertIn(b'Active Job Openings', response.data)
        print(" [PASS] Home Page rendered successfully.")

    def test_02_job_search_and_filters(self):
        # All jobs
        resp = self.client.get('/jobs')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Explore Tech Opportunities', resp.data)

        # Keyword filter for 'Python'
        resp_py = self.client.get('/jobs?q=Python')
        self.assertEqual(resp_py.status_code, 200)
        self.assertIn(b'Python', resp_py.data)

        # Category filter
        resp_cat = self.client.get('/jobs?category=data-science-ai')
        self.assertEqual(resp_cat.status_code, 200)
        print(" [PASS] Job Search and Multi-Faceted Filters work correctly.")

    def test_03_job_details_page(self):
        job = Job.query.first()
        self.assertIsNotNone(job)
        resp = self.client.get(f'/jobs/{job.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(job.company.name.encode('utf-8'), resp.data)
        self.assertIn(b'Offered CTC', resp.data)
        print(f" [PASS] Job Details page for #{job.id} ('{job.title}') loaded.")

    def test_04_seeker_workflow(self):
        # 1. Login as seeker
        login_resp = self.login('seeker@jobconnect.com', 'seeker123')
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b'Aarav Sharma', login_resp.data)

        # 2. View Dashboard
        dash_resp = self.client.get('/seeker/dashboard')
        self.assertEqual(dash_resp.status_code, 200)
        self.assertIn(b'Profile Health', dash_resp.data)

        # 3. View Profile
        prof_resp = self.client.get('/seeker/profile')
        self.assertEqual(prof_resp.status_code, 200)
        self.assertIn(b'Professional Profile', prof_resp.data)

        # 4. View Resumes
        res_resp = self.client.get('/seeker/resume')
        self.assertEqual(res_resp.status_code, 200)
        self.assertIn(b'Resume Management', res_resp.data)

        # 5. View Applications
        apps_resp = self.client.get('/seeker/applications')
        self.assertEqual(apps_resp.status_code, 200)
        self.assertIn(b'My Job Applications', apps_resp.data)

        # 6. View Saved Jobs
        saved_resp = self.client.get('/seeker/saved-jobs')
        self.assertEqual(saved_resp.status_code, 200)
        self.assertIn(b'Bookmarked Jobs', saved_resp.data)

        # 7. Logout
        self.client.get('/logout')
        print(" [PASS] Job Seeker authentication and all dashboard pages verified.")

    def test_05_employer_workflow(self):
        # 1. Login as employer
        login_resp = self.login('employer@jobconnect.com', 'employer123')
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b'Priya Nair', login_resp.data)

        # 2. Employer Dashboard
        dash_resp = self.client.get('/employer/dashboard')
        self.assertEqual(dash_resp.status_code, 200)
        self.assertIn(b'Recruiter Dashboard', dash_resp.data)

        # 3. Post a Job Page (GET)
        post_resp = self.client.get('/employer/post-job')
        self.assertEqual(post_resp.status_code, 200)
        self.assertIn(b'Post a New Job Opening', post_resp.data)

        # 4. My Jobs list
        my_jobs_resp = self.client.get('/employer/jobs')
        self.assertEqual(my_jobs_resp.status_code, 200)
        self.assertIn(b'My Posted Job Openings', my_jobs_resp.data)

        # 5. Candidate Applicants Hub
        app_resp = self.client.get('/employer/applications')
        self.assertEqual(app_resp.status_code, 200)
        self.assertIn(b'Candidate Applicants', app_resp.data)

        # 6. Company Profile
        comp_resp = self.client.get('/employer/company-profile')
        self.assertEqual(comp_resp.status_code, 200)
        self.assertIn(b'Company Profile', comp_resp.data)

        # 7. Logout
        self.client.get('/logout')
        print(" [PASS] Employer authentication, job postings, and applicants hub verified.")

    def test_06_admin_workflow(self):
        # 1. Login as admin
        login_resp = self.login('admin@jobconnect.com', 'admin123')
        self.assertEqual(login_resp.status_code, 200)

        # 2. Admin Dashboard
        admin_dash = self.client.get('/admin/dashboard')
        self.assertEqual(admin_dash.status_code, 200)
        self.assertIn(b'Admin Command Center', admin_dash.data)

        # 3. Manage Users
        users_resp = self.client.get('/admin/users')
        self.assertEqual(users_resp.status_code, 200)
        self.assertIn(b'User Management', users_resp.data)

        # 4. Moderate Jobs
        jobs_resp = self.client.get('/admin/jobs')
        self.assertEqual(jobs_resp.status_code, 200)
        self.assertIn(b'Job Moderation', jobs_resp.data)

        # 5. Categories
        cat_resp = self.client.get('/admin/categories')
        self.assertEqual(cat_resp.status_code, 200)
        self.assertIn(b'Domain Categories', cat_resp.data)

        # 6. Messages
        msg_resp = self.client.get('/admin/messages')
        self.assertEqual(msg_resp.status_code, 200)
        self.assertIn(b'Contact Inquiries', msg_resp.data)

        # 7. Logout
        self.client.get('/logout')
        print(" [PASS] Admin Command Center and all administrative governance pages verified.")

    def test_07_about_and_contact(self):
        # About
        about_resp = self.client.get('/about')
        self.assertEqual(about_resp.status_code, 200)
        self.assertIn(b'Connecting Visionary Companies', about_resp.data)

        # Contact GET
        contact_resp = self.client.get('/contact')
        self.assertEqual(contact_resp.status_code, 200)
        self.assertIn(b'Get in Touch with JobConnect', contact_resp.data)

        # Contact POST
        post_contact = self.client.post('/contact', data={
            'name': 'Aditi Rao',
            'email': 'aditi@example.com',
            'subject': 'Campus Recruitment Partnership',
            'message': 'We want to recruit 200+ graduates using JobConnect.'
        }, follow_redirects=True)
        self.assertEqual(post_contact.status_code, 200)
        self.assertIn(b'Thank you for reaching out', post_contact.data)
        print(" [PASS] About Us and Contact Us form submission verified.")

if __name__ == '__main__':
    print("=" * 60)
    print("[TEST SUITE] Running JobConnect Automated Verification Suite")
    print("=" * 60)
    unittest.main()
