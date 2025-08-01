from app import app, db
from models import User, Job, Application, SavedJob
from faker import Faker
import random

fake = Faker()

def seed():
    with app.app_context():
        print(" Dropping all tables...")
        db.drop_all()

        print(" Creating all tables...")
        db.create_all()

        print("Creating users...")
        users = []
        for i in range(5):
            user = User(
                username=fake.user_name(),
                email=fake.unique.email(),
                role='jobseeker'
            )
            user.set_password('password')
            users.append(user)
            db.session.add(user)

        for i in range(5):
            user = User(
                username=fake.user_name(),
                email=fake.unique.email(),
                role='employer'
            )
            user.set_password('password')
            users.append(user)
            db.session.add(user)

        db.session.commit()

        print("Creating jobs...")
        employers = [u for u in users if u.role == 'employer']
        job_ids = []
        for _ in range(10):
            job = Job(
                title=fake.job(),
                description=fake.paragraph(nb_sentences=5),
                location=fake.city(),
                salary=f"${random.randint(30000, 120000)}",
                job_type=random.choice(['Full-time', 'Part-time', 'Remote']),
                category=random.choice(['Engineering', 'Design', 'Marketing', 'Sales']),
                experience_required=random.choice(['None', '1 year', '2+ years', '5+ years']),
                user_id=random.choice(employers).id
            )
            db.session.add(job)
            db.session.flush()  # Get the ID before commit
            job_ids.append(job.id)

        db.session.commit()

        print("📄 Creating applications...")
        jobseekers = [u for u in users if u.role == 'jobseeker']
        for seeker in jobseekers:
            applied_jobs = random.sample(job_ids, k=3)
            for job_id in applied_jobs:
                application = Application(
                    status=random.choice(['pending', 'accepted', 'rejected', 'interview']),
                    user_id=seeker.id,
                    job_id=job_id
                )
                db.session.add(application)

        db.session.commit()

        print("Creating saved jobs...")
        for seeker in jobseekers:
            saved_jobs = random.sample(job_ids, k=2)
            for job_id in saved_jobs:
                saved = SavedJob(
                    user_id=seeker.id,
                    job_id=job_id
                )
                db.session.add(saved)

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
