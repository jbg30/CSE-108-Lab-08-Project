# -----------------------------------------------
# app.py - Flask + SQLAlchemy backend for Lab 7
# Replaces students.json with a persistent SQLite database
# -----------------------------------------------

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import logging

# -----------------------
# Flask app setup
# -----------------------
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Allow frontend JS to talk to backend
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# -----------------------
# Database configuration
# -----------------------
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'grades.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------
# Student model
# -----------------------
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    grade = db.Column(db.String(10), nullable=False)

    def to_pair(self):
        return (self.name, self.grade)

# Create DB and table if not exist
with app.app_context():
    db.create_all()

# -----------------------
# HTML routes
# -----------------------
@app.route("/")
def home(): return render_template("index.html")

@app.route("/add")
def add(): return render_template("add.html")

@app.route("/delete")
def delete(): return render_template("delete.html")

@app.route("/search")
def search(): return render_template("search.html")

@app.route("/update")
def update(): return render_template("update.html")

# -----------------------
# REST API routes
# -----------------------

@app.route("/api/grades", methods=["GET"])
def get_all_grades():
    students = Student.query.all()
    return jsonify({s.name: s.grade for s in students})

@app.route("/api/grades/<name>", methods=["GET"])
def get_grade(name):
    student = Student.query.filter(Student.name.ilike(name)).first()
    if student:
        return jsonify({student.name: student.grade})
    return jsonify({"error": "Student not found"}), 404

@app.route("/api/grades", methods=["POST"])
def add_grade():
    data = request.get_json() or {}
    name = data.get("name")
    grade = data.get("grade")
    if not name or not grade:
        return jsonify({"error": "Missing name or grade"}), 400

    existing = Student.query.filter(Student.name.ilike(name)).first()
    if existing:
        existing.grade = grade
        db.session.commit()
        return jsonify({"message": "Student updated"}), 200

    new_student = Student(name=name, grade=grade)
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"message": "Student added"}), 201

@app.route("/api/grades/<name>", methods=["PUT"])
def update_grade_api(name):
    student = Student.query.filter(Student.name.ilike(name)).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json() or {}
    new_grade = data.get("grade")
    if not new_grade:
        return jsonify({"error": "Missing grade"}), 400

    student.grade = new_grade
    db.session.commit()
    return jsonify({"message": "Grade updated"})

@app.route("/api/grades/<name>", methods=["DELETE"])
def delete_grade_api(name):
    student = Student.query.filter(Student.name.ilike(name)).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": "Student deleted"})
    return jsonify({"error": "Student not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)