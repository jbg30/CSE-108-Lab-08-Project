from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Use a NEW database file for Lab 8
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///enrollment.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------- LAB 8 TABLES (you can expand these later) ----------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(16), nullable=False)  # "student", "teacher", "admin"

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
# ---------------------------------------------------------------


# Original Lab 7 Student table (still works, just in the new DB)
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    grade = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {self.name: self.grade}


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


# ---------- NEW: LOGIN ENDPOINT FOR LAB 8 ----------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # This is what the frontend will use:
    return jsonify(
        {
            "id": user.id,
            "full_name": user.full_name,
            "role": user.role,
        }
    )
# --------------------------------------------------


# ---------- COURSE / ENROLLMENT ENDPOINTS ----------

# 1) All courses (for "Add Courses" list)
@app.route("/api/courses", methods=["GET"])
def get_courses():
    courses = Course.query.all()
    result = []

    for c in courses:
        enrolled_count = Enrollment.query.filter_by(course_id=c.id).count()
        result.append(
            {
                "id": c.id,
                "code": c.code,
                "title": c.title,
                "capacity": c.capacity,
                "enrolled_count": enrolled_count,
                "teacher_name": c.teacher.full_name if c.teacher else None,
            }
        )

    return jsonify(result)


# 2) Courses a specific student is enrolled in ("Your Courses")
@app.route("/api/students/<int:student_id>/courses", methods=["GET"])
def get_student_courses(student_id):
    student = User.query.get_or_404(student_id)

    if student.role != "student":
        return jsonify({"error": "User is not a student"}), 400

    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    result = []

    for e in enrollments:
        c = e.course
        result.append(
            {
                "id": c.id,
                "code": c.code,
                "title": c.title,
                "capacity": c.capacity,
                "grade": e.grade,
            }
        )

    return jsonify(result)


# 3) Enroll a student in a course
@app.route("/api/students/<int:student_id>/enroll/<int:course_id>", methods=["POST"])
def enroll_student_in_course(student_id, course_id):
    student = User.query.get_or_404(student_id)
    if student.role != "student":
        return jsonify({"error": "User is not a student"}), 400

    course = Course.query.get_or_404(course_id)

    # Already enrolled?
    existing = Enrollment.query.filter_by(
        student_id=student_id, course_id=course_id
    ).first()
    if existing:
        return jsonify({"error": "Student is already enrolled in this course"}), 400

    # Capacity check
    enrolled_count = Enrollment.query.filter_by(course_id=course_id).count()
    if enrolled_count >= course.capacity:
        return jsonify({"error": "Course is full"}), 400

    enrollment = Enrollment(student_id=student_id, course_id=course_id, grade=None)
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({"message": "Enrolled successfully"}), 201

# ---------- END COURSE / ENROLLMENT ENDPOINTS ----------


# Section: All Grades
@app.route("/api/grades", methods=["GET"])
def get_all_grades():
    students = Student.query.all()
    return jsonify({s.name: s.grade for s in students})


# Section: Get Grade
@app.route("/api/grades/<string:name>", methods=["GET"])
def get_grade(name):
    student = Student.query.filter_by(name=name).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({student.name: student.grade})


# Section: Add new student
@app.route("/api/grades", methods=["POST"])
def add_student():
    data = request.get_json()
    name = data.get("name")
    grade = data.get("grade")

    if not name or grade is None:
        return jsonify({"error": "Name and grade required"}), 400

    existing = Student.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "Student already exists"}), 400

    new_student = Student(name=name, grade=grade)
    db.session.add(new_student)
    db.session.commit()

    return jsonify({name: grade}), 201


# Section: Edit Grade
@app.route("/api/grades/<string:name>", methods=["PUT"])
def edit_student(name):
    student = Student.query.filter_by(name=name).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()
    grade = data.get("grade")
    if grade is None:
        return jsonify({"error": "Grade required"}), 400

    student.grade = grade
    db.session.commit()
    return jsonify({student.name: student.grade})


# Section: Delete
@app.route("/api/grades/<string:name>", methods=["DELETE"])
def delete_student(name):
    student = Student.query.filter_by(name=name).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": f"{name} deleted successfully"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
