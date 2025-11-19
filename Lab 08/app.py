from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import db, Student, Teacher, Admin, Course, Enrollment
from admin import setup_admin
from flask import redirect, url_for, session
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
setup_admin(app)

# AUTHENTICATION ROUTES (student, teacher, admin logins)

@app.route('/')
def index():
    return redirect(url_for('student_login'))

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('studentLoginEmail')
        password = request.form.get('studentLoginPassword')
        
        print(f"Student login attempt: {email}")
        
        student = Student.query.filter_by(email=email).first()
        
        if student and student.check_password(password):
            # Store user info in session
            session['user_id'] = student.id
            session['user_email'] = student.email
            session['user_name'] = student.name
            session['role'] = 'student'
            print(f"Student login successful: {student.name}")
            return redirect(url_for('student_dashboard'))
        else:
            print("Student login failed")
            return render_template('student_login.html', error="Invalid email or password")
    
    return render_template('student_login.html')

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Teacher login attempt: {email}")
        
        teacher = Teacher.query.filter_by(email=email).first()
        
        if teacher and teacher.check_password(password):
            session['user_id'] = teacher.id
            session['user_email'] = teacher.email
            session['user_name'] = teacher.name
            session['role'] = 'teacher'
            print(f"Teacher login successful: {teacher.name}")
            return redirect(url_for('teacher_dashboard'))
        else:
            print("Teacher login failed")
            return render_template('professor_login.html', error="Invalid email or password")
    
    return render_template('professor_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Admin login attempt: {username}")
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['user_id'] = admin.id
            session['user_name'] = admin.username
            session['role'] = 'admin'
            print(f"Admin login successful: {admin.username}")
            return redirect(url_for('admin_dashboard'))
        else:
            print("Admin login failed")
            return render_template('admin_login.html', error="Invalid username or password")
    
    return render_template('admin_login.html')

# Update grade
@app.route("/api/admin/enrollments/<int:enrollment_id>", methods=["PUT"])
def admin_update_grade(enrollment_id):
    data = request.json
    new_grade = data.get("grade")

    if new_grade is None:
        return jsonify({"success": False, "error": "Grade not provided"}), 400

    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({"success": False, "error": "Enrollment not found"}), 404

    enrollment.grade = new_grade
    db.session.commit()

    return jsonify({
        "success": True,
        "enrollment_id": enrollment.id,
        "grade": enrollment.grade
    })

# Remove student
@app.route("/api/admin/enrollments/<int:enrollment_id>", methods=["DELETE"])
def admin_remove_student(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({"success": False, "error": "Enrollment not found"}), 404

    db.session.delete(enrollment)
    db.session.commit()

    return jsonify({
        "success": True,
        "enrollment_id": enrollment_id
    })


# DASHBOARD ROUTES

@app.route('/student/dashboard')
def student_dashboard():
    # Check if user is logged in as student
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('student_login'))
    
    student_id = session['user_id']
    student_name = session['user_name']
    
    print(f"Loading dashboard for student: {student_name} (ID: {student_id})")
    
    # Get student's enrolled courses
    enrollments = Enrollment.query.filter_by(student_id=student_id).join(Course).all()
    
    enrolled_courses = []
    for enrollment in enrollments:
        enrolled_courses.append({
            'name': enrollment.course.name,
            'professor': enrollment.course.teacher.name,
            'credits': 3,  # Default credits
            'grade': enrollment.grade
        })
    
    print(f"Student has {len(enrolled_courses)} enrolled courses")
    
    return render_template('student_dashboard.html', 
                         student_name=student_name,
                         courses=enrolled_courses)

@app.route('/teacher/dashboard')
def teacher_dashboard():
    # Check if user is logged in as teacher
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('teacher_login'))

    teacher_id = session['user_id']
    teacher_name = session['user_name']

    print(f"Loading dashboard for teacher: {teacher_name} (ID: {teacher_id})")

    # Get courses taught by this teacher
    courses = Course.query.filter_by(teacher_id=teacher_id).all()

    # Build course data list
    course_data = []
    for course in courses:
        enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()

        course_data.append({
            'id': course.id,
            'name': course.name,
            'teacher_name': teacher_name,
            'enrollment_count': enrollment_count,
            'capacity': course.capacity
        })

    print(f"Teacher has {len(course_data)} courses")

    return render_template(
        'professor_dashboard.html',
        professor_name=teacher_name,
        courses=course_data
    )

# TEACHER COURSES

@app.route('/professor/course/<int:course_id>')
def view_course(course_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('teacher_login'))

    teacher_id = session['user_id']
    course = Course.query.get_or_404(course_id)

    # Make sure this teacher owns the course
    if course.teacher_id != teacher_id:
        return "Unauthorized", 403

    # Get students enrolled in this course
    enrollments = Enrollment.query.filter_by(course_id=course_id).join(Student).all()
    student_data = []
    for enrollment in enrollments:
        student_data.append({
            'id': enrollment.student.id,
            'name': enrollment.student.name,
            'grade': enrollment.grade
        })

    return render_template(
        'professor_course.html',
        course=course,
        students=student_data
    )

@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    classes = Course.query.options(
        db.joinedload(Course.teacher),
        db.joinedload(Course.enrollments).joinedload(Enrollment.student)
    ).all()

    return render_template("admin_dashboard.html", classes=classes)

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add_class():
    # Only admins can access this
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description") or ""
        capacity = request.form.get("capacity")
        teacher_id = request.form.get("teacher_id")

        # Basic validation
        if not name or not capacity or not teacher_id:
            error = "All fields are required."
            teachers = Teacher.query.all()
            return render_template(
                "admin_add_class.html", teachers=teachers, error=error
            )

        try:
            capacity = int(capacity)
        except ValueError:
            error = "Capacity must be a number."
            teachers = Teacher.query.all()
            return render_template(
                "admin_add_class.html", teachers=teachers, error=error
            )

        new_course = Course(
            name=name,
            description=description,
            capacity=capacity,
            teacher_id=int(teacher_id),
        )
        db.session.add(new_course)
        db.session.commit()

        print(f"Admin added new class: {name}")
        return redirect(url_for("admin_dashboard"))

    # GET: show the form with list of teachers
    teachers = Teacher.query.all()
    return render_template("admin_add_class.html", teachers=teachers)

@app.route('/student/register')
def student_register():
    # Check if user is logged in as student
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('student_login'))
    
    student_id = session['user_id']
    student_name = session['user_name']
    
    print(f"Loading registration page for student: {student_name} (ID: {student_id})")
    
    # Get all available courses
    courses = Course.query.all()
    course_data = []
    
    for course in courses:
        enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()
        course_data.append({
            'id': course.id,
            'name': course.name,
            'professor': course.teacher.name,
            'enrolled': enrollment_count,
            'capacity': course.capacity
        })
    
    print(f"Passing {len(course_data)} courses to registration page")
    
    # Debug: print each course
    for course in course_data:
        print(f"   - {course['name']} by {course['professor']} ({course['enrolled']}/{course['capacity']})")
    
    return render_template('student_register.html', courses=course_data)

# API ENDPOINTS

# allows the front end javascript to update grades in the teacher.js function
@app.route('/api/course/<int:course_id>/student/<int:student_id>/grade', methods=['PUT'])
def update_grade(course_id, student_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return jsonify({'error': 'Not logged in'}), 401

    course = Course.query.get_or_404(course_id)

    if course.teacher_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    grade = data.get('grade')

    enrollment = Enrollment.query.filter_by(course_id=course_id, student_id=student_id).first()
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    enrollment.grade = grade
    db.session.commit()

    return jsonify({'message': 'Grade updated successfully'})

@app.route('/api/student/register', methods=['POST'])
def api_student_register():
    if 'user_id' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Not logged in'}), 401
    
    student_id = session['user_id']
    student_name = session['user_name']
    course_id = request.json.get('courseId')
    
    print(f"Student {student_name} (ID: {student_id}) attempting to enroll in course {course_id}")
    
    # Check if course exists
    course = Course.query.get(course_id)
    if not course:
        print(f"Course {course_id} not found")
        return jsonify({'error': 'Course not found'}), 404
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        student_id=student_id, course_id=course_id
    ).first()
    
    if existing_enrollment:
        print(f"Student already enrolled in {course.name}")
        return jsonify({'error': 'Already enrolled in this course'}), 400
    
    # Check course capacity
    enrollment_count = Enrollment.query.filter_by(course_id=course_id).count()
    if enrollment_count >= course.capacity:
        print(f"Course {course.name} is full ({enrollment_count}/{course.capacity})")
        return jsonify({'error': 'Course is full'}), 400
    
    # Create new enrollment
    new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
    db.session.add(new_enrollment)
    db.session.commit()
    
    print(f"Successfully enrolled {student_name} in {course.name}")
    
    return jsonify({'message': 'Successfully enrolled in course'})

# Grades API endpoints for your index.html and script.js
@app.route('/api/grades', methods=['GET', 'POST'])
def api_grades():
    if request.method == 'GET':
        # Return all grades
        enrollments = Enrollment.query.filter(Enrollment.grade.isnot(None)).all()
        grades = {}
        for enrollment in enrollments:
            student = Student.query.get(enrollment.student_id)
            grades[student.name] = enrollment.grade
        
        print(f"Returning {len(grades)} grades via API")
        return jsonify(grades)
    
    elif request.method == 'POST':
        # Add new grade
        data = request.json
        student_name = data.get('name')
        grade = data.get('grade')
        
        print(f"Adding grade {grade} for student {student_name}")
        
        # Find student by name
        student = Student.query.filter_by(name=student_name).first()
        if student:
            # For demo, add to first enrollment or create one
            enrollment = Enrollment.query.filter_by(student_id=student.id).first()
            if not enrollment:
                # Create a dummy enrollment if none exists
                first_course = Course.query.first()
                enrollment = Enrollment(student_id=student.id, course_id=first_course.id)
                db.session.add(enrollment)
            
            enrollment.grade = grade
            db.session.commit()
            print(f"Added grade {grade} for {student_name}")
            return jsonify({'message': 'Grade added successfully'})
        
        print(f"Student {student_name} not found")
        return jsonify({'error': 'Student not found'}), 404

# Individual student grade options
@app.route('/api/grades/<student_name>', methods=['GET', 'PUT', 'DELETE'])
def api_grade_student(student_name):
    print(f"Grade operation for student: {student_name}")
    
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        print(f"Student {student_name} not found")
        return jsonify({'error': 'Student not found'}), 404
    
    if request.method == 'GET':
        enrollment = Enrollment.query.filter_by(student_id=student.id).first()
        if enrollment and enrollment.grade:
            print(f"Found grade {enrollment.grade} for {student_name}")
            return jsonify({student_name: enrollment.grade})
        print(f"No grade found for {student_name}")
        return jsonify({'error': 'Grade not found'}), 404
    
    elif request.method == 'PUT':
        data = request.json
        new_grade = data.get('grade')
        
        enrollment = Enrollment.query.filter_by(student_id=student.id).first()
        if enrollment:
            enrollment.grade = new_grade
            db.session.commit()
            print(f"Updated grade to {new_grade} for {student_name}")
            return jsonify({'message': 'Grade updated successfully'})
        
        print(f"No enrollment found for {student_name}")
        return jsonify({'error': 'Enrollment not found'}), 404
    
    elif request.method == 'DELETE':
        enrollment = Enrollment.query.filter_by(student_id=student.id).first()
        if enrollment:
            enrollment.grade = None
            db.session.commit()
            print(f"Deleted grade for {student_name}")
            return jsonify({'message': 'Grade deleted successfully'})
        
        print(f"No enrollment found for {student_name}")
        return jsonify({'error': 'Enrollment not found'}), 404
    
# ADMIN COURSE MANAGEMENT API (used by admin.js Edit/Delete/Add)


def _course_to_dict(course: Course):
    enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()
    return {
        "id": course.id,
        "name": course.name,
        "professor": course.teacher.name if course.teacher else "No Teacher",
        "students": enrollment_count,
        "capacity": course.capacity,
    }


@app.route("/api/admin/courses", methods=["GET", "POST"])
def api_admin_courses():
    # Ensure admin
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Not authorized"}), 401

    if request.method == "GET":
        courses = Course.query.all()
        return jsonify([_course_to_dict(c) for c in courses])

    # POST - create new course
    data = request.json or {}
    name = data.get("name")
    professor_name = data.get("professor")
    capacity = data.get("capacity", 30)

    if not name or not professor_name:
        return jsonify({"error": "Name and professor are required"}), 400

    teacher = Teacher.query.filter_by(name=professor_name).first()
    if not teacher:
        return jsonify({"error": f"Teacher '{professor_name}' not found"}), 404

    course = Course(
        name=name,
        description=data.get("description", ""),
        capacity=capacity,
        teacher_id=teacher.id,
    )
    db.session.add(course)
    db.session.commit()

    print(f"Admin created course {course.name} (ID: {course.id})")
    return jsonify(_course_to_dict(course)), 201

@app.route("/admin/course/<int:course_id>/edit")
def admin_edit_course(course_id):
    # Get the course
    course = Course.query.get_or_404(course_id)
    
    # Make sure course has a list of enrollments for the template
    enrollments = Enrollment.query.filter_by(course_id=course_id).join(Student).all()
    course.enrollments = enrollments  # attach it dynamically

    return render_template("admin_edit.html", course=course)

# Admin Edit/Delete course
@app.route("/api/admin/courses/<int:course_id>", methods=["PUT", "DELETE"])
def api_admin_course_detail(course_id):
    
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Not authorized"}), 401

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    if request.method == "PUT":
        data = request.json or {}
        name = data.get("name")
        professor_name = data.get("professor")
        capacity = data.get("capacity")

        if name:
            course.name = name
        if capacity is not None:
            course.capacity = capacity

        if professor_name:
            teacher = Teacher.query.filter_by(name=professor_name).first()
            if not teacher:
                return jsonify({"error": f"Teacher '{professor_name}' not found"}), 404
            course.teacher_id = teacher.id

        db.session.commit()
        print(f"Admin updated course {course.id}")
        return jsonify(_course_to_dict(course))

    # DELETE
    Enrollment.query.filter_by(course_id=course.id).delete()
    db.session.delete(course)
    db.session.commit()
    print(f"Admin deleted course {course_id}")
    return jsonify({"message": "Course deleted"})


# ADMIN WORK
@app.route('/admin_logout')
def admin_logout():
    session.pop('role', None)
    session.pop('user_id', None)
    return redirect(url_for('admin_login'))


# Logout

@app.route('/logout')
def logout():
    user_info = f"{session.get('user_name', 'Unknown')} ({session.get('role', 'Unknown')})"
    session.clear()
    print(f"User logged out: {user_info}")
    return redirect(url_for('student_login'))

# APPLICATION STARTUP

if __name__ == '__main__':
    
    print("\nExample Logins:")
    print("   Student: jsantos@student.com / password")
    print("   Teacher: ahepworth@teacher.com / password")
    print("   Admin: admin / admin123")
    print("")
    
    app.run(debug=True, port=5000)