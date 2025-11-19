from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy instance - this will be used to interact with our database
db = SQLAlchemy()

class User(UserMixin):
    """
    Base User class for authentication.
    This provides common functionality for all user types (student, teacher, admin)
    """
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

class Student(db.Model):
    """
    Represents a student in the system.
    Stores student information and manages course enrollments.
    """
    __tablename__ = 'students'  # Table name in database
    
    # Primary key - unique identifier for each student
    id = db.Column(db.Integer, primary_key=True)
    # Student's name
    name = db.Column(db.String(100), nullable=False)
    # Unique email for login and communication
    email = db.Column(db.String(100), unique=True, nullable=False)
    # Hashed password for security
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Relationship with enrollments - allows easy access to student's courses
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)

    def set_password(self, password):
        """Hash and set the student's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the provided password against the stored hash"""
        return check_password_hash(self.password_hash, password)

class Teacher(db.Model):
    """
    Represents a teacher in the system.
    Teachers can manage courses and student grades.
    """
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Courses taught by this teacher
    courses = db.relationship('Course', backref='teacher', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(db.Model):
    """
    Represents an administrator in the system.
    Admins have full control over all data.
    """
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Course(db.Model):
    """
    Represents a course offered by the university.
    Contains course details and capacity information.
    """
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    # Course name (e.g., "CSE 162")
    name = db.Column(db.String(100), nullable=False)
    # Course description
    description = db.Column(db.Text)
    # Maximum number of students allowed
    capacity = db.Column(db.Integer, nullable=False, default=30)
    
    # Foreign key linking to the teacher who teaches this course
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    
    # Relationship with enrollments - allows access to students in this course
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

class Enrollment(db.Model):
    """
    Represents a student's enrollment in a course.
    Also stores the student's grade for that course.
    """
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key linking to student
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    # Foreign key linking to course
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    # Student's grade in this course (nullable until assigned)
    grade = db.Column(db.Float, nullable=True)
    
    # Ensure a student can only enroll in a course once
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),
    )