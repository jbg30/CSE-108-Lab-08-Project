# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(16), nullable=False)  # "student", "teacher", "admin"

    # relationships
    taught_courses = db.relationship("Course", back_populates="teacher", lazy=True)
    enrollments = db.relationship("Enrollment", back_populates="student", lazy=True)


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False)     # e.g. "CSE 108"
    title = db.Column(db.String(128), nullable=False)   # e.g. "Web Apps"
    capacity = db.Column(db.Integer, nullable=False, default=30)

    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    teacher = db.relationship("User", back_populates="taught_courses")

    enrollments = db.relationship("Enrollment", back_populates="course", lazy=True)


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    grade = db.Column(db.String(4), nullable=True)  # e.g. "A", "B+", or None

    student = db.relationship("User", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")
