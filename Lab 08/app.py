from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import db, Student, Teacher, Admin, Course, Enrollment
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_sample_data():
    """Create sample data that matches your frontend expectations"""
    with app.app_context():
        db.create_all()
        
        # Only create sample data if no students exist
        if not Student.query.first():
            print("🔄 Creating sample data...")
            
            # Create students from your frontend
            student1 = Student(name="Chuck Norris", email="cnorris@student.com")
            student1.set_password("password")
            
            student2 = Student(name="Mindy Smith", email="mindy@student.com") 
            student2.set_password("password")
            
            # Create teachers from your frontend
            teacher1 = Teacher(name="Dr. Hepworth", email="ahepworth@teacher.com")
            teacher1.set_password("password")
            
            teacher2 = Teacher(name="Professor Smith", email="smith@teacher.com")
            teacher2.set_password("password")
            
            # Create admin
            admin1 = Admin(username="admin")
            admin1.set_password("admin123")
            
            # Add users first and commit to get their IDs
            db.session.add_all([student1, student2, teacher1, teacher2, admin1])
            db.session.commit()
            
            print(f"✅ Users created. Teacher IDs: {teacher1.id}, {teacher2.id}")
            
            # Now create courses with the actual teacher objects
            course1 = Course(name="Intro to Web", description="Web Development", capacity=30, teacher_id=teacher1.id)
            course2 = Course(name="Data Structures", description="Algorithms", capacity=25, teacher_id=teacher2.id)
            course3 = Course(name="Math 101", description="Mathematics", capacity=25, teacher_id=teacher1.id)
            course4 = Course(name="History 201", description="World History", capacity=20, teacher_id=teacher2.id)
            
            db.session.add_all([course1, course2, course3, course4])
            db.session.commit()
            
            # Create sample enrollments
            enrollment1 = Enrollment(student_id=student1.id, course_id=course1.id, grade=85.5)
            enrollment2 = Enrollment(student_id=student1.id, course_id=course2.id, grade=92.0)
            enrollment3 = Enrollment(student_id=student2.id, course_id=course3.id, grade=88.0)
            db.session.add_all([enrollment1, enrollment2, enrollment3])
            db.session.commit()
            
            print("✅ Sample data created successfully!")
            print("📧 Student: cnorris@student.com / password")
            print("📧 Teacher: ahepworth@teacher.com / password") 
            print("👤 Admin: admin / admin123")
            
            # Verify data was created
            print(f"📊 Students: {Student.query.count()}, Teachers: {Teacher.query.count()}, Courses: {Course.query.count()}, Enrollments: {Enrollment.query.count()}")
        else:
            print("✅ Database already has data")
            print(f"📊 Current counts - Students: {Student.query.count()}, Teachers: {Teacher.query.count()}, Courses: {Course.query.count()}, Enrollments: {Enrollment.query.count()}")

# ========== AUTHENTICATION ROUTES ==========

@app.route('/')
def index():
    """Home page redirects to student login"""
    return redirect(url_for('student_login'))

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    """Student login using your student_login.html"""
    if request.method == 'POST':
        email = request.form.get('studentLoginEmail')
        password = request.form.get('studentLoginPassword')
        
        print(f"🔐 Student login attempt: {email}")
        
        student = Student.query.filter_by(email=email).first()
        
        if student and student.check_password(password):
            # Store user info in session
            session['user_id'] = student.id
            session['user_email'] = student.email
            session['user_name'] = student.name
            session['role'] = 'student'
            print(f"✅ Student login successful: {student.name}")
            return redirect(url_for('student_dashboard'))
        else:
            print("❌ Student login failed")
            return render_template('student_login.html', error="Invalid email or password")
    
    return render_template('student_login.html')

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    """Teacher login using your teacher_login.html"""
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        
        print(f"🔐 Teacher login attempt: {email}")
        
        teacher = Teacher.query.filter_by(email=email).first()
        
        if teacher and teacher.check_password(password):
            session['user_id'] = teacher.id
            session['user_email'] = teacher.email
            session['user_name'] = teacher.name
            session['role'] = 'teacher'
            print(f"✅ Teacher login successful: {teacher.name}")
            return redirect(url_for('teacher_dashboard'))
        else:
            print("❌ Teacher login failed")
            return render_template('teacher_login.html', error="Invalid email or password")
    
    return render_template('teacher_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login using your admin_login.html"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"🔐 Admin login attempt: {username}")
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['user_id'] = admin.id
            session['user_name'] = admin.username
            session['role'] = 'admin'
            print(f"✅ Admin login successful: {admin.username}")
            return redirect(url_for('admin_dashboard'))
        else:
            print("❌ Admin login failed")
            return render_template('admin_login.html', error="Invalid username or password")
    
    return render_template('admin_login.html')

# ========== DASHBOARD ROUTES ==========

@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard using your student_dashboard.html"""
    # Check if user is logged in as student
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('student_login'))
    
    student_id = session['user_id']
    student_name = session['user_name']
    
    print(f"🎓 Loading dashboard for student: {student_name} (ID: {student_id})")
    
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
    
    print(f"📚 Student has {len(enrolled_courses)} enrolled courses")
    
    return render_template('student_dashboard.html', 
                         student_name=student_name,
                         courses=enrolled_courses)

@app.route('/teacher/dashboard')
def teacher_dashboard():
    """Teacher dashboard using professor_dashboard.html"""
    # Check if user is logged in as teacher
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('teacher_login'))

    teacher_id = session['user_id']
    teacher_name = session['user_name']

    print(f"👨‍🏫 Loading dashboard for teacher: {teacher_name} (ID: {teacher_id})")

    # Get courses taught by this teacher
    courses = Course.query.filter_by(teacher_id=teacher_id).all()

    # Build course data list
    course_data = []
    for course in courses:
        enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()

        course_data.append({
            'id': course.id,
            'name': course.name,
            'teacher_name': teacher_name,  # Show the professor name
            'enrollment_count': enrollment_count,
            'capacity': course.capacity
        })

    print(f"📖 Teacher has {len(course_data)} courses")

    return render_template(
        'professor_dashboard.html',
        professor_name=teacher_name,
        courses=course_data
    )

# ========== TEACHER COURSES ==========

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

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard using your admin_dashboard.html"""
    # Check if user is logged in as admin
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    # Get all courses with enrollment counts
    courses = Course.query.all()
    course_data = []
    
    for course in courses:
        enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()
        course_data.append({
            'id': course.id,
            'name': course.name,
            'professor': course.teacher.name,
            'students': enrollment_count,
            'capacity': course.capacity
        })
    
    print(f"👤 Admin dashboard loaded with {len(course_data)} courses")
    
    return render_template('admin_dashboard.html', classes=course_data)

@app.route('/student/register')
def student_register():
    """Class registration using your student_register.html"""
    # Check if user is logged in as student
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('student_login'))
    
    student_id = session['user_id']
    student_name = session['user_name']
    
    print(f"📝 Loading registration page for student: {student_name} (ID: {student_id})")
    
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
    
    print(f"📚 Passing {len(course_data)} courses to registration page")
    
    # Debug: print each course
    for course in course_data:
        print(f"   - {course['name']} by {course['professor']} ({course['enrolled']}/{course['capacity']})")
    
    return render_template('student_register.html', courses=course_data)

# ========== API ENDPOINTS ==========

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
    """API endpoint for course registration (for your student.js)"""
    if 'user_id' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Not logged in'}), 401
    
    student_id = session['user_id']
    student_name = session['user_name']
    course_id = request.json.get('courseId')
    
    print(f"🎯 Student {student_name} (ID: {student_id}) attempting to enroll in course {course_id}")
    
    # Check if course exists
    course = Course.query.get(course_id)
    if not course:
        print(f"❌ Course {course_id} not found")
        return jsonify({'error': 'Course not found'}), 404
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        student_id=student_id, course_id=course_id
    ).first()
    
    if existing_enrollment:
        print(f"❌ Student already enrolled in {course.name}")
        return jsonify({'error': 'Already enrolled in this course'}), 400
    
    # Check course capacity
    enrollment_count = Enrollment.query.filter_by(course_id=course_id).count()
    if enrollment_count >= course.capacity:
        print(f"❌ Course {course.name} is full ({enrollment_count}/{course.capacity})")
        return jsonify({'error': 'Course is full'}), 400
    
    # Create new enrollment
    new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
    db.session.add(new_enrollment)
    db.session.commit()
    
    print(f"✅ Successfully enrolled {student_name} in {course.name}")
    
    return jsonify({'message': 'Successfully enrolled in course'})

# Grades API endpoints for your index.html and script.js
@app.route('/api/grades', methods=['GET', 'POST'])
def api_grades():
    """Grades API for your script.js"""
    if request.method == 'GET':
        # Return all grades
        enrollments = Enrollment.query.filter(Enrollment.grade.isnot(None)).all()
        grades = {}
        for enrollment in enrollments:
            student = Student.query.get(enrollment.student_id)
            grades[student.name] = enrollment.grade
        
        print(f"📊 Returning {len(grades)} grades via API")
        return jsonify(grades)
    
    elif request.method == 'POST':
        # Add new grade
        data = request.json
        student_name = data.get('name')
        grade = data.get('grade')
        
        print(f"📝 Adding grade {grade} for student {student_name}")
        
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
            print(f"✅ Added grade {grade} for {student_name}")
            return jsonify({'message': 'Grade added successfully'})
        
        print(f"❌ Student {student_name} not found")
        return jsonify({'error': 'Student not found'}), 404

@app.route('/api/grades/<student_name>', methods=['GET', 'PUT', 'DELETE'])
def api_grade_student(student_name):
    """Individual student grade operations for your script.js"""
    print(f"📊 Grade operation for student: {student_name}")
    
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        print(f"❌ Student {student_name} not found")
        return jsonify({'error': 'Student not found'}), 404
    
    if request.method == 'GET':
        enrollment = Enrollment.query.filter_by(student_id=student.id).first()
        if enrollment and enrollment.grade:
            print(f"✅ Found grade {enrollment.grade} for {student_name}")
            return jsonify({student_name: enrollment.grade})
        print(f"❌ No grade found for {student_name}")
        return jsonify({'error': 'Grade not found'}), 404
    
    elif request.method == 'PUT':
        data = request.json
        new_grade = data.get('grade')
        
        enrollment = Enrollment.query.filter_by(student_id=student.id).first()
        if enrollment:
            enrollment.grade = new_grade
            db.session.commit()
            print(f"✅ Updated grade to {new_grade} for {student_name}")
            return jsonify({'message': 'Grade updated successfully'})
        
        print(f"❌ No enrollment found for {student_name}")
        return jsonify({'error': 'Enrollment not found'}), 404
    
    elif request.method == 'DELETE':
        enrollment = Enrollment.query.filter_by(student_id=student.id).first()
        if enrollment:
            enrollment.grade = None
            db.session.commit()
            print(f"✅ Deleted grade for {student_name}")
            return jsonify({'message': 'Grade deleted successfully'})
        
        print(f"❌ No enrollment found for {student_name}")
        return jsonify({'error': 'Enrollment not found'}), 404

# ========== UTILITY ROUTES ==========

@app.route('/logout')
def logout():
    """Logout all user types"""
    user_info = f"{session.get('user_name', 'Unknown')} ({session.get('role', 'Unknown')})"
    session.clear()
    print(f"🚪 User logged out: {user_info}")
    return redirect(url_for('student_login'))

@app.route('/debug/courses')
def debug_courses():
    """Debug route to check courses in database"""
    courses = Course.query.all()
    result = "<h2>Courses in Database:</h2><ul>"
    for course in courses:
        enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()
        teacher_name = course.teacher.name if course.teacher else "No Teacher"
        result += f"<li>{course.name} - {teacher_name} - {enrollment_count}/{course.capacity} (ID: {course.id})</li>"
    result += f"</ul><p>Total courses: {len(courses)}</p>"
    
    # Add students info
    students = Student.query.all()
    result += "<h3>Students:</h3><ul>"
    for student in students:
        enrollments = Enrollment.query.filter_by(student_id=student.id).count()
        result += f"<li>{student.name} - {student.email} (Enrollments: {enrollments})</li>"
    result += f"</ul><p>Total students: {len(students)}</p>"
    
    return result

@app.route('/debug/registration-data')
def debug_registration_data():
    """Debug route to see exactly what data is being passed to registration page"""
    if 'user_id' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Not logged in as student'})
    
    courses = Course.query.all()
    course_data = []
    
    for course in courses:
        enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()
        course_info = {
            'id': course.id,
            'name': course.name,
            'professor': course.teacher.name,
            'enrolled': enrollment_count,
            'capacity': course.capacity
        }
        course_data.append(course_info)
        print(f"📖 Course: {course_info}")  # This will print to console
    
    return jsonify(course_data)

@app.route('/debug')
def debug_info():
    """Debug page to check database state"""
    students = Student.query.all()
    teachers = Teacher.query.all()
    courses = Course.query.all()
    enrollments = Enrollment.query.all()
    
    info = f"""
    <h2>Debug Information</h2>
    <p>Students: {len(students)}</p>
    <p>Teachers: {len(teachers)}</p>
    <p>Courses: {len(courses)}</p>
    <p>Enrollments: {len(enrollments)}</p>
    
    <h3>Students:</h3>
    <ul>
    {"".join(f'<li>{s.name} - {s.email} (ID: {s.id})</li>' for s in students)}
    </ul>
    
    <h3>Teachers:</h3>
    <ul>
    {"".join(f'<li>{t.name} - {t.email} (ID: {t.id})</li>' for t in teachers)}
    </ul>
    
    <h3>Courses:</h3>
    <ul>
    {"".join(f'<li>{c.name} - Teacher: {c.teacher.name} (ID: {c.id})</li>' for c in courses)}
    </ul>
    
    <h3>Enrollments:</h3>
    <ul>
    {"".join(f'<li>Student {e.student_id} in Course {e.course_id} - Grade: {e.grade}</li>' for e in enrollments)}
    </ul>
    
    <h3>Session Info:</h3>
    <pre>{dict(session)}</pre>
    
    <p><a href="/">Home</a> | <a href="/debug/courses">Course Details</a></p>
    """
    return info

# ========== APPLICATION STARTUP ==========

if __name__ == '__main__':
    with app.app_context():
        # Create database and sample data
        create_sample_data()
    
    print("\n🎓 ACME University Web App Starting...")
    print("📍 Server running at: http://localhost:5000")
    print("\n📋 Available Logins:")
    print("   Student: cnorris@student.com / password")
    print("   Teacher: ahepworth@teacher.com / password")
    print("   Admin: admin / admin123")
    print("\n🐛 Debug Routes:")
    print("   http://localhost:5000/debug - Full database info")
    print("   http://localhost:5000/debug/courses - Course details")
    print("\n🚀 Ready to go!")
    
    app.run(debug=True, port=5000)