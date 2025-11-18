from werkzeug.security import generate_password_hash
from app import app, db, User, Course, Enrollment


def seed():
    with app.app_context():
        # Drop everything and recreate tables (careful: wipes data!)
        db.drop_all()
        db.create_all()

        # ---- Users ----
        s1 = User(
            username="mindy",
            full_name="Mindy Student",
            role="student",
            password_hash=generate_password_hash("mindy123"),
        )
        s2 = User(
            username="chuck",
            full_name="Chuck Student",
            role="student",
            password_hash=generate_password_hash("chuck123"),
        )
        t1 = User(
            username="ahepworth",
            full_name="Dr. Hepworth",
            role="teacher",
            password_hash=generate_password_hash("teacher123"),
        )
        admin = User(
            username="admin",
            full_name="ACME Admin",
            role="admin",
            password_hash=generate_password_hash("admin123"),
        )

        db.session.add_all([s1, s2, t1, admin])
        db.session.commit()

        # ---- Courses ----
        c1 = Course(code="CSE 108", title="Web Apps", capacity=30, teacher_id=t1.id)
        c2 = Course(code="CSE 162", title="Databases", capacity=25, teacher_id=t1.id)

        db.session.add_all([c1, c2])
        db.session.commit()

        # ---- Enrollments ----
        e1 = Enrollment(student_id=s1.id, course_id=c1.id, grade=None)
        e2 = Enrollment(student_id=s2.id, course_id=c2.id, grade="B+")

        db.session.add_all([e1, e2])
        db.session.commit()

        print("✅ Database seeded!")


if __name__ == "__main__":
    seed()
