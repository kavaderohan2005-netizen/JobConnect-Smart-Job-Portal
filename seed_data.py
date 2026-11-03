import os
import json
from datetime import datetime, timedelta, date
from database import db
from models import User, Company, Category, JobSeeker, Employer, Job, Application, Resume, SavedJob, Notification, ContactMessage

def seed_database():
    # Check if already seeded
    if User.query.first():
        print("Database already contains data. Skipping initial seeding.")
        return

    print("Seeding database with realistic Indian Job Portal data...")

    # 1. Create Categories
    categories_data = [
        {"name": "Data Science & AI", "slug": "data-science-ai", "icon": "fa-brain", "description": "Machine Learning, Deep Learning, Generative AI, and Data Science"},
        {"name": "Data Analytics & BI", "slug": "data-analytics-bi", "icon": "fa-chart-pie", "description": "Power BI, Tableau, SQL Analytics, and Business Intelligence"},
        {"name": "Software Engineering", "slug": "software-engineering", "icon": "fa-laptop-code", "description": "Backend, Systems, Microservices, and Full-Stack Engineering"},
        {"name": "Web & Frontend Development", "slug": "web-frontend-development", "icon": "fa-code", "description": "React.js, Vue, Angular, Modern Web Interfaces"},
        {"name": "Database & Data Engineering", "slug": "database-data-engineering", "icon": "fa-database", "description": "PostgreSQL, MySQL, Spark, ETL Pipelines & Big Data"},
        {"name": "Product & Business Analysis", "slug": "product-business-analysis", "icon": "fa-briefcase", "description": "Product Management, Requirement Gathering, Agile Business Analysis"},
        {"name": "Cloud & DevOps", "slug": "cloud-devops", "icon": "fa-cloud", "description": "AWS, GCP, Kubernetes, CI/CD, Infrastructure as Code"},
        {"name": "Cybersecurity & IT", "slug": "cybersecurity-it", "icon": "fa-shield-halved", "description": "Information Security, Vulnerability Assessment, Network Sec"}
    ]

    cat_objects = {}
    for c_data in categories_data:
        cat = Category(
            name=c_data["name"],
            slug=c_data["slug"],
            icon=c_data["icon"],
            description=c_data["description"]
        )
        db.session.add(cat)
        cat_objects[c_data["slug"]] = cat

    db.session.flush()

    # 2. Create Top Indian Tech Companies
    companies_data = [
        {
            "name": "Razorpay",
            "logo": "razorpay.png",
            "website": "https://razorpay.com",
            "location": "Bengaluru, Karnataka",
            "industry": "FinTech / Financial Services",
            "company_size": "2,000-5,000 employees",
            "founded_year": 2014,
            "description": "Razorpay is India's leading full-stack financial solutions company enabling seamless payments, banking, and credit lines for fast-growing businesses."
        },
        {
            "name": "Swiggy",
            "logo": "swiggy.png",
            "website": "https://swiggy.com",
            "location": "Bengaluru, Karnataka",
            "industry": "Consumer Tech / Quick Commerce",
            "company_size": "5,000-10,000 employees",
            "founded_year": 2014,
            "description": "Swiggy is India's leading on-demand convenience platform connecting millions of consumers with restaurants, grocery deliveries, and dining experiences."
        },
        {
            "name": "Flipkart",
            "logo": "flipkart.png",
            "website": "https://flipkart.com",
            "location": "Bengaluru, Karnataka",
            "industry": "E-Commerce",
            "company_size": "10,000+ employees",
            "founded_year": 2007,
            "description": "Flipkart is one of India's leading digital commerce entities, revolutionizing supply chains, technology, and consumer experiences across the subcontinent."
        },
        {
            "name": "Tata Consultancy Services (TCS)",
            "logo": "tcs.png",
            "website": "https://tcs.com",
            "location": "Mumbai & Pune, Maharashtra",
            "industry": "IT Services & Consulting",
            "company_size": "100,000+ employees",
            "founded_year": 1968,
            "description": "TCS is an IT services, consulting, and business solutions organization partnering with many of the world's largest businesses in their transformation journeys."
        },
        {
            "name": "Infosys",
            "logo": "infosys.png",
            "website": "https://infosys.com",
            "location": "Bengaluru & Hyderabad",
            "industry": "IT Services & Digital Transformation",
            "company_size": "50,000+ employees",
            "founded_year": 1981,
            "description": "A global leader in next-generation digital services and consulting, empowering clients across 50+ countries to navigate digital transformation."
        },
        {
            "name": "Zomato",
            "logo": "zomato.png",
            "website": "https://zomato.com",
            "location": "Gurgaon, Haryana",
            "industry": "Internet / FoodTech",
            "company_size": "4,000-8,000 employees",
            "founded_year": 2008,
            "description": "Zomato is a technology platform connecting customers, restaurant partners, and delivery partners across India and beyond."
        },
        {
            "name": "PhonePe",
            "logo": "phonepe.png",
            "website": "https://phonepe.com",
            "location": "Bengaluru, Karnataka",
            "industry": "Digital Payments & Wealth Tech",
            "company_size": "3,000-6,000 employees",
            "founded_year": 2015,
            "description": "PhonePe is India's largest UPI and digital payments platform, processing billions of transactions per month."
        },
        {
            "name": "Acceldata",
            "logo": "acceldata.png",
            "website": "https://acceldata.io",
            "location": "Bengaluru (Hybrid)",
            "industry": "Enterprise Data Observability",
            "company_size": "200-500 employees",
            "founded_year": 2018,
            "description": "Acceldata is the market leader in enterprise data observability, helping enterprises monitor, optimize, and debug massive distributed data platforms."
        }
    ]

    comp_objects = {}
    for c_data in companies_data:
        comp = Company(
            name=c_data["name"],
            logo=c_data["logo"],
            website=c_data["website"],
            location=c_data["location"],
            industry=c_data["industry"],
            company_size=c_data["company_size"],
            founded_year=c_data["founded_year"],
            description=c_data["description"]
        )
        db.session.add(comp)
        comp_objects[c_data["name"]] = comp

    db.session.flush()

    # 3. Create Users (Admin, Employer, Job Seeker)
    # Admin User
    admin_user = User(
        username="admin",
        email="admin@jobconnect.com",
        role="admin",
        is_active=True
    )
    admin_user.set_password("admin123")
    db.session.add(admin_user)

    # Employer 1 (Razorpay Recruiter)
    emp_user_1 = User(
        username="priya_recruiter",
        email="employer@jobconnect.com",
        role="employer",
        is_active=True
    )
    emp_user_1.set_password("employer123")
    db.session.add(emp_user_1)
    db.session.flush()

    emp_profile_1 = Employer(
        user_id=emp_user_1.id,
        company_id=comp_objects["Razorpay"].id,
        full_name="Priya Nair",
        designation="Lead Technical Talent Partner",
        phone="+91 98765 43210"
    )
    db.session.add(emp_profile_1)

    # Employer 2 (Swiggy Recruiter)
    emp_user_2 = User(
        username="rohit_swiggy",
        email="rohit.hr@swiggy.in",
        role="employer",
        is_active=True
    )
    emp_user_2.set_password("employer123")
    db.session.add(emp_user_2)
    db.session.flush()

    emp_profile_2 = Employer(
        user_id=emp_user_2.id,
        company_id=comp_objects["Swiggy"].id,
        full_name="Rohit Verma",
        designation="Principal Engineering Recruiter",
        phone="+91 98111 22334"
    )
    db.session.add(emp_profile_2)

    # Employer 3 (Infosys & TCS Openings)
    emp_user_3 = User(
        username="ananya_tcs",
        email="ananya.k@tcs.com",
        role="employer",
        is_active=True
    )
    emp_user_3.set_password("employer123")
    db.session.add(emp_user_3)
    db.session.flush()

    emp_profile_3 = Employer(
        user_id=emp_user_3.id,
        company_id=comp_objects["Tata Consultancy Services (TCS)"].id,
        full_name="Ananya Kulkarni",
        designation="Regional Hiring Lead",
        phone="+91 99223 88776"
    )
    db.session.add(emp_profile_3)

    # Job Seeker 1 (Senior Data Scientist / AI Specialist)
    seeker_user_1 = User(
        username="aarav_sharma",
        email="seeker@jobconnect.com",
        role="job_seeker",
        is_active=True
    )
    seeker_user_1.set_password("seeker123")
    db.session.add(seeker_user_1)
    db.session.flush()

    seeker_education = [
        {"degree": "M.Tech in Artificial Intelligence & Machine Learning", "institution": "IIT Madras", "year": "2021", "score": "9.2 CGPA"},
        {"degree": "B.Tech in Computer Science & Engineering", "institution": "NIT Trichy", "year": "2019", "score": "8.8 CGPA"}
    ]
    seeker_experience = [
        {"title": "Senior Data Scientist", "company": "Fractal Analytics", "duration": "2022 - Present", "description": "Architected predictive recommendation engines and LLM-powered enterprise search systems serving 5M+ daily active requests."},
        {"title": "Machine Learning Engineer", "company": "Mu Sigma", "duration": "2021 - 2022", "description": "Developed end-to-end classification, fraud detection, and demand forecasting pipelines in PySpark and scikit-learn."}
    ]
    seeker_projects = [
        {"title": "Autonomous Clinical Research RAG Pipeline", "tech": "Python, LangChain, PyTorch, FAISS, FastAPI", "link": "https://github.com/aarav-sharma/clinical-rag", "summary": "Built a multi-agent RAG system parsing clinical trials and biomedical literature with sub-second hybrid retrieval."},
        {"title": "High-Throughput Fraud Anomaly Engine", "tech": "Python, Kafka, XGBoost, Redis, Docker", "link": "https://github.com/aarav-sharma/fraud-detection-stream", "summary": "Real-time streaming fraud prevention engine detecting suspicious transactions under 20ms latency."}
    ]

    seeker_profile_1 = JobSeeker(
        user_id=seeker_user_1.id,
        full_name="Aarav Sharma",
        headline="Senior Data Scientist | Machine Learning | GenAI & PyTorch Specialist",
        phone="+91 98450 12345",
        location="Bengaluru, Karnataka",
        bio="Passionate Data Scientist with 5+ years of experience delivering high-scale machine learning, natural language processing, and deep learning solutions. Skilled in translating complex business problems into high-ROI production models.",
        github_url="https://github.com/aarav-sharma",
        linkedin_url="https://linkedin.com/in/aarav-sharma-ds",
        portfolio_url="https://aaravsharma.dev",
        skills="Python, Machine Learning, Deep Learning, PyTorch, SQL, Pandas, Scikit-Learn, Docker, FastApi, MLOps, LangChain",
        experience_years=5.2,
        current_company="Fractal Analytics",
        current_salary="₹24 LPA",
        expected_salary="₹32 LPA",
        education_data=json.dumps(seeker_education),
        experience_data=json.dumps(seeker_experience),
        projects_data=json.dumps(seeker_projects)
    )
    db.session.add(seeker_profile_1)
    db.session.flush()

    # Create dummy initial resume for Seeker 1
    resume_file_path = "sample_aarav_sharma_resume.pdf"
    res1 = Resume(
        seeker_id=seeker_profile_1.id,
        original_filename="Aarav_Sharma_Resume_2026.pdf",
        stored_filename=resume_file_path,
        file_path=f"uploads/resumes/{resume_file_path}",
        file_size=245800,
        is_primary=True
    )
    db.session.add(res1)
    db.session.flush()

    # Job Seeker 2 (Full Stack / Python Developer)
    seeker_user_2 = User(
        username="sneha_patel",
        email="sneha.patel@gmail.com",
        role="job_seeker",
        is_active=True
    )
    seeker_user_2.set_password("seeker123")
    db.session.add(seeker_user_2)
    db.session.flush()

    seeker_profile_2 = JobSeeker(
        user_id=seeker_user_2.id,
        full_name="Sneha Patel",
        headline="Full Stack Python & React Developer | 3+ Years Experience",
        phone="+91 97234 56789",
        location="Pune, Maharashtra",
        bio="Full Stack Developer focused on building clean, performant, and reliable web applications using Flask, FastAPI, React, and PostgreSQL.",
        github_url="https://github.com/snehapatel-code",
        linkedin_url="https://linkedin.com/in/sneha-patel-dev",
        skills="Python, Flask, Django, React.js, JavaScript, HTML5, CSS3, PostgreSQL, Git, REST APIs",
        experience_years=3.0,
        current_company="Cognizant",
        current_salary="₹9.5 LPA",
        expected_salary="₹15 LPA",
        education_data=json.dumps([{"degree": "B.E in Information Technology", "institution": "Pune University", "year": "2023", "score": "8.5 CGPA"}]),
        experience_data=json.dumps([{"title": "Software Engineer", "company": "Cognizant", "duration": "2023 - Present", "description": "Developed microservices and customer portal modules in Flask and React."}]),
        projects_data=json.dumps([{"title": "TaskFlow Pro", "tech": "Python, Flask, React, SQLite", "link": "https://github.com", "summary": "Kanban project tracking app with real-time updates."}])
    )
    db.session.add(seeker_profile_2)
    db.session.flush()

    # 4. Create Realistic Indian Job Postings
    # Cover: Data Analyst, Data Scientist, Python Developer, Machine Learning Engineer,
    # SQL Developer, Power BI Developer, Software Developer, Web Developer, Business Analyst.
    jobs_seed = [
        {
            "employer": emp_profile_1,
            "company": comp_objects["Razorpay"],
            "category": cat_objects["data-science-ai"],
            "title": "Lead Data Scientist – Risk & Fraud AI",
            "job_type": "Full-time",
            "work_mode": "Hybrid",
            "experience_level": "Senior Level",
            "min_salary": 2400000,
            "max_salary": 3800000,
            "location": "Bengaluru, Karnataka",
            "skills_required": "Python, Machine Learning, Deep Learning, XGBoost, PyTorch, SQL, Risk Modeling, AWS",
            "openings": 2,
            "deadline": date.today() + timedelta(days=45),
            "description": """Razorpay is seeking an experienced Lead Data Scientist to build next-generation machine learning and deep learning fraud prevention models. You will be responsible for safeguarding billions of dollars in daily payment volumes across millions of Indian merchants.

What You Will Do:
- Architect and deploy real-time fraud detection systems with sub-50ms inference latency.
- Design unsupervised graph neural networks and deep learning models to identify money-muling rings.
- Collaborate with platform engineering and product teams to integrate ML models into core payment gateways.
- Mentor junior data scientists and champion MLOps best practices.""",
            "requirements": """- 5+ years of production experience in machine learning and applied data science.
- Strong proficiency in Python, PyTorch/TensorFlow, scikit-learn, and SQL.
- Prior experience in FinTech, fraud detection, credit underwriting, or anomaly detection is a massive plus.
- Solid grounding in distributed computing (Spark, Ray, Kafka).
- Master's or Bachelor's in CS, Statistics, Mathematics, or related quantitative field.""",
            "benefits": """- Highly competitive compensation + lucrative ESOP grants.
- Comprehensive health insurance for employee and immediate family (₹10 Lakh sum insured).
- Flexible work hours and hybrid work model (2 days office, 3 days remote).
- Annual learning stipend of ₹75,000 for courses and conferences.
- Free catered meals and wellness allowances."""
        },
        {
            "employer": emp_profile_2,
            "company": comp_objects["Swiggy"],
            "category": cat_objects["data-science-ai"],
            "title": "Senior Machine Learning Engineer (Instamart & Logistics)",
            "job_type": "Full-time",
            "work_mode": "Hybrid",
            "experience_level": "Senior Level",
            "min_salary": 2800000,
            "max_salary": 4500000,
            "location": "Bengaluru, Karnataka",
            "skills_required": "Python, Machine Learning, Deep Learning, MLOps, Kubernetes, Spark, C++, PyTorch",
            "openings": 3,
            "deadline": date.today() + timedelta(days=30),
            "description": """At Swiggy Instamart, speed and mathematical precision determine customer delight. We are looking for an exceptional Senior Machine Learning Engineer to solve hyper-local delivery routing, demand forecasting, and inventory allocation challenges.

Key Responsibilities:
- Design and productionize real-time supply-demand prediction models across 30+ Indian metropolitan regions.
- Build automated MLOps pipelines using Kubeflow, MLflow, and AWS SageMaker.
- Optimize deep neural network inference for high-throughput microservices.""",
            "requirements": """- 4-8 years experience deploying machine learning systems in production environments.
- Deep expertise in Python, PyTorch, Docker, Kubernetes, and gRPC microservices.
- Experience with time-series forecasting, reinforcement learning, or combinatorial optimization.
- B.Tech/M.Tech in Computer Science or related fields.""",
            "benefits": """- Industry-benchmark salary + Swiggy stock options.
- Unlimited leave policy and wellness recharge days.
- Relocation assistance to Bengaluru.
- Ergonomic home office setup reimbursement."""
        },
        {
            "employer": emp_profile_1,
            "company": comp_objects["Razorpay"],
            "category": cat_objects["software-engineering"],
            "title": "Senior Python Developer – Core Banking & Microservices",
            "job_type": "Full-time",
            "work_mode": "Hybrid",
            "experience_level": "Mid Level",
            "min_salary": 1600000,
            "max_salary": 2600000,
            "location": "Bengaluru, Karnataka",
            "skills_required": "Python, FastAPI, Flask, PostgreSQL, Redis, Docker, Celery, REST APIs, Microservices",
            "openings": 4,
            "deadline": date.today() + timedelta(days=60),
            "description": """Join RazorpayX, India's premier neo-banking platform. We are seeking talented Senior Python Developers to engineer highly scalable, fault-tolerant backend services handling payouts, payroll, and corporate cards.

Responsibilities:
- Build high-concurrency RESTful and gRPC APIs using Python (FastAPI/Flask).
- Optimize complex database queries, schema designs, and Redis caching layers.
- Implement robust idempotent transaction processors ensuring 99.999% uptime.""",
            "requirements": """- 3-6 years of professional backend development with Python.
- Strong knowledge of relational databases (PostgreSQL, MySQL) and transaction management.
- Hands-on experience with asynchronous task queues (Celery, RabbitMQ, Kafka).
- Clean code architecture, unit testing, and CI/CD pipelines.""",
            "benefits": """- Comprehensive medical insurance covering parents.
- Flexible hybrid work options.
- Gym and fitness reimbursement."""
        },
        {
            "employer": emp_profile_2,
            "company": comp_objects["Swiggy"],
            "category": cat_objects["data-analytics-bi"],
            "title": "Lead Data Analyst – Growth & Customer Retention",
            "job_type": "Full-time",
            "work_mode": "Onsite",
            "experience_level": "Mid Level",
            "min_salary": 1400000,
            "max_salary": 2200000,
            "location": "Bengaluru, Karnataka",
            "skills_required": "SQL, Python, Data Analytics, Tableau, A/B Testing, Statistics, Excel",
            "openings": 2,
            "deadline": date.today() + timedelta(days=40),
            "description": """Swiggy is looking for a Growth Data Analyst to drive deep cohort analytics, user funnel optimization, and high-stakes marketing attribution modeling.

What You Will Do:
- Run statistical hypothesis testing and design A/B experiments for consumer app features.
- Build self-serve dashboards in Tableau and automated SQL metric monitors in Snowflake.
- Uncover user drop-off trends and formulate actionable strategies for executive leaders.""",
            "requirements": """- 3-5 years experience as a Data Analyst in consumer tech or high-growth startups.
- Expert-level SQL skills (window functions, CTEs, query optimization).
- Hands-on statistical analysis in Python (Pandas, NumPy, SciPy).
- Demonstrated experience communicating data stories to non-technical stakeholders.""",
            "benefits": """- Competitive package + meal vouchers.
- Clear career growth ladder into Lead Analyst / Analytics Manager roles."""
        },
        {
            "employer": emp_profile_3,
            "company": comp_objects["Tata Consultancy Services (TCS)"],
            "category": cat_objects["data-analytics-bi"],
            "title": "Power BI & Business Intelligence Developer",
            "job_type": "Full-time",
            "work_mode": "Hybrid",
            "experience_level": "Mid Level",
            "min_salary": 800000,
            "max_salary": 1400000,
            "location": "Pune, Maharashtra",
            "skills_required": "Power BI, DAX, Power Query, SQL, Data Modeling, Azure, Data Warehousing",
            "openings": 5,
            "deadline": date.today() + timedelta(days=50),
            "description": """TCS Digital Enterprise Practice is hiring Power BI Developers for our global banking and healthcare clients. You will transform complex multi-source business data into intuitive, executive-ready interactive dashboards.

Responsibilities:
- Develop enterprise Power BI reports using advanced DAX calculations and Power Query M scripts.
- Design dimensional data models (Star and Snowflake schemas).
- Configure Power BI gateway, row-level security (RLS), and scheduled dataset refreshes.""",
            "requirements": """- 3-6 years of hands-on experience in Power BI development and data modeling.
- Strong SQL proficiency for data extraction, aggregation, and validation.
- Microsoft Certified: Power BI Data Analyst (PL-300) certification is a strong advantage.
- Experience connecting with Azure SQL, Synapse, or Snowflake.""",
            "benefits": """- Stable career growth in Fortune 500 client engagements.
- International client travel opportunities.
- TCS corporate benefits and annual bonus."""
        },
        {
            "employer": emp_profile_3,
            "company": comp_objects["Tata Consultancy Services (TCS)"],
            "category": cat_objects["database-data-engineering"],
            "title": "Senior SQL Developer / Database Administrator",
            "job_type": "Full-time",
            "work_mode": "Hybrid",
            "experience_level": "Mid Level",
            "min_salary": 900000,
            "max_salary": 1600000,
            "location": "Hyderabad, Telangana",
            "skills_required": "SQL, MySQL, PostgreSQL, Stored Procedures, Performance Tuning, ETL, Indexing",
            "openings": 3,
            "deadline": date.today() + timedelta(days=35),
            "description": """We are seeking an experienced SQL Developer to lead database optimization, stored procedure development, and ETL pipeline workflows for large-scale enterprise financial databases.

Key Tasks:
- Write complex stored procedures, triggers, views, and functions.
- Profile and optimize slow queries, analyze execution plans, and maintain indexing strategies.
- Ensure database high availability, backup automation, and replication health.""",
            "requirements": """- 4+ years of professional SQL development on MySQL, PostgreSQL, or MS SQL Server.
- Expert understanding of ACID properties, locking mechanisms, and query execution plans.
- Experience with database migrations and schema version control tools.""",
            "benefits": """- Annual performance bonus and retirement gratuity.
- Comprehensive medical benefits."""
        },
        {
            "employer": emp_profile_1,
            "company": comp_objects["Flipkart"],
            "category": cat_objects["web-frontend-development"],
            "title": "Frontend Engineer III (React.js & Design Systems)",
            "job_type": "Full-time",
            "work_mode": "Onsite",
            "experience_level": "Senior Level",
            "min_salary": 2200000,
            "max_salary": 3600000,
            "location": "Bengaluru, Karnataka",
            "skills_required": "React.js, Next.js, TypeScript, JavaScript, CSS3, Tailwind CSS, Webpack, Redux",
            "openings": 2,
            "deadline": date.today() + timedelta(days=45),
            "description": """Flipkart is hiring Frontend Engineers to build ultra-responsive web experiences for Big Billion Days and millions of daily Indian shoppers.

You will:
- Build accessible, lightning-fast UI components in React and TypeScript.
- Improve Core Web Vitals (LCP, FID, CLS) and optimize bundle size for low-bandwidth mobile networks.
- Contribute to Flipkart's internal design system and UI component libraries.""",
            "requirements": """- 4+ years experience building large-scale web applications in React.js and TypeScript.
- Deep understanding of modern browser rendering pipelines, DOM performance, and state management.
- Strong aesthetic eye for responsive design and micro-interactions.""",
            "benefits": """- Flipkart stock options + joining bonus.
- Health insurance with zero deductible.
- Subsidized transport and day care support."""
        },
        {
            "employer": emp_profile_2,
            "company": comp_objects["Zomato"],
            "category": cat_objects["product-business-analysis"],
            "title": "Senior Business Analyst – Operations & Logistics",
            "job_type": "Full-time",
            "work_mode": "Hybrid",
            "experience_level": "Mid Level",
            "min_salary": 1500000,
            "max_salary": 2400000,
            "location": "Gurgaon, Haryana",
            "skills_required": "Business Analysis, SQL, Python, Excel, Process Optimization, Jira, Agile",
            "openings": 2,
            "deadline": date.today() + timedelta(days=40),
            "description": """Zomato is looking for a business-minded analytical thinker to optimize fleet utilization, delivery partner payouts, and restaurant onboarding efficiency.

Responsibilities:
- Synthesize quantitative data and operational bottlenecks into executive strategic recommendations.
- Work closely with Product Managers and Operations Leaders to define KPIs and SLA metrics.
- Create automated reporting workflows and predictive cost-to-serve models.""",
            "requirements": """- 3-5 years experience as a Business Analyst in tech, e-commerce, or strategy consulting.
- Advanced SQL and financial modeling proficiency in Excel/Google Sheets.
- Strong stakeholder management and presentation skills.""",
            "benefits": """- Competitive cash package + stock options.
- Generous dining credits on Zomato Gold.
- Vibrant Gurgaon campus culture."""
        },
        {
            "employer": emp_profile_1,
            "company": comp_objects["PhonePe"],
            "category": cat_objects["software-engineering"],
            "title": "Software Development Engineer (Python / Backend)",
            "job_type": "Full-time",
            "work_mode": "Onsite",
            "experience_level": "Entry Level",
            "min_salary": 1200000,
            "max_salary": 1800000,
            "location": "Bengaluru, Karnataka",
            "skills_required": "Python, Data Structures, Algorithms, MySQL, Docker, Git, REST APIs",
            "openings": 5,
            "deadline": date.today() + timedelta(days=60),
            "description": """PhonePe is seeking enthusiastic Software Development Engineers to contribute to our high-throughput merchant payment stack. This role offers an unparalleled opportunity to work on mission-critical national infrastructure.

Key Tasks:
- Write robust, high-performance Python code for backend APIs and processing workers.
- Participate in code reviews, technical design documents, and unit test automation.
- Investigate and resolve production system alarms with rapid turnaround.""",
            "requirements": """- 1-3 years software engineering experience or strong graduation project portfolio.
- Excellent foundation in Computer Science fundamentals: Algorithms, Data Structures, OOP.
- Familiarity with Python, relational databases, and Linux environments.""",
            "benefits": """- High entry-level compensation with annual bonuses.
- Comprehensive medical, dental, and vision insurance.
- Mentorship by India's top distributed systems engineers."""
        },
        {
            "employer": emp_profile_1,
            "company": comp_objects["Acceldata"],
            "category": cat_objects["data-science-ai"],
            "title": "Machine Learning Engineer – AI Observability",
            "job_type": "Full-time",
            "work_mode": "Remote",
            "experience_level": "Senior Level",
            "min_salary": 2600000,
            "max_salary": 4200000,
            "location": "Remote, India",
            "skills_required": "Python, Machine Learning, Anomaly Detection, Spark, Kafka, FastAPI, PyTorch",
            "openings": 2,
            "deadline": date.today() + timedelta(days=50),
            "description": """Acceldata builds enterprise observability tools for petabyte-scale data pipelines. We need an ML Engineer to build autonomous drift detection, cost optimization recommendations, and failure prediction models for Apache Spark, Snowflake, and Databricks clusters.

Responsibilities:
- Develop streaming anomaly detection algorithms for multi-tenant data pipelines.
- Deploy low-footprint inference models embedded directly into customer Kubernetes clusters.
- Collaborate with US and India based distributed teams.""",
            "requirements": """- 4+ years applied machine learning experience with heavy focus on system performance.
- Proficiency with Python, streaming engines (Kafka/Flink), and cloud storage.
- Passion for 100% remote work excellence and autonomous problem-solving.""",
            "benefits": """- 100% Remote flexibility anywhere in India.
- US Dollar pegged compensation benchmarks.
- Home office setup grant of ₹1,00,000 + latest Apple MacBook Pro."""
        },
        {
            "employer": emp_profile_3,
            "company": comp_objects["Infosys"],
            "category": cat_objects["web-frontend-development"],
            "title": "Full Stack Web Developer (Python + JavaScript)",
            "job_type": "Full-time",
            "work_mode": "Hybrid",
            "experience_level": "Mid Level",
            "min_salary": 750000,
            "max_salary": 1300000,
            "location": "Noida / Delhi NCR",
            "skills_required": "Python, Django, JavaScript, HTML5, CSS3, Bootstrap, PostgreSQL, Git",
            "openings": 6,
            "deadline": date.today() + timedelta(days=40),
            "description": """Infosys Digital Studio is hiring Full Stack Web Developers to build responsive web applications and portals for European automotive and life sciences clients.

Responsibilities:
- Implement end-to-end features combining Python backend services with modern responsive web interfaces.
- Write unit tests and maintain documentation for secure web standards.""",
            "requirements": """- 2-5 years experience in web application development.
- Sound skills in Python (Django or Flask) and modern frontend web stacks.
- Good communication skills for global client interactions.""",
            "benefits": """- Structured learning paths and certification sponsorship.
- Infosys campus amenities and sports clubs."""
        }
    ]

    job_records = []
    for j_data in jobs_seed:
        job = Job(
            employer_id=j_data["employer"].id,
            company_id=j_data["company"].id,
            category_id=j_data["category"].id,
            title=j_data["title"],
            job_type=j_data["job_type"],
            work_mode=j_data["work_mode"],
            experience_level=j_data["experience_level"],
            min_salary=j_data["min_salary"],
            max_salary=j_data["max_salary"],
            location=j_data["location"],
            skills_required=j_data["skills_required"],
            openings=j_data["openings"],
            deadline=j_data["deadline"],
            description=j_data["description"],
            requirements=j_data["requirements"],
            benefits=j_data["benefits"],
            status="active",
            views_count=142,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(job)
        job_records.append(job)

    db.session.flush()

    # 5. Create Sample Applications for Seeker 1
    app1 = Application(
        job_id=job_records[0].id, # Razorpay Lead Data Scientist
        seeker_id=seeker_profile_1.id,
        resume_id=res1.id,
        cover_letter="I am very excited to apply for the Lead Data Scientist role at Razorpay. With over 5 years of experience building real-time fraud engines and deep learning models at scale, I am confident I can make an immediate high-impact contribution.",
        status="shortlisted",
        recruiter_notes="Strong profile with IIT background and proven track record in financial anomaly detection. Recommended for Technical Round 1."
    )
    db.session.add(app1)

    app2 = Application(
        job_id=job_records[1].id, # Swiggy ML Engineer
        seeker_id=seeker_profile_1.id,
        resume_id=res1.id,
        cover_letter="My experience deploying distributed deep learning models and real-time inference microservices aligns closely with Swiggy Instamart's logistics requirements.",
        status="under_review",
        recruiter_notes="Profile under review by hiring manager."
    )
    db.session.add(app2)

    app3 = Application(
        job_id=job_records[9].id, # Acceldata ML Observability
        seeker_id=seeker_profile_1.id,
        resume_id=res1.id,
        cover_letter="I have deep expertise in building streaming anomaly detection pipelines with Kafka and Spark, which makes me an ideal fit for Acceldata.",
        status="applied"
    )
    db.session.add(app3)

    # 6. Saved Jobs for Seeker 1
    save1 = SavedJob(user_id=seeker_user_1.id, job_id=job_records[2].id)
    save2 = SavedJob(user_id=seeker_user_1.id, job_id=job_records[6].id)
    db.session.add_all([save1, save2])

    # 7. Sample Notifications
    n1 = Notification(
        user_id=seeker_user_1.id,
        title="Application Shortlisted!",
        message="Congratulations! Razorpay has shortlisted your application for Lead Data Scientist – Risk & Fraud AI.",
        link="/seeker/applications"
    )
    n2 = Notification(
        user_id=emp_user_1.id,
        title="New Application Received",
        message="Aarav Sharma has applied for Lead Data Scientist – Risk & Fraud AI.",
        link=f"/employer/jobs/{job_records[0].id}/applicants"
    )
    db.session.add_all([n1, n2])

    # 8. Sample Contact Message
    msg1 = ContactMessage(
        name="Vikram Malhotra",
        email="vikram.m@techcorp.in",
        subject="Enterprise Employer Partnership Inquiry",
        message="We are looking to onboard 50+ recruiters onto JobConnect platform. Would love to schedule a demo of enterprise bulk posting and ATS integration."
    )
    db.session.add(msg1)

    # Commit all seed data
    db.session.commit()
    print("Database seeding completed successfully!")
    print("Pre-configured login accounts:")
    print(" - Job Seeker:  seeker@jobconnect.com   / seeker123")
    print(" - Employer:    employer@jobconnect.com / employer123")
    print(" - Admin:       admin@jobconnect.com    / admin123")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()
