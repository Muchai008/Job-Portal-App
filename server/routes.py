from flask import request, jsonify, session
from app import app, db, bcrypt
from models import User, Job, Application, SavedJob
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS, cross_origin
import traceback

#AUTH 
try:
    from routes import *
except Exception as e:
    print("ROUTE IMPORT ERROR:", e)

@app.route('/api/auth/signup', methods=['POST'])
@cross_origin(supports_credentials=True)
def signup():
    data = request.get_json()
    try:
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(
            name=data['name'],
            email=data['email'],
            password=hashed_pw,
            role=data['role']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Signup successful"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    if not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user_id'] = user.id
    session['role'] = user.role
    return jsonify({'message': 'Login successful', 'role': user.role, 'user': user.email})


@app.route('/api/auth/logout', methods=['POST'])
@cross_origin(supports_credentials=True)
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out"}), 200

@app.route('/api/auth/user', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })

#JOBS

@app.route('/api/jobs', methods=['GET'])
@cross_origin()
def get_all_jobs():
    jobs = Job.query.filter_by(is_active=True).all()
    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "category": job.category,
            "salary": job.salary,
            "experience_required": job.experience_required,
            "job_type": job.job_type,
            "employer_id": job.employer_id,
            "created_at": job.created_at
        })
    return jsonify(result)

@app.route('/api/jobs', methods=['POST'])
@cross_origin(supports_credentials=True)
def post_job():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(user_id)
    if user.role != 'employer':
        return jsonify({"error": "Only employers can post jobs"}), 403

    data = request.get_json()
    job = Job(
        title=data['title'],
        description=data['description'],
        location=data['location'],
        category=data.get('category'),
        salary=data.get('salary'),
        experience_required=data.get('experience_required'),
        job_type=data.get('job_type'),
        employer_id=user.id
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "Job posted successfully"}), 201

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
def edit_job(job_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    job = Job.query.get_or_404(job_id)
    if job.employer_id != user_id:
        return jsonify({"error": "Not your job"}), 403

    data = request.get_json()
    job.title = data['title']
    job.description = data['description']
    job.location = data['location']
    job.category = data.get('category')
    job.salary = data.get('salary')
    job.experience_required = data.get('experience_required')
    job.job_type = data.get('job_type')
    db.session.commit()
    return jsonify({"message": "Job updated"}), 200

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete_job(job_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    job = Job.query.get_or_404(job_id)
    if job.employer_id != user_id:
        return jsonify({"error": "Not your job"}), 403
    job.is_active = False
    db.session.commit()
    return jsonify({"message": "Job deleted"}), 200

#APPLICATIONS

@app.route('/api/apply/<int:job_id>', methods=['POST'])
@cross_origin(supports_credentials=True)
def apply_to_job(job_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(user_id)
    if user.role != 'jobseeker':
        return jsonify({"error": "Only jobseekers can apply"}), 403
    existing = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing:
        return jsonify({"error": "Already applied"}), 400
    application = Application(user_id=user_id, job_id=job_id)
    db.session.add(application)
    db.session.commit()
    return jsonify({"message": "Application submitted"}), 201

@app.route('/api/applications', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_applications():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(user_id)

    if user.role == 'jobseeker':
        apps = Application.query.filter_by(user_id=user_id).all()
    else:
        apps = Application.query.join(Job).filter(Job.employer_id == user_id).all()

    result = []
    for a in apps:
        result.append({
            "id": a.id,
            "job_id": a.job_id,
            "job_title": a.job.title,
            "status": a.status,
            "applicant_id": a.user_id,
            "applicant_name": a.applicant.name,
            "applied_at": a.applied_at
        })
    return jsonify(result)

@app.route('/api/applications/<int:app_id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_application_status(app_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    app_entry = Application.query.get_or_404(app_id)
    job = Job.query.get(app_entry.job_id)
    if job.employer_id != user_id:
        return jsonify({"error": "Only employer can update status"}), 403

    new_status = request.get_json().get('status')
    if new_status not in ['pending', 'accepted', 'rejected', 'interview']:
        return jsonify({"error": "Invalid status"}), 400

    app_entry.status = new_status
    db.session.commit()
    return jsonify({"message": "Application status updated"}), 200

@app.route('/api/applications/<int:app_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def withdraw_application(app_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    app_entry = Application.query.get_or_404(app_id)
    if app_entry.user_id != user_id:
        return jsonify({"error": "Not your application"}), 403

    db.session.delete(app_entry)
    db.session.commit()
    return jsonify({"message": "Application withdrawn"}), 200

# ---------- SAVED JOBS ----------

@app.route('/api/saved/<int:job_id>', methods=['POST'])
@cross_origin(supports_credentials=True)
def save_job(job_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    if SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first():
        return jsonify({"error": "Already saved"}), 400
    save = SavedJob(user_id=user_id, job_id=job_id)
    db.session.add(save)
    db.session.commit()
    return jsonify({"message": "Job saved"}), 201

@app.route('/api/saved/<int:job_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def unsave_job(job_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    saved = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
    if not saved:
        return jsonify({"error": "Job not saved"}), 404
    db.session.delete(saved)
    db.session.commit()
    return jsonify({"message": "Job unsaved"}), 200

@app.route('/api/saved', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_saved_jobs():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    saved = SavedJob.query.filter_by(user_id=user_id).all()
    result = [{
        "job_id": s.job.id,
        "title": s.job.title,
        "location": s.job.location,
        "category": s.job.category
    } for s in saved]
    return jsonify(result)
