from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy instance - this will be used to interact with our database
db = SQLAlchemy()

# authentication for all
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# stores student info
class Student(db.Model):
    __tablename__ = 'students'
    
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
    
    def __str__(self):
        return self.name

# stores teacher info
class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    courses = db.relationship('Course', backref='teacher', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __str__(self):
        return self.name

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# courses offered and capacity
class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=30)

    # Foreign key linking to the teacher who teaches this course
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    
    # Relationship with enrollments - allows access to students in this course
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

    def __str__(self):
        return self.name

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    grade = db.Column(db.Float, nullable=True)
    
    # Ensure a student can only enroll in a course once
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),
    )
    

