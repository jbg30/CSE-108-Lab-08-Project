from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, Student, Teacher, Admin as AdminUser, Course, Enrollment
from flask import session, redirect, url_for
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField

class StudentAdminView(ModelView):
    form_excluded_columns = ('password_hash',)
    form_extra_fields = {
        'password': PasswordField('Password')
    }

    def on_model_change(self, form, model, is_created):
        # If the password field is filled, hash it and store in password_hash
        if form.password.data:
            model.set_password(form.password.data)

class TeacherAdminView(ModelView):
    form_excluded_columns = ('password_hash',)
    form_extra_fields = {
        'password': PasswordField('Password')
    }

    def on_model_change(self, form, model, is_created):
        # If the password field is filled, hash it and store in password_hash
        if form.password.data:
            model.set_password(form.password.data)

def setup_admin(app):
    
    # Give the admin a unique endpoint name to avoid blueprint conflicts
    admin = Admin(app, name="ACME University Admin", endpoint="flask_admin")  

    # Custom ModelView to restrict access to real admins
    class SecureModelView(ModelView):
        def is_accessible(self):
            return session.get("role") == "admin"

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for("admin_login"))
                
    # models
    admin.add_view(StudentAdminView(Student, db.session, name="Students", endpoint="student_admin", category="Users"))
    admin.add_view(TeacherAdminView(Teacher, db.session, name="Teachers", endpoint="teacher_admin", category="Users"))
    admin.add_view(SecureModelView(AdminUser, db.session, category="Users"))
    admin.add_view(SecureModelView(Course, db.session, category="Courses"))
    admin.add_view(SecureModelView(Enrollment, db.session, category="Courses"))
