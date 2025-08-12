from flask import request, jsonify, session
from app import app, db, bcrypt
from models import User, Job, Application, SavedJob
from sqlalchemy.exc import IntegrityError
from flask_cors import cross_origin
import traceback

# ============================
# AUTH ROUTES
# ============================

@app.route("/api/auth/signup", methods=["POST"])
@cross_origin(supports_credentials=True)
def signup():
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        if not all([username, email, password, role]):
            return jsonify({"error": "All fields are required"}), 400

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Signup successful"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/auth/login", methods=["POST"])
@cross_origin(supports_credentials=True)
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify({"error": "Invalid credentials"}), 401

        session["user_id"] = user.id
        session["role"] = user.role
        return jsonify({"message": "Login successful", "role": user.role}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/auth/logout", methods=["POST"])
@cross_origin(supports_credentials=True)
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


@app.route("/api/auth/forgot-password", methods=["POST"])
@cross_origin(supports_credentials=True)
def forgot_password():
    try:
        data = request.get_json()
        email = data.get("email")
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "No account found with that email"}), 404
        # NOTE: In production, send email with reset token
        return jsonify({"message": "Password reset link sent (mock)"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


# ============================
# JOB ROUTES (EMPLOYER)
# ============================

@app.route("/api/jobs", methods=["POST"])
@cross_origin(supports_credentials=True)
def post_job():
    try:
        if session.get("role") != "employer":
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        new_job = Job(
            title=data.get("title"),
            description=data.get("description"),
            salary=data.get("salary"),
            location=data.get("location"),
            category=data.get("category"),
            experience=data.get("experience"),
            employer_id=session["user_id"],
        )
        db.session.add(new_job)
        db.session.commit()

        return jsonify({"message": "Job posted successfully"}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/jobs/<int:job_id>", methods=["PUT"])
@cross_origin(supports_credentials=True)
def edit_job(job_id):
    try:
        if session.get("role") != "employer":
            return jsonify({"error": "Unauthorized"}), 403

        job = Job.query.get_or_404(job_id)
        if job.employer_id != session["user_id"]:
            return jsonify({"error": "Not your job"}), 403

        data = request.get_json()
        for field in ["title", "description", "salary", "location", "category", "experience"]:
            if field in data:
                setattr(job, field, data[field])

        db.session.commit()
        return jsonify({"message": "Job updated successfully"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
@cross_origin(supports_credentials=True)
def delete_job(job_id):
    try:
        if session.get("role") != "employer":
            return jsonify({"error": "Unauthorized"}), 403

        job = Job.query.get_or_404(job_id)
        if job.employer_id != session["user_id"]:
            return jsonify({"error": "Not your job"}), 403

        db.session.delete(job)
        db.session.commit()
        return jsonify({"message": "Job deleted"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/jobs/mine", methods=["GET"])
@cross_origin(supports_credentials=True)
def my_jobs():
    try:
        if session.get("role") != "employer":
            return jsonify({"error": "Unauthorized"}), 403

        jobs = Job.query.filter_by(employer_id=session["user_id"]).all()
        return jsonify([job.to_dict() for job in jobs]), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


# ============================
# JOB ROUTES (JOBSEEKER)
# ============================

@app.route("/api/jobs", methods=["GET"])
@cross_origin(supports_credentials=True)
def list_jobs():
    try:
        jobs = Job.query.all()
        return jsonify([job.to_dict() for job in jobs]), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/jobs/<int:job_id>/apply", methods=["POST"])
@cross_origin(supports_credentials=True)
def apply_to_job(job_id):
    try:
        if session.get("role") != "jobseeker":
            return jsonify({"error": "Unauthorized"}), 403

        new_app = Application(job_id=job_id, user_id=session["user_id"], status="pending")
        db.session.add(new_app)
        db.session.commit()
        return jsonify({"message": "Application submitted"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Already applied"}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/applications/mine", methods=["GET"])
@cross_origin(supports_credentials=True)
def my_applications():
    try:
        if session.get("role") != "jobseeker":
            return jsonify({"error": "Unauthorized"}), 403

        apps = Application.query.filter_by(user_id=session["user_id"]).all()
        return jsonify([app.to_dict() for app in apps]), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/applications/<int:application_id>/withdraw", methods=["DELETE"])
@cross_origin(supports_credentials=True)
def withdraw_application(application_id):
    try:
        if session.get("role") != "jobseeker":
            return jsonify({"error": "Unauthorized"}), 403

        app_obj = Application.query.get_or_404(application_id)
        if app_obj.user_id != session["user_id"]:
            return jsonify({"error": "Not your application"}), 403

        db.session.delete(app_obj)
        db.session.commit()
        return jsonify({"message": "Application withdrawn"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


# ============================
# APPLICATION MANAGEMENT (EMPLOYER)
# ============================

@app.route("/api/jobs/<int:job_id>/applications", methods=["GET"])
@cross_origin(supports_credentials=True)
def view_applicants(job_id):
    try:
        if session.get("role") != "employer":
            return jsonify({"error": "Unauthorized"}), 403

        job = Job.query.get_or_404(job_id)
        if job.employer_id != session["user_id"]:
            return jsonify({"error": "Not your job"}), 403

        applications = Application.query.filter_by(job_id=job_id).all()
        return jsonify([a.to_dict() for a in applications]), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/applications/<int:application_id>/status", methods=["PUT"])
@cross_origin(supports_credentials=True)
def update_application_status(application_id):
    try:
        if session.get("role") != "employer":
            return jsonify({"error": "Unauthorized"}), 403

        app_obj = Application.query.get_or_404(application_id)
        job = Job.query.get(app_obj.job_id)
        if job.employer_id != session["user_id"]:
            return jsonify({"error": "Not your job"}), 403

        data = request.get_json()
        new_status = data.get("status")
        if new_status not in ["pending", "accepted", "rejected", "interview"]:
            return jsonify({"error": "Invalid status"}), 400

        app_obj.status = new_status
        db.session.commit()
        return jsonify({"message": "Status updated"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500

