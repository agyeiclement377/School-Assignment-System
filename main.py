from flask import Flask ,render_template ,request ,flash ,redirect ,url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import UserMixin
from sqlalchemy.sql import func
import json
from flask_login import LoginManager ,login_user ,login_required ,logout_user ,current_user 
from werkzeug.security import generate_password_hash ,check_password_hash
db = SQLAlchemy()
DB_NAME = "database.db"

def create_database(app):
    if not path.exists('School Assignment Website/' + DB_NAME):
        db.create_all(app=app)
        print('Create Database..!')

#--------------------------DATABASE MODELS-------------------------#
class Assignment(db.Model):
    id = db.Column(db.Integer ,primary_key=True)
    data = db.Column(db.String(10000))
    submissiondate = db.Column(db.String(10000))
    grade = db.Column(db.Integer)
    teacher_grade = db.Column(db.Integer ,db.ForeignKey('teacher.grade')) #Realtes User notes to a specific User
    student_grade = db.Column(db.Integer ,db.ForeignKey('student.grade')) #Realtes User notes to a specific User


class Teacher(db.Model ,UserMixin):
    id = db.Column(db.Integer ,primary_key = True)
    email = db.Column(db.String(150) ,unique=True)
    password = db.Column(db.String(150))
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    grade = db.Column(db.Integer)
    Assignment = db.relationship('Assignment') #Relates a user to a Note

class Student(db.Model ,UserMixin):
    id = db.Column(db.Integer ,primary_key = True)
    email = db.Column(db.String(150) ,unique=True)
    password = db.Column(db.String(150))
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    grade = db.Column(db.Integer)
    Assignment = db.relationship('Assignment') #Relates a user to a Note


#---------------------APP CONFIGURATIONS---------------------#
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
db.init_app(app)  #Initialize app
#db.drop_all(app=app)
create_database(app)

#---------------------MANAGE LOGINS---------------------------#

login_manager = LoginManager()
login_manager.login_view = 'loginadmin'
login_manager.login_view = 'loginstudent'
login_manager.init_app(app)

@login_manager.user_loader
def load_student(id):
    return Student.query.get(int(id))
def load_teacher(id):
    return Teacher.query.get(int(id))



#----Home Page----#
@app.route('/')
def home():
    return render_template('home.html' )


#----Student Page----#
@app.route('/studentpage')  
def studentpage():
    assignments = Assignment.query.filter_by(grade = current_user.grade)
    return render_template('studentpage.html' ,user=current_user , assignments=assignments )


#----Admin Page----#
assignments = ''
@app.route('/adminpage' ,methods = ['GET' ,'POST'])
def adminpage():
    if request.method == "POST":
        data = request.form.get('data')
        grade = request.form.get('grade')
        submissiondate = request.form.get('submissiondate')
        email = request.form.get('email')

        teacher = Teacher.query.filter_by(email=email).first()

        new_assignment = Assignment(data=data ,grade=grade ,submissiondate=submissiondate ,teacher_grade = teacher.grade)
        db.session.add(new_assignment)
        db.session.commit()
        flash("New Assignment Added" ,category="success")

        global assignments
        assignments = teacher.Assignment
        print(assignments)
        
        
    return render_template('adminpage.html' ,Assignments = assignments )

#----------LOGOUT PAGES---------#
#Made two logout pages because login_user doesnt seem to work for admin

#----Logout Page Admin----#
@app.route('/logoutadmin')
def logoutadmin():
    logout_user()
    return redirect(url_for('home'))

#----Logout Page Student----#
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#----Admin Login ----#
@app.route('/loginadmin' ,methods = ["GET" ,"POST"])
def loginadmin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password1')

        #Querying info
        teacher = Teacher.query.filter_by(email=email).first()
        if teacher:
            if check_password_hash(teacher.password , password):
                flash("Admin Logged in Successfully!" ,category='success')
                login_user(teacher ,remember=True)
                return redirect(url_for('adminpage'))

            else:
                flash("Wrong Password." ,category='error')
        else:
            flash("Account Not found. Create an account Here", category="error")
            return redirect(url_for('signup'))

    
    return render_template("loginadmin.html" ,user = current_user)


#----Student Login----#'

@app.route('/loginstudent' ,methods = ["GET" ,"POST"])
def loginstudent():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password1')
        grade = request.form.get('grade')

        #Querying info
        student = Student.query.filter_by(email=email).first()
        if student:
            if check_password_hash(student.password , password):
                flash("Student Logged in Successfully!" ,category='success')
                login_user(student ,remember=True)
                return redirect(url_for('studentpage') )

            else:
                flash("Wrong Password." ,category='error')
        else:
            flash("Account Not found. Create an account Here", category="error")
            return redirect(url_for('signup'))


    return render_template("loginstudent.html" ,user = current_user)



#----Sign Up Page----#
@app.route('/signup' ,methods=["GET" ,"POST"])
def signup():
    
    if request.method == "POST":
        status = request.form.get('status').lower()
        if status=="teacher":
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            grade = request.form.get('grade')

            teacher = Teacher.query.filter_by(email=email).first()
            if teacher:
                flash('Email already exists.Try logging in' ,category='error')
                return redirect(url_for("loginadmin"))


            elif len(email) < 4:
                flash('Email must be greater than 4 characters.' ,category='error')
            elif len(firstname) < 2:
                flash('First Name must be greater than 1 character.' ,category='error')
            elif password1 != password2:
                flash('Passwords do not match',category='error')
            elif len(password1) < 5:
                print('less')
                flash('Password must be at least 7 characters.' ,category='error')
            else:
                new_teacher = Teacher(email=email ,firstname=firstname ,lastname=lastname, grade=grade,password=generate_password_hash(password1 ,method='sha256'))
            
                db.session.add(new_teacher)
                db.session.commit()
                flash('Account Created!' ,category="success")

                return redirect(url_for('loginadmin'))
        elif status=="student":
            
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            grade = request.form.get('grade')

            student = Student.query.filter_by(email=email).first()
            if student:
                flash('Email already exists.' ,category='error')


            elif len(email) < 4:
                flash('Email must be greater than 4 characters.' ,category='error')
            elif len(firstname) < 2:
                flash('First Name must be greater than 1 character.' ,category='error')
            elif password1 != password2:
                flash('Passwords do not match',category='error')
            elif len(password1) < 5:
                print('less')
                flash('Password must be at least 7 characters.' ,category='error')
            else:
                new_student = Student(email=email ,firstname=firstname ,lastname=lastname, grade=grade,password=generate_password_hash(password1 ,method='sha256'))
            
                db.session.add(new_student)
                db.session.commit()
                flash('Account Created!' ,category="success")
                return redirect(url_for('loginstudent'))
        else:
            flash("Student or a Teacher?", category="error")

        
                



            
    return render_template('signup.html' ,user=current_user)

#-----DELETE NOTES -----#
@app.route('/deletenote' ,methods=['GET','POST'])
def deletenote():
    email = request.form.get('email')
    assignmentdata = request.form.get('assignmentdata')
    assignment = Assignment.query.filter_by(data=assignmentdata).first()

    teacher = Teacher.query.filter_by(email=email).first()

    if teacher :
        if assignment:
            db.session.delete(assignment)
            db.session.commit()
            flash("Assignment Deleted" ,category='success')
            assignments = teacher.Assignment

            return render_template('adminpage.html' ,Assignments=assignments)
        else :
            flash("Assignment Not found" ,category='error')
    else:
        flash("Account not found, Try again" ,category='error')
    
    return render_template('deletepage.html')

    

if __name__ == "__main__":
    app.run(debug=True ,port=4996)
