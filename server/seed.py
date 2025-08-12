from app import app
from models import db, User, Job, Application, SavedJob

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Create users
    employer1 = User(username='employer1', email='employer1@example.com', role='employer')
    employer1.set_password('password123')

    employer2 = User(username='employer2', email='employer2@example.com', role='employer')
    employer2.set_password('password123')

    jobseeker1 = User(username='jobseeker1', email='jobseeker1@example.com', role='jobseeker')
    jobseeker1.set_password('password123')

    jobseeker2 = User(username='jobseeker2', email='jobseeker2@example.com', role='jobseeker')
    jobseeker2.set_password('password123')

    db.session.add_all([employer1, employer2, jobseeker1, jobseeker2])
    db.session.commit()

    # Create jobs
    job1 = Job(
        title='Software Engineer',
        description='Develop and maintain software solutions.',
        location='Nairobi',
        salary='100,000 KES',
        job_type='Full-time',
        category='IT',
        experience_required='2 years',
        user_id=employer1.id
    )

    job2 = Job(
        title='Data Analyst',
        description='Analyze and interpret complex data sets.',
        location='Mombasa',
        salary='80,000 KES',
        job_type='Full-time',
        category='Data',
        experience_required='1 year',
        user_id=employer2.id
    )

    job3 = Job(
        title='Graphic Designer',
        description='Create engaging and on-brand graphics.',
        location='Kisumu',
        salary='60,000 KES',
        job_type='Part-time',
        category='Design',
        experience_required='3 years',
        user_id=employer1.id
    )

    db.session.add_all([job1, job2, job3])
    db.session.commit()

    # Create applications
    application1 = Application(user_id=jobseeker1.id, job_id=job1.id, status='pending')
    application2 = Application(user_id=jobseeker2.id, job_id=job2.id, status='accepted')
    application3 = Application(user_id=jobseeker1.id, job_id=job3.id, status='rejected')

    db.session.add_all([application1, application2, application3])
    db.session.commit()

    # Create saved jobs
    saved1 = SavedJob(user_id=jobseeker1.id, job_id=job2.id)
    saved2 = SavedJob(user_id=jobseeker2.id, job_id=job1.id)

    db.session.add_all([saved1, saved2])
    db.session.commit()

    print("Database seeded successfully!")
