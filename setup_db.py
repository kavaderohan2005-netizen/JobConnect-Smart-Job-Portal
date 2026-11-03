import os
import sys
from app import create_app
from database import db
from seed_data import seed_database
from models import User, Job, Company, Application

def setup():
    print("=" * 65)
    print("  JobConnect – Smart Job Portal Database Setup")
    print("=" * 65)
    
    app = create_app()
    with app.app_context():
        print(f"Connecting to database engine: {app.config.get('ACTIVE_DB_NAME')}")
        print("Creating all database tables according to schema...")
        db.create_all()
        print("Tables created successfully.")
        
        print("Checking sample data...")
        seed_database()
        
        # Summary
        print("-" * 65)
        print("DATABASE SUMMARY:")
        print(f" - Users:        {User.query.count()}")
        print(f" - Companies:    {Company.query.count()}")
        print(f" - Jobs:         {Job.query.count()}")
        print(f" - Applications: {Application.query.count()}")
        print("-" * 65)
        print("TEST LOGIN CREDENTIALS:")
        print(" 1. Job Seeker:  Email: seeker@jobconnect.com   | Pass: seeker123")
        print(" 2. Employer:    Email: employer@jobconnect.com | Pass: employer123")
        print(" 3. Admin:       Email: admin@jobconnect.com    | Pass: admin123")
        print("=" * 65)

if __name__ == "__main__":
    setup()
