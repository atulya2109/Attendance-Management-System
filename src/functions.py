from base import db, User, Teachers, Students, Class, Subject, Attendance
from functools import wraps
from flask_login import current_user
from base import login_manager
import json
from datetime import datetime

def login_required(role = 'ANY'):

    def wrapper(fn):

        @wraps(fn)

        def decorated_view(*args,**kwargs):

            if current_user.get_id() == None:
                return login_manager.unauthorized()

            if current_user.getRole() != role and role != 'ANY':
                return login_manager.unauthorized()
            
            return fn(*args,**kwargs)
        
        return decorated_view
    return wrapper

def loginStudent(usrname,pswrd):
    
    user = User.query.filter_by(id = usrname, pwd = pswrd, role = 'Student').first()

    if user != None:
        student = Students.query.filter_by(id = user.id).first() 
        return user

    return None

def loginTeacher(usrname,pswrd):
    
    user = User.query.filter_by(id = usrname, pwd = pswrd, role = 'Teacher').first()

    if user != None:
        teacher = Teachers.query.filter_by(id = user.id).first() 
        return user

    return None

def loginAdmin(usrname,pswrd):

    user = User.query.filter_by(id = usrname, pwd = pswrd, role = 'Admin').first()
    return user

def createTeacher(info_dict):

    name = info_dict['tc_name']
    username = info_dict['tc_id']
    passkey = info_dict['tc_pass']
    subject = info_dict['tc_course']
    newTeacher = Teachers(name = name,id = username)
    newUser = User(id = username, pwd = passkey,role = 'Teacher')

    for key,pair in info_dict.items():

        if key.startswith('Section_name'):
            sec = pair
            sem = info_dict[f'Semester_name{key[12:]}']
        
            classroom = Class.query.filter_by(section = sec, semester = sem).first()
            sub = Subject.query.filter_by(name = subject).first()

            if classroom == None:
                classroom = createClass(sec,sem)
            
            if sub == None:
                sub = createSubject(subject)

            classroom.subjects.append(sub)
            newTeacher.classes.append(classroom)
            newTeacher.subject = sub.id
    
    db.session.add(newTeacher)
    db.session.add(newUser)
    db.session.commit()

def createStudent(name,usrname,passkey,sec,sem):
    
    newUser = User(id = usrname, pwd = passkey,role = 'Student')
    clssroom = Class.query.filter_by(section = sec, semester = sem).first()
    newStudent = Students(name = name,id = usrname, classroom = clssroom)
    db.session.add(newUser)
    db.session.add(newStudent)
    db.session.commit()

def createClass(sec, sem):

    newClass = Class(section = sec,semester = sem)
    db.session.add(newClass)
    db.session.commit()
    return newClass

def createSubject(subject):

    newSubject = Subject(name = subject)
    db.session.add(newSubject)
    db.session.commit()
    return newSubject

def getStudents(sec, sem):
    clssroom = Class.query.filter_by(section = sec, semester = sem).first()

    classStudents = clssroom.classStudents
    students = {}
    stlist = []

    for student in classStudents:

        stdict = {
            'id': student.id,
            'name': student.name
        }
        stlist.append(stdict)

    students['students'] = stlist
    return students

def addAttendance(data,id):

    sub_id = Teachers.query.filter_by(id = id).first().subject

    students = data['students']

    for student in students:

        date = datetime.strptime(data['date'],"%Y-%m-%d").date()
        # print(student['id'])
        std_id = int(student['id'])
        newAttend = Attendance(date = date, student = std_id,subject = sub_id,present = student['present'])
        db.session.add(newAttend)
    
    db.session.commit()
    
def getStudentAttendance(id):

    classroom = Students.query.filter_by(id = id).first().classroom_id
    subjects = Class.query.filter_by(id = classroom).first().subjects

    subs = []

    for subject in subjects:
        subject_name = subject.name
       
        total = len(Attendance.query.filter_by(student = id, subject = subject.id).all())
        present = len(Attendance.query.filter_by(student = id, subject = subject.id, present = 1).all())
        
        if total == 0:
            pct = 'NA'

        else:
            pct = present*100/total

        subs.append({
            'subject':subject_name,
            'attendance':pct
        })

    return subs