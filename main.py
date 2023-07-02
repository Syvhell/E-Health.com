from itertools import groupby
from operator import itemgetter
from flask import Flask, render_template, request, redirect,url_for,jsonify,session,flash
from flask_mysqldb import MySQL, MySQLdb
from flask_mail import Mail, Message
from config import mail_username,mail_password
from werkzeug.utils import secure_filename
import os
import urllib.request
from datetime import datetime,timedelta
import random
import string

app = Flask(__name__)

app.secret_key = "Group3CapstoneProject"

app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'clinic_system'






# Configure the email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'qsuclinic@gmail.com'  # Replace with your Gmail username
app.config['MAIL_PASSWORD'] = 'ywapjaclfciagmdw'  # Replace with your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'qsuclinic@gmail.com'  # Replace with your Gmail username
mail = Mail(app)


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

mysql = MySQL(app)




#-------------------------------------------------------------------------------Images----------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





#-------------------------------------------------------------------------------LANDINGPAGE----------------------------------
@app.route('/', methods=['POST','GET'])
def landingpage():
    staffs = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    staffs.execute('SELECT * FROM tbl_moderator ORDER BY id')
    staff = staffs.fetchall()
    doc = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    doc.execute('SELECT * FROM tbl_headmoderator ORDER BY id')
    docs = doc.fetchall()
    return render_template('Landingpage/outindex.html',staff=staff,docs=docs)


#----------------------------------------------------------------------------------HEADMODERATOR-----------------------------------------------------------

@app.route('/headmoderator/login', methods=['POST','GET'])
def headmoderator_login():
    return render_template('headmoderator/login.html')

@app.route('/headmoderator/loginexecute', methods=['POST','GET'])
def headmoderator_loginexecute():
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE idnumber =%s AND password = %s ', (idnumber, password))
        account = cursor.fetchone()
        if account:
            cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND idnumber = %s', (0, idnumber))
            not_approved = cursor.fetchone()
            if not_approved:
                return render_template('headmoderator/login.html',error='Your Account is NOT Yet Approved')
            else:
                session['loggedin'] = True
                session['id'] = account['id']
                session['status'] = account['status']
                return redirect(url_for('headmoderator_dashboard'))
    return render_template('headmoderator/login.html')

@app.route('/headmoderator/admin-dashboard', methods=['POST','GET'])
def headmoderator_dashboard():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')

    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students ORDER BY id')
        studentapproval = cursorapprove.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER BY id')
        appointments = appointment.fetchall()
        cur = mysql.connection.cursor()
        status = 2
        cur.execute('SELECT COUNT(*) FROM tbl_moderator WHERE status= %s',[status])
        result = cur.fetchone()
        user_count = result[0]
        cur.close()
        status = 3
        cur1 = mysql.connection.cursor()
        cur1.execute('SELECT COUNT(*) FROM tbl_students WHERE status= %s',[status])
        result = cur1.fetchone()
        user_count1 = result[0]
        cur1.close()
        cur2 = mysql.connection.cursor()
        cur2.execute('SELECT COUNT(*) FROM tbl_appointments')
        result = cur2.fetchone()
        user_count2 = result[0]
        cur2.close()
        status = 4
        cur3 = mysql.connection.cursor()
        cur3.execute('SELECT COUNT(*) FROM tbl_students WHERE status= %s',[status])
        result = cur3.fetchone()
        user_count3 = result[0]
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
        cur1.close()

    return render_template('headmoderator/index.html',Notification=Notification,admin=admin,studentapproval=studentapproval, appointments=appointments,user_count=user_count,user_count1=user_count1,user_count2=user_count2,user_count3 =user_count3 )



@app.route('/headmoderator/profile', methods=['POST','GET'])
def headmoderator_profile():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/profile.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/edit-profile', methods=['POST','GET'])
def headmoderator_edit_profile():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('headmoderator/edit-profile.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/patients',methods=['POST','GET'])
def headmoderator_patients():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_medical ORDER BY Date')
        medical = appointment.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/patients.html', admin=admin,medical=medical,Notification=Notification)




@app.route('/headmoderatorsearchpatient', methods=['POST'])
def headmoderatorsearchpatient():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_medical ORDER BY Date')
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if request.method == 'POST':
        query = request.form['search_query']
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute("SELECT * FROM tbl_medical WHERE idnumber LIKE %s", ("%" + query + "%",))
        results = cursor1.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE First_name LIKE %s", ("%" + query + "%",))
        resultsname = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Middle_name LIKE %s", ("%" + query + "%",))
        resultsmiddlename = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Last_name LIKE %s", ("%" + query + "%",))
        resultslastname = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Title LIKE %s", ("%" + query + "%",))
        resultslasttitle = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Treatment LIKE %s", ("%" + query + "%",))
        resultstreatment = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Diagnosis LIKE %s", ("%" + query + "%",))
        resultsdiagnosis = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Date LIKE %s", ("%" + query + "%",))
        resultsdate = cursor.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
        return render_template('headmoderator/patients_search.html', Notification=Notification,query=query, results=results,resultsname =resultsname, resultslastname =resultslastname,admin=admin,appointments=appointments,resultslasttitle=resultslasttitle,resultsmiddlename=resultsmiddlename,resultstreatment=resultstreatment,resultsdiagnosis=resultsdiagnosis,resultsdate=resultsdate)






@app.route('/headmoderator/add-patient' , methods=['POST','GET'])
def headmorator_add_patients():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/add-patient.html', admin=admin,Notification=Notification)



@app.route('/headmoderator/add-patient-execute', methods=['post','get'])
def headmoderator_add_patient_execute():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        Physician = request.form['firstname']
        Year_level = request.form['Year_level']
        Course = request.form['Course']
        idnumber = request.form['id_number']
        First_name = request.form['First_name']
        Middle_name = request.form['Middle_name']
        Last_name = request.form['Last_name']
        Cp_number = request.form['Cp_number']
        Home_Address = request.form['Home_Address']
        date = request.form['date']
        Gender = request.form['Gender']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        title = request.form['title']
        cur.execute("INSERT INTO tbl_medical (Physician ,Year_level,Course,idnumber,First_name,Middle_name,Last_name,Cp_number,Address,Date,Gender,Diagnosis,Treatment,Title) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[Physician ,Year_level,Course,idnumber,First_name,Middle_name,Last_name,Cp_number,Home_Address,date,Gender,diagnosis,treatment,title])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('headmorator_add_patients'))


@app.route('/get_names', methods=['POST'])
def get_names():
    id_number = request.form['id_number']
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT idnumber, Email,Year_level,Course,First_name ,Middle_name,Last_name ,Cp_number ,Gender,Home_Address FROM tbl_students WHERE idnumber = %s", (id_number,))
    if result > 0:
        data = cursor.fetchone()
        idnumber = data[0]
        email = data[1]
        yearlevel=data[2]
        course = data[3]
        firstname = data[4]
        middlename = data[5]
        lastname = data[6]
        Cp_number = data[7]
        Gender = data[8]
        address = data[9]

        return jsonify({'idnumber': idnumber, 'email': email,'yearlevel':yearlevel,'course':course,'firstname':firstname,'middlename':middlename,'lastname':lastname,'Cp_number':Cp_number,'Gender':Gender,'address':address})
    else:
        return jsonify({'name': '', 'email': '','yearlevel':'','course':'','firstname':'','middlename':'','lastname':'','Cp_number':'','Gender':'','address':''})




@app.route('/headmoderator/add-visitor-patient' , methods=['POST','GET'])
def headmoderator_add_visitor_patients():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/add-visitor-patient.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/add-visitor-patient-execute', methods=['post','get'])
def headmoderator_add_visitor_patient_execute():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        idnumber = request.form['id_number']
        Physician = request.form['firstname']
        First_name = request.form['First_name']
        Middle_name = request.form['Middle_name']
        Last_name = request.form['Last_name']
        Cp_number = request.form['Cp_number']
        Home_Address = request.form['Home_Address']
        date = request.form['date']
        Gender = request.form['Gender']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        Title = 'Walkin Patient'
        cur.execute("INSERT INTO tbl_medical (idnumber,Physician ,First_name,Middle_name,Last_name,Cp_number,Address,Date,Gender,Diagnosis,Treatment,Title) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idnumber,Physician ,First_name,Middle_name,Last_name,Cp_number,Home_Address,date,Gender,diagnosis,treatment,Title])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('headmoderator_add_visitor_patients'))

@app.route('/headmoderator/appointment-add-patient-execute-status1/<int:id>', methods=['post','get'])
def headmoderator_appointment_add_patient_execute_status1(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    status1 = 7
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_appointments SET status1 = %s WHERE id = %s', (status1, id))
    mysql.connection.commit()
    return redirect(url_for('headmoderator_appointments'))






@app.route('/headmoderator/staff-list' , methods=['POST','GET'])
def headmorator_staff_list():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        cursorapprove.execute('SELECT * FROM tbl_moderator ORDER BY id')
        admin = cursor.fetchone()
        moderatorapproval = cursorapprove.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/staff-list.html',moderatorapproval=moderatorapproval, admin=admin,Notification=Notification)

@app.route('/headmoderator/approve-user/<int:id>')
def headmoderator_approve(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    status = 2
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_moderator SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()
    return redirect(url_for('headmorator_staff_list'))

@app.route('/headmoderator/disapprove-user/<int:id>')
def headmoderator_remove_access(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    status = 0
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_moderator  SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()
    return redirect(url_for('headmorator_staff_list'))

@app.route('/headmoderator/add-staff' , methods=['POST','GET'])
def headmorator_add_staff():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/add-staff.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/add-staff-execute', methods=['post','get'])
def headmoderator_add_staff_execute():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        gender = request.form['gender']
        password = request.form['password']
        cur2.execute('SELECT * FROM tbl_moderator WHERE idnumber = %s', (idnumber,))
        result2 = cur2.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
        if result2:
            return render_template('headmoderator/add-staff.html', error2='ID-Number already exist!',Notification=Notification)
        else:
            cur.execute(
                "INSERT INTO tbl_moderator (idnumber,First_name,Middle_name,Last_name,gender,password) VALUES (%s,%s,%s,%s,%s,%s)",
                [idnumber,firstname,middlename,lastname,gender,password])
            mysql.connection.commit()
            cur.close()
            return render_template('headmoderator/add-staff.html',Notification=Notification, message='Successfully Added!', admin=admin)

@app.route('/headmoderator/staff-profile' , methods=['POST','GET'])
def headmorator_staff_profile():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('headmoderator/staff-profile.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/appointments' , methods=['POST','GET'])
def headmoderator_appointments():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE status1=%s ORDER BY Start_date_time',(5,))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('headmoderator/appointments.html', appointments=appointments, admin=admin,Notification=Notification)


@app.route('/headmoderator/appointments-success' , methods=['POST','GET'])
def headmoderator_appointments_success():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE status1=%s ORDER BY Start_date_time',(6,))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('headmoderator/appointments-success.html', appointments=appointments, admin=admin,Notification=Notification)



@app.route('/headmoderator/appointments-canceled' , methods=['POST','GET'])
def headmoderator_appointments_canceled():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE status1=%s ORDER BY Start_date_time',(8,))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('headmoderator/appointments-canceled.html', appointments=appointments, admin=admin,Notification=Notification)



@app.route('/headmoderator/appointments-due' , methods=['POST','GET'])
def headmoderator_appointments_due():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE status1=%s ORDER BY Start_date_time',(7,))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('headmoderator/appointments-due.html', appointments=appointments, admin=admin,Notification=Notification)

@app.route('/headsearch', methods=['POST'])
def headsearch():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER BY id')
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if request.method == 'POST':
        query = request.form['search_query']
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute("SELECT * FROM tbl_appointments WHERE ID_Number LIKE %s", ("%" + query + "%",))
        results = cursor1.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE firstname LIKE %s", ("%" + query + "%",))
        resultsname = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE middlename LIKE %s", ("%" + query + "%",))
        resultsmiddlename = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE lastname LIKE %s", ("%" + query + "%",))
        resultslastname = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE email LIKE %s", ("%" + query + "%",))
        resultsemail = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE Title LIKE %s", ("%" + query + "%",))
        resultstitle = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE Start_date_time LIKE %s", ("%" + query + "%",))
        resultsStart_date_time = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE status LIKE %s", ("%" + query + "%",))
        resultsstatus = cursor.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
        return render_template('headmoderator/appointments_search.html', Notification=Notification,query=query, results=results,resultsname =resultsname, resultslastname =resultslastname,admin=admin,appointments=appointments,resultsmiddlename=resultsmiddlename,resultsemail =resultsemail,resultstitle =resultstitle,resultsStart_date_time=resultsStart_date_time,resultsstatus=resultsstatus  )







@app.route('/headrange', methods=['POST','GET'])
def headrange():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    if request.method == 'POST':
        From = request.form['From']
        to = request.form['to']
        print(From)
        print(to)
        query = "SELECT * from tbl_appointments WHERE end_date_unavailable BETWEEN '{}' AND '{}'".format(From, to)
        cur.execute(query)
        ordersrange = cur.fetchall()
    return jsonify({'htmlresponse': render_template('headmoderator/response.html', ordersrange=ordersrange,Notification=Notification)})



@app.route('/headmoderator/add-appointment' , methods=['POST','GET'])
def headmoderator_add_appointment():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/add-appointment.html', admin=admin,Notification=Notification)



@app.route('/headmoderator/add-appointment-execute', methods=['post','get'])
def headmoderator_add_appointment_execute():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if request.method == 'POST':
        date_str = request.form['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        title = request.form['title']
        cur.execute('SELECT * FROM disabled_dates WHERE date = %s', (date_obj,))
        result = cur.fetchone()
        if result:
            return render_template('headmoderator/add-appointment.html', admin=admin, error='Date is already Disabled!!')
        else:
            cur.execute(
                "INSERT INTO disabled_dates (date,Title) VALUES (%s,%s)",
                [date_obj,title ])
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('headmoderator_add_appointment',error='Disabled succefully!!'))




@app.route('/headmoderator/appoinement-add-patient/<int:id>' , methods=['POST','GET'])
def headmoderator_appointment_add_patients(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment_patient = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment_patient.execute('SELECT * FROM tbl_appointments WHERE id = %s', (id,))
        appointment = appointment_patient.fetchone()
    return render_template('headmoderator/appointment-add-patient.html', admin=admin,appointment=appointment,Notification=Notification)



@app.route('/headmoderator/appointment-add-patient-execute/<int:id>', methods=['post','get'])
def headmoderator_appointment_add_patient_execute(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        Physician = request.form['Firstname']
        Year_level = request.form['yearlevel']
        Course = request.form['course']
        idnumber = request.form['idnumber']
        First_name = request.form['firstname']
        Middle_name = request.form['middlename']
        Last_name = request.form['lastname']
        Cp_number = request.form['Cp_number']
        Home_Address = request.form['address']
        date = request.form['date']
        Gender = request.form['Gender']
        Title = request.form['title']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        status = 'Appointment Rendered'
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status = %s WHERE id = %s', (status, id))
        mysql.connection.commit()
        status1 = 6
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status1 = %s WHERE id = %s', (status1, id))
        mysql.connection.commit()
        cur.execute("INSERT INTO tbl_medical (Physician,Year_level,Course,idnumber,First_name,Middle_name,Last_name,Cp_number,Address,Date,Gender,Title,Diagnosis,Treatment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[Physician ,Year_level,Course,idnumber,First_name,Middle_name,Last_name,Cp_number,Home_Address,date,Gender,Title ,diagnosis,treatment])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('headmoderator_appointments'))



@app.route('/headmoderator/add-appointment-dentist' , methods=['POST','GET'])
def headmoderator_add_appointment_dentist():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/add-appointment-dental.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/add-appointment-execute-dental', methods=['post','get'])
def headmoderator_add_appointment_execute_dental():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    if request.method == 'POST':
        date_str = request.form['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        title = request.form['title']
        cur.execute('SELECT * FROM disabled_dates_dental WHERE date = %s', (date_obj,))
        result = cur.fetchone()
        if result:
            return render_template('headmoderator/add-appointment.html',Notification=Notification, admin=admin, error='Date is already Disabled!!')
        else:
            cur.execute(
                "INSERT INTO disabled_dates_dental (date,Title) VALUES (%s,%s)",
                [date_obj,title ])
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('headmoderator_add_appointment_dentist',error='Disabled Succesfully!!'))






@app.route('/headmoderator/calendar' , methods=['POST','GET'])
def headmorator_calendar():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER BY id')
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('headmoderator/calendar.html',Notification=Notification, appointments=appointments, admin=admin)

@app.route('/headmoderator/compose' , methods=['POST','GET'])
def headmorator_compose():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        status = 'Appointment Canceled'
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status = %s WHERE id = %s', (status, id))
        mysql.connection.commit()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/compose.html',Notification=Notification, admin=admin)


@app.route('/headmoderator/compose-cancel/<int:id>' , methods=['POST','GET'])
def headmorator_compose_cancel(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_appointments WHERE id = %s', (id,))
        mail = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()

    return render_template('headmoderator/compose-cancel.html', admin=admin,mail=mail,Notification=Notification)


@app.route('/headmoderator/send_email/recipient', methods=['POST'])
def headmoderator_send_email_recipient():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        recipient = request.form['recipient']
        message = request.form['textarea']

        # Create the message
        msg = Message(subject='New message from your school Clinic',
                      recipients=[recipient])  # Replace with your email address
        msg.body = f"You have received a new message from :{name} \n\n{message}"

        try:
            # Send the message
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending your message: {e}', 'error')

    return redirect(url_for('headmorator_appointments'))




@app.route('/headmoderator/send_email', methods=['POST'])
def headmoderator_send_email():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        recipient = request.form['recipient']
        message = request.form['textarea']

        # Create the message
        msg = Message(subject='New message from your school Clinic',
                      recipients=[recipient])  # Replace with your email address
        msg.body = f"You have received a new message from {name}: \n\n{message}"

        try:
            # Send the message
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending your message: {e}', 'error')

    return render_template('headmoderator/compose.html', admin=admin,Notification=Notification)



@app.route('/headmoderator/approve-student',methods=['POST','GET'])
def headmoderator_approve_student():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_students ORDER BY id')
        approve = appointment.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/approve-students.html', admin=admin,approve=approve,Notification=Notification)

@app.route('/head_moderator/approve-user/<int:id>')
def head_moderator_approve(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    status = 3
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_students SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()

    return redirect(url_for('headmoderator_approve_student'))

@app.route('/head_moderator/disapprove-user/<int:id>')
def head_moderator_remove_access(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    status = 0
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_students  SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()
    return redirect(url_for('headmoderator_approve_student'))



@app.route('/head_moderator/faculty_approve-user/<int:id>')
def head_moderator_faculty_approve(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    status = 4
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_students SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()
    return redirect(url_for('headmoderator_approve_faculty'))

@app.route('/head_moderator/faculty_disapprove-user/<int:id>')
def head_moderator_faculty_remove_access(id):
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    status = 0
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_students  SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()
    return redirect(url_for('headmoderator_approve_faculty'))




@app.route('/headmoderator/approve-faculty',methods=['POST','GET'])
def headmoderator_approve_faculty():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_students ORDER BY id')
        approve = appointment.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/approve-faculty.html', admin=admin,approve=approve,Notification=Notification)




@app.route('/headmoderator/inbox' , methods=['POST','GET'])
def headmorator_inbox():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/inbox.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/mail-view' , methods=['POST','GET'])
def headmorator_mail_view():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/mail-view.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/blog' , methods=['POST','GET'])
def headmorator_blog():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/blog.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/blog-details' , methods=['POST','GET'])
def headmorator_blog_details():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/blog-details.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/add-blog' , methods=['POST','GET'])
def headmorator_add_blog():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/add-blog.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/add-blog/execute' , methods=['POST','GET'])
def headmorator_add_blog_execute():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        subcategory = request.form['subcategory']
        tags = request.form['tags']
        gender = request.form['gender']
        about = request.form['about']
        image = request.form['image']
        cur.execute(
            "INSERT INTO tbl_blog (title,author,category,subcategory,tags,gender,about,image) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            [title,author,category,subcategory,tags,gender,about,image])
        mysql.connection.commit()
        cur.close()
        return render_template('headmoderator/add-blog.html', message='Successfully Added!', admin=admin,Notification=Notification)
    return render_template('headmoderator/add-blog.html', admin=admin,Notification=Notification)


@app.route('/headmoderator/edit-blog' , methods=['POST','GET'])
def headmorator_edit_blog():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/edit-blog.html', admin=admin,Notification=Notification)




@app.route('/headmoderator/patient-reports' , methods=['POST','GET'])
def headmoderator_patient_reports():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
    cur = mysql.connection.cursor()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()

    # Execute queries to retrieve the student counts for each month and course
    cur.execute(
        "SELECT Date, Course, Gender, COUNT(*) as count FROM tbl_medical GROUP BY Date, Course, Gender"
    )
    month_order = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    results = cur.fetchall()

    # Create a list of tuples to store the counts per month and course
    counts_per_month_course = []

    # Iterate over the results and populate the list
    for row in results:
        Date = row[0]
        Course = row[1]
        Gender = row[2]
        count = row[3]

        if Date is None:
            continue

        month = Date.strftime('%B')

        # Check if the month already exists in the list
        for i, (m, c) in enumerate(counts_per_month_course):
            if m == month:
                # Check if the course already exists for this month
                if Course in c:
                    c[Course][Gender] = count
                else:
                    c[Course] = {'Male': 0, 'Female': 0}
                    c[Course][Gender] = count
                break
        else:
            # Add a new tuple for this month
            counts_per_month_course.append((month, {Course: {'Male': 0, 'Female': 0}}))
            counts_per_month_course[-1][1][Course][Gender] = count

    # Sort the list by month name using the custom sorting order
    counts_per_month_course.sort(key=lambda x: month_order[x[0]])

    # Calculate the total counts per course
    total_counts_per_course = {}
    for _, courses in counts_per_month_course:
        for course, counts in courses.items():
            if course not in total_counts_per_course:
                total_counts_per_course[course] = {'Male': 0, 'Female': 0}
            total_counts_per_course[course]['Male'] += counts['Male']
            total_counts_per_course[course]['Female'] += counts['Female']

    # Calculate the total counts per month
    total_counts_per_month = {}
    for month, courses in counts_per_month_course:
        if month not in total_counts_per_month:
            total_counts_per_month[month] = {'Male': 0, 'Female': 0}
        for counts in courses.values():
            total_counts_per_month[month]['Male'] += counts['Male']
            total_counts_per_month[month]['Female'] += counts['Female']

    # Calculate the total counts for the whole year
    total_year_male = sum(total_counts_per_month[month]['Male'] for month in total_counts_per_month)
    total_year_female = sum(total_counts_per_month[month]['Female'] for month in total_counts_per_month)

    # Close the database connection
    cur.close()

    # Establish a database connection
    cur = mysql.connection.cursor()

    # Execute query to retrieve the student counts per title and gender
    cur.execute(
        "SELECT Title, Gender, COUNT(*) as count FROM tbl_medical GROUP BY Title, Gender"
    )
    results = cur.fetchall()

    # Create a dictionary to store the counts per title and gender
    counts_per_title_gender = {}

    # Iterate over the results and populate the dictionary
    for row in results:
        services = row[0]
        gender = row[1]
        count = row[2]

        if services not in counts_per_title_gender:
            counts_per_title_gender[services] = {'Male': 0, 'Female': 0}

        counts_per_title_gender[services][gender] = count

    # Calculate the total counts
    total_counts = {'Male': 0, 'Female': 0}
    for counts in counts_per_title_gender.values():
        total_counts['Male'] += counts['Male']
        total_counts['Female'] += counts['Female']

    # Close the database connection






    # Render the template and pass the counts as template variables
    return render_template(
        'headmoderator/patient-reports.html',Notification=Notification,admin=admin,
        counts_per_month_course=counts_per_month_course,
        total_counts_per_course=total_counts_per_course,
        total_counts_per_month=total_counts_per_month,
        total_year_male=total_year_male,
        total_year_female=total_year_female,counts_per_title_gender=counts_per_title_gender, total_counts=total_counts
    )



@app.route('/headmoderator/patient-reports-monthly' , methods=['POST','GET'])
def headmoderator_patient_reports_monthly():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
    cur = mysql.connection.cursor()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    cur.execute(
        "SELECT Date, Course, Gender, COUNT(*) as count FROM tbl_medical GROUP BY Date, Course, Gender"
    )
    month_order = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    results = cur.fetchall()

    # Create a list of tuples to store the counts per month and course
    counts_per_month_course = []

    # Iterate over the results and populate the list
    for row in results:
        Date = row[0]
        Course = row[1]
        Gender = row[2]
        count = row[3]

        if Date is None:
            continue

        month = Date.strftime('%B')

        # Check if the month already exists in the list
        for i, (m, c) in enumerate(counts_per_month_course):
            if m == month:
                # Check if the course already exists for this month
                if Course in c:
                    c[Course][Gender] = count
                else:
                    c[Course] = {'Male': 0, 'Female': 0}
                    c[Course][Gender] = count
                break
        else:
            # Add a new tuple for this month
            counts_per_month_course.append((month, {Course: {'Male': 0, 'Female': 0}}))
            counts_per_month_course[-1][1][Course][Gender] = count

    # Sort the list by month name using the custom sorting order
    counts_per_month_course.sort(key=lambda x: month_order[x[0]])

    # Calculate the total counts per course
    total_counts_per_course = {}
    for _, courses in counts_per_month_course:
        for course, counts in courses.items():
            if course not in total_counts_per_course:
                total_counts_per_course[course] = {'Male': 0, 'Female': 0}
            total_counts_per_course[course]['Male'] += counts['Male']
            total_counts_per_course[course]['Female'] += counts['Female']

    # Calculate the total counts per month
    total_counts_per_month = {}
    for month, courses in counts_per_month_course:
        if month not in total_counts_per_month:
            total_counts_per_month[month] = {'Male': 0, 'Female': 0}
        for counts in courses.values():
            total_counts_per_month[month]['Male'] += counts['Male']
            total_counts_per_month[month]['Female'] += counts['Female']

    # Calculate the total counts for the whole year
    total_year_male = sum(total_counts_per_month[month]['Male'] for month in total_counts_per_month)
    total_year_female = sum(total_counts_per_month[month]['Female'] for month in total_counts_per_month)

    # Close the database connection
    cur.close()

    # Render the template and pass the counts as template variables
    return render_template(
        'headmoderator/patient-reports-monthly.html',
        counts_per_month_course=counts_per_month_course,
        total_counts_per_course=total_counts_per_course,
        total_counts_per_month=total_counts_per_month,
        total_year_male=total_year_male,
        total_year_female=total_year_female,admin=admin,Notification=Notification,
    )





# Define the custom sorting order for months
month_order = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}


@app.route('/headmoderator/patient-reports-weekly' , methods=['POST','GET'])
def headmoderator_patient_reports_weekly():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
    cur = mysql.connection.cursor()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    cur = mysql.connection.cursor()

    # Execute queries to retrieve the student counts for each week and course
    cur.execute(
        "SELECT Date, Course, Gender, COUNT(*) as count FROM tbl_medical GROUP BY Date, Course, Gender"
    )
    results = cur.fetchall()

    # Create a dictionary to store the counts per week and course
    counts_per_week_course = {}

    # Iterate over the results and populate the dictionary
    for row in results:
        Date = row[0]
        Course = row[1]
        Gender = row[2]
        count = row[3]

        if Date is None:
            continue

        week_start = Date - timedelta(days=Date.weekday())
        week_end = week_start + timedelta(days=6)
        week_range = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"

        if week_range not in counts_per_week_course:
            counts_per_week_course[week_range] = {Course: {'Male': 0, 'Female': 0}}
        if Course in counts_per_week_course[week_range]:
            counts_per_week_course[week_range][Course][Gender] = count
        else:
            counts_per_week_course[week_range][Course] = {'Male': 0, 'Female': 0}
            counts_per_week_course[week_range][Course][Gender] = count

    # Sort the dictionary by week start date
    sorted_counts_per_week_course = dict(sorted(counts_per_week_course.items(), key=lambda x: datetime.strptime(x[0][:10], '%Y-%m-%d')))

    # Get the unique list of courses
    courses = set(course for week in sorted_counts_per_week_course.values() for course in week.keys())

    # Close the database connection
    cur.close()

    # Render the template and pass the counts as template variables

    return render_template(
        'headmoderator/patient-reports-weekly.html',Notification=Notification,admin=admin,counts_per_week_course=sorted_counts_per_week_course,
        courses=courses
    )


@app.route('/headmoderator/patient-reports-daily' , methods=['POST','GET'])
def headmoderator_patient_reports_daily():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
    cur = mysql.connection.cursor()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()

    if request.method == 'POST':
        search_date = request.form['searchDate']
        cursor = mysql.connection.cursor()

        # Retrieve student counts per department for the selected date
        query = """
            SELECT Date, Course, SUM(CASE WHEN Gender='Male' THEN 1 ELSE 0 END) AS male_count,
            SUM(CASE WHEN Gender='Female' THEN 1 ELSE 0 END) AS female_count
            FROM tbl_medical
            WHERE Date = %s
            GROUP BY Date, Course
        """
        cursor.execute(query, (search_date,))
        results = cursor.fetchall()

        if results:
            return render_template('headmoderator/patient-reports-daily.html', results=results, search_date=search_date,Notification=Notification, admin=admin)
        else:
            no_data_message = "No Data Found for the selected date."
            return render_template('headmoderator/patient-reports-daily.html', no_data_message=no_data_message, search_date=search_date,Notification=Notification, admin=admin)
    else:
        return render_template(
            'headmoderator/patient-reports-daily.html', Notification=Notification, admin=admin,

        )


@app.route('/headmoderator/invoice-reports' , methods=['POST','GET'])
def headmorator_invoice_reports():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/invoice-reports.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/semester-reports' , methods=['POST','GET'])
def headmorator_semester_reports():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/semester-reports.html', admin=admin,Notification=Notification)

@app.route('/headmoderator/settings' , methods=['POST','GET'])
def headmorator_settings():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('headmoderator/settings.html', admin=admin,Notification=Notification)


@app.route('/headmoderator/announcement',methods=['POST','GET'])
def headmoderator_announcements():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_students ORDER BY id')
        approve = appointment.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('/headmoderator/announcements.html', admin=admin,approve=approve,Notification=Notification)

@app.route('/headmoderator/announcement/execute', methods=['POST', 'GET'])
def headmoderator_announcements_execute():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        textarea = request.form['textarea']
        cur.execute("INSERT INTO tbl_announcements (name, title, textarea) VALUES (%s,%s,%s)",
                [name, title, textarea])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('headmoderator_announcements'))



@app.route('/headmoderator/announcement-view',methods=['POST','GET'])
def headmoderator_announcements_view():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        announcement = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        announcement.execute('SELECT * FROM tbl_announcements ORDER BY id')
        announcements = announcement.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('/headmoderator/announcements-view.html', admin=admin,announcements=announcements,Notification=Notification)




@app.route('/headmoderator/logout', methods=['POST', 'GET'])
def headmoderator_logout():
    if not session.get('id'):
        return redirect(url_for('headmoderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('headmoderator/login.html', error='Your are not a Moderator!!')
    if session.get('id'):
        session['id'] = None
        session['idnumber'] = None
        return redirect(url_for('headmoderator_login'))




#----------------------------------------------------------------------------------MODERATOR-----------------------------------------------------------

@app.route('/moderator/login', methods=['POST','GET'])
def moderator_login():
    return render_template('moderator/login.html')

@app.route('/moderator/loginexecute', methods=['POST','GET'])
def moderator_loginexecute():
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE idnumber =%s AND password = %s ', (idnumber, password))
        account = cursor.fetchone()
        if account:
            cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND idnumber = %s', (0, idnumber))
            not_approved = cursor.fetchone()
            if not_approved:
                return render_template('moderator/login.html',error='Your Account is NOT Yet Approved')
            else:
                session['loggedin'] = True
                session['id'] = account['id']
                session['idnumber'] = account['idnumber']
                return redirect(url_for('moderator_dashboard'))
    return render_template('moderator/login.html',error='Invalid Username or Password')

@app.route('/moderator/dashboard', methods=['POST','GET'])
def moderator_dashboard():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        cursorapprove.execute('SELECT * FROM tbl_students ORDER BY id')
        studentapproval = cursorapprove.fetchall()
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER BY id')
        appointments = appointment.fetchall()
        cur = mysql.connection.cursor()
        status = 2
        cur.execute('SELECT COUNT(*) FROM tbl_moderator WHERE status= %s',[status])
        result = cur.fetchone()
        user_count = result[0]
        cur.close()
        status = 3
        cur1 = mysql.connection.cursor()
        cur1.execute('SELECT COUNT(*) FROM tbl_students WHERE status= %s',[status])
        result = cur1.fetchone()
        user_count1 = result[0]
        cur1.close()
        cur2 = mysql.connection.cursor()
        cur2.execute('SELECT COUNT(*) FROM tbl_appointments')
        result = cur2.fetchone()
        user_count2 = result[0]
        cur2.close()
        status = 4
        cur3 = mysql.connection.cursor()
        cur3.execute('SELECT COUNT(*) FROM tbl_students WHERE status= %s',[status])
        result = cur3.fetchone()
        user_count3 = result[0]
        cur1.close()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/index.html', Notification=Notification,admin=admin,studentapproval=studentapproval, appointments=appointments,user_count=user_count,user_count1=user_count1,user_count2=user_count2,user_count3 =user_count3 )

@app.route('/moderator/approve-user/<int:id>')
def moderator_approve(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    status = 3
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_students SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()
    return redirect(url_for('moderator_approve_student'))

@app.route('/moderator/disapprove-user/<int:id>')
def moderator_remove_access(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    status = 0
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_students  SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()
    return redirect(url_for('moderator_approve_student'))


@app.route('/moderator/approve-user-faculty/<int:id>')
def moderator_approve_faculty_execute(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')

    status = 4
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_students SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()
    return redirect(url_for('moderator_approve_faculty'))

@app.route('/moderator/disapprove-user-faculty/<int:id>')
def moderator_remove_access_faculty(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    status = 0
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_students  SET status = %s WHERE id = %s', (status, id))
    mysql.connection.commit()
    return redirect(url_for('moderator_approve_faculty'))


@app.route('/moderator/profile', methods=['POST','GET'])
def moderator_profile():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursorapprove1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove1.execute('SELECT * FROM tbl_moderatorbackinfo WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval1 = cursorapprove1.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/profile.html', admin=admin, studentapproval=studentapproval,
                           studentapproval1=studentapproval1,Notification=Notification)


@app.route('/moderator/edit-profile', methods=['POST','GET'])
def moderator_edit_profile():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/edit-profile.html', admin=admin,Notification=Notification)



@app.route('/moderator/edit-moderatorbackinfo', methods=['POST','GET'])
def moderator_edit_moderatorbackinfo():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursorapprove1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove1.execute('SELECT * FROM tbl_moderatorbackinfo WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval1 = cursorapprove1.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/edit-moderatorbackinfo.html', admin=admin,studentapproval1=studentapproval1,Notification=Notification)


@app.route('/moderator/edit-moderatorbackground/execute/<int:id>', methods=['post','get'])
def moderator_edit_moderatorbackground_execute(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        Email = request.form['Email']
        Phone = request.form['Phone']
        Address = request.form['Address']
        Birthdate = request.form['Birthdate']
        status = request.form['status']
        ID_Number = request.form['ID_Number']
        cur.execute('UPDATE tbl_moderatorbackinfo SET Email=%s,Phone=%s,Address=%s,Birthdate=%s,status=%s,ID_Number=%s WHERE id= %s', (Email,Phone,Address,Birthdate,status,ID_Number,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('moderator_profile'))


@app.route('/moderator/edit-profile/execute/<int:id>', methods=['post','get'])
def moderator_edit_profile_execute(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        First_name = request.form['First_name']
        Middle_name = request.form['Middle_name']
        Last_name = request.form['Last_name']
        gender = request.form['gender']
        extension = request.form['extension']
        cur.execute('UPDATE tbl_moderator SET extension=%s,gender=%s,Last_name=%s,Middle_name=%s,First_name=%s WHERE id= %s', (extension,gender,Last_name,Middle_name,First_name,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('moderator_profile'))




@app.route('/moderator/add-profile', methods=['POST','GET'])
def moderator_add_profile():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/add-profilebackground.html', admin=admin,Notification=Notification)




@app.route('/moderator/add-profile/execute', methods=['post','get'])
def moderator_add_profile_execute():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        status = request.form['status']
        ID_Number = request.form['idnumber']
        Phone = request.form['phone']
        Email = request.form['email']
        Address = request.form['Address']
        Birthdate = request.form['Birthdate']
        cur.execute("INSERT INTO tbl_moderatorbackinfo (status,ID_Number,Phone,Email,Address,Birthdate) VALUES (%s,%s,%s,%s,%s,%s)",[status,ID_Number,Phone,Email,Address,Birthdate])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('moderator_profile'))






@app.route('/moderator/patients',methods=['POST','GET'])
def moderator_patients():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_medical ORDER BY Date')
        medical = appointment.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/patients.html', admin=admin,medical=medical,Notification=Notification)


@app.route('/moderatorsearchpatient', methods=['POST'])
def moderatorsearchpatient():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_medical ORDER BY Date')
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if request.method == 'POST':
        query = request.form['search_query']
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute("SELECT * FROM tbl_medical WHERE idnumber LIKE %s", ("%" + query + "%",))
        results = cursor1.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE First_name LIKE %s", ("%" + query + "%",))
        resultsname = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Middle_name LIKE %s", ("%" + query + "%",))
        resultsmiddlename = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Last_name LIKE %s", ("%" + query + "%",))
        resultslastname = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Title LIKE %s", ("%" + query + "%",))
        resultslasttitle = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Treatment LIKE %s", ("%" + query + "%",))
        resultstreatment = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Diagnosis LIKE %s", ("%" + query + "%",))
        resultsdiagnosis = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_medical WHERE Date LIKE %s", ("%" + query + "%",))
        resultsdate = cursor.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
        return render_template('moderator/patients_search.html',Notification=Notification,query=query, results=results,resultsname =resultsname, resultslastname =resultslastname,admin=admin,appointments=appointments,resultslasttitle=resultslasttitle,resultsmiddlename=resultsmiddlename,resultstreatment=resultstreatment,resultsdiagnosis=resultsdiagnosis,resultsdate=resultsdate)





@app.route('/moderator/add-patient' , methods=['POST','GET'])
def moderator_add_patients():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/add-patient.html', admin=admin,Notification=Notification)



@app.route('/get_name', methods=['POST'])
def get_name():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    id_number = request.form['id_number']
    cursor = mysql.connection.cursor()
    result = cursor.execute(
    "SELECT idnumber, Email,Year_level,Course,First_name ,Middle_name,Last_name ,Cp_number ,Gender,Home_Address FROM tbl_students WHERE idnumber = %s",
        (id_number,))
    if result > 0:
        data = cursor.fetchone()
        idnumber = data[0]
        email = data[1]
        yearlevel = data[2]
        course = data[3]
        firstname = data[4]
        middlename = data[5]
        lastname = data[6]
        Cp_number = data[7]
        Gender = data[8]
        address = data[9]

        return jsonify(
            {'idnumber': idnumber, 'email': email, 'yearlevel': yearlevel, 'course': course, 'firstname': firstname,
             'middlename': middlename, 'lastname': lastname, 'Cp_number': Cp_number, 'Gender': Gender,
             'address': address})
    else:
        return jsonify(
            {'name': '', 'email': '', 'yearlevel': '', 'course': '', 'firstname': '', 'middlename': '', 'lastname': '',
             'Cp_number': '', 'Gender': '', 'address': ''})


@app.route('/moderator/add-patient-execute', methods=['post','get'])
def moderator_add_patient_execute():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        Physician = request.form['Firstname']
        Year_level = request.form['yearlevel']
        Course = request.form['course']
        idnumber = request.form['idnumber']
        First_name = request.form['firstname']
        Middle_name = request.form['middlename']
        Last_name = request.form['lastname']
        Cp_number = request.form['Cp_number']
        Home_Address = request.form['address']
        date = request.form['date']
        Gender = request.form['gender']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        Title = 'Walkin Patient'
        cur.execute("INSERT INTO tbl_medical (Physician,Year_level,Course,idnumber,First_name,Middle_name,Last_name,Cp_number,Address,Date,Title,Gender,Diagnosis,Treatment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[Physician ,Year_level,Course,idnumber,First_name,Middle_name,Last_name,Cp_number,Home_Address,date,Title,Gender,diagnosis,treatment])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('moderator_add_patients'))





@app.route('/moderator/appoinement-add-patient/<int:id>' , methods=['POST','GET'])
def moderator_appointment_add_patients(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment_patient = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment_patient.execute('SELECT * FROM tbl_appointments WHERE id = %s', (id,))
        appointment = appointment_patient.fetchone()
    return render_template('moderator/appointment-add-patient.html', admin=admin,appointment=appointment,Notification=Notification)



@app.route('/moderator/appointment-add-patient-execute/<int:id>', methods=['post','get'])
def moderator_appointment_add_patient_execute(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        Physician = request.form['Firstname']
        Year_level = request.form['yearlevel']
        Course = request.form['course']
        idnumber = request.form['idnumber']
        First_name = request.form['firstname']
        Middle_name = request.form['middlename']
        Last_name = request.form['lastname']
        Cp_number = request.form['Cp_number']
        Home_Address = request.form['address']
        date = request.form['date']
        Gender = request.form['Gender']
        Title = request.form['title']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        status = 'Appointment Rendered'
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status = %s WHERE id = %s', (status, id))
        mysql.connection.commit()
        status1 = 6
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status1 = %s WHERE id = %s', (status1, id))
        mysql.connection.commit()
        cur.execute("INSERT INTO tbl_medical (Physician,Year_level,Course,idnumber,First_name,Middle_name,Last_name,Cp_number,Address,Date,Gender,Title,Diagnosis,Treatment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[Physician ,Year_level,Course,idnumber,First_name,Middle_name,Last_name,Cp_number,Home_Address,date,Gender,Title ,diagnosis,treatment])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('moderator_appointments'))


@app.route('/moderator/appointment-add-patient-execute-status1/<int:id>', methods=['post','get'])
def moderator_appointment_add_patient_execute_status1(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    status1 = 7
    cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorapprove.execute('UPDATE tbl_appointments SET status1 = %s WHERE id = %s', (status1, id))
    mysql.connection.commit()
    return redirect(url_for('moderator_appointments'))

@app.route('/moderator/add-visitor-patient' , methods=['POST','GET'])
def moderator_add_visitor_patients():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/add-visitor-patient.html', admin=admin,Notification=Notification)

@app.route('/moderator/add-visitor-patient-execute', methods=['post','get'])
def moderator_add_visitor_patient_execute():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        idnumber = request.form['id_number']
        Physician = request.form['firstname']
        First_name = request.form['First_name']
        Middle_name = request.form['Middle_name']
        Last_name = request.form['Last_name']
        Cp_number = request.form['Cp_number']
        Home_Address = request.form['Home_Address']
        date = request.form['date']
        Gender = request.form['Gender']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        title = request.form['title']
        cur.execute("INSERT INTO tbl_medical (idnumber,Physician ,First_name,Middle_name,Last_name,Cp_number,Address,Date,Gender,Diagnosis,Treatment,Title) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idnumber,Physician ,First_name,Middle_name,Last_name,Cp_number,Home_Address,date,Gender,diagnosis,treatment,title])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('moderator_add_visitor_patients'))




@app.route('/moderator/staff-list' , methods=['POST','GET'])
def moderator_staff_list():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        cursorapprove.execute('SELECT * FROM tbl_moderator ORDER BY id')
        admin = cursor.fetchone()
        moderatorapproval = cursorapprove.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/staff-list.html',moderatorapproval=moderatorapproval, admin=admin,Notification=Notification)


@app.route('/moderator/add-staff' , methods=['POST','GET'])
def moderator_add_staff():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/add-staff.html', admin=admin,Notification=Notification)

@app.route('/moderator/add-staff-execute', methods=['post','get'])
def moderator_add_staff_execute():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        gender = request.form['gender']
        password = request.form['password']
        cur2.execute('SELECT * FROM tbl_moderator WHERE idnumber = %s', (idnumber,))
        result2 = cur2.fetchone()
        if result2:
            return render_template('headmoderator/add-staff.html', error2='ID-Number already exist!',Notification=Notification)
        else:
            cur.execute(
                "INSERT INTO tbl_moderator (idnumber,firstname,lastname,gender,password) VALUES (%s,%s,%s,%s,%s)",
                [idnumber,firstname,lastname,gender,password])
            mysql.connection.commit()
            cur.close()
            return render_template('headmoderator/add-staff.html', message='Successfully Added!', admin=admin,Notification=Notification)


@app.route('/moderator/appointments' , methods=['POST','GET'])
def moderator_appointments():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE status1=%s ORDER BY Start_date_time',(5,))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('moderator/appointments.html', appointments=appointments, admin=admin,Notification=Notification)

@app.route('/moderator/appointments-canceled' , methods=['POST','GET'])
def moderator_appointments_canceled():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE status1=%s ORDER BY Start_date_time',(8,))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('moderator/appointments-canceled.html', appointments=appointments, admin=admin,Notification=Notification)


@app.route('/moderator/appointments-due' , methods=['POST','GET'])
def moderator_appointments_due():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE status1=%s ORDER BY Start_date_time',(7,))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('moderator/appointments-due.html', appointments=appointments, admin=admin,Notification=Notification)


@app.route('/moderator/appointments-success' , methods=['POST','GET'])
def moderator_appointments_success():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE status1=%s ORDER BY Start_date_time',(6,))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('moderator/appointments-success.html', appointments=appointments, admin=admin,Notification=Notification)


@app.route('/moderatorsearch', methods=['POST'])
def moderatorsearch():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER BY id')
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    if request.method == 'POST':
        query = request.form['search_query']
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute("SELECT * FROM tbl_appointments WHERE ID_Number LIKE %s", ("%" + query + "%",))
        results = cursor1.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE firstname LIKE %s", ("%" + query + "%",))
        resultsname = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE middlename LIKE %s", ("%" + query + "%",))
        resultsmiddlename = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE lastname LIKE %s", ("%" + query + "%",))
        resultslastname = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE email LIKE %s", ("%" + query + "%",))
        resultsemail = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE Title LIKE %s", ("%" + query + "%",))
        resultstitle = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE Start_date_time LIKE %s", ("%" + query + "%",))
        resultsStart_date_time = cursor.fetchall()
        query = request.form['search_query']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_appointments WHERE status LIKE %s", ("%" + query + "%",))
        resultsstatus = cursor.fetchall()
        return render_template('moderator/appointments_search.html',Notification=Notification,query=query, results=results,resultsname =resultsname, resultslastname =resultslastname,admin=admin,appointments=appointments,resultsmiddlename=resultsmiddlename,resultsemail =resultsemail,resultstitle =resultstitle,resultsStart_date_time=resultsStart_date_time,resultsstatus=resultsstatus )



















@app.route('/range', methods=['POST','GET'])
def srange():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if request.method == 'POST':
        From = request.form['From']
        to = request.form['to']
        print(From)
        print(to)
        query = "SELECT * from tbl_appointments WHERE Start_date_time BETWEEN '{}' AND '{}'".format(From, to)
        cur.execute(query)
        ordersrange = cur.fetchall()
    return jsonify({'htmlresponse': render_template('moderator/response.html', ordersrange=ordersrange,admin=admin)})



@app.route('/moderator/add-appointment' , methods=['POST','GET'])
def moderator_add_appointment():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/add-appointment.html', admin=admin,Notification=Notification)

@app.route('/add_date', methods=['POST'])
def add_date():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    # Get the date from the form
    if request.method == 'POST':
        date_str = request.form['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

    # Insert the date into the database
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO disabled_dates (date) VALUES (%s)", [date_obj,])
        mysql.connection.commit()
        return redirect(url_for('moderator_add_appointment'))

@app.route('/moderator/add-appointment-execute', methods=['post','get'])
def moderator_add_appointment_execute():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    if request.method == 'POST':
        date_str = request.form['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        title = request.form['title']
        cur.execute('SELECT * FROM disabled_dates WHERE date = %s', (date_obj,))
        result = cur.fetchone()
        if result:
            return render_template('moderator/add-appointment.html', admin=admin, error='Date is already Disabled!!',Notification=Notification)
        else:
            cur.execute(
                "INSERT INTO disabled_dates (date,Title) VALUES (%s,%s)",
                [date_obj,title ])
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('moderator_add_appointment',error='Disabled Succesfully!!'))




@app.route('/moderator/add-appointment-dentist' , methods=['POST','GET'])
def moderator_add_appointment_dentist():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/add-appointment-dental.html', admin=admin,Notification=Notification)

@app.route('/moderator/add-appointment-execute-dental', methods=['post','get'])
def moderator_add_appointment_execute_dental():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    if request.method == 'POST':
        date_str = request.form['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        title = request.form['title']
        cur.execute('SELECT * FROM disabled_dates_dental WHERE date = %s', (date_obj,))
        result = cur.fetchone()
        if result:
            return render_template('moderator/add-appointment.html', admin=admin, error='Date is already Disabled!!',Notification=Notification)
        else:
            cur.execute(
                "INSERT INTO disabled_dates_dental (date,Title) VALUES (%s,%s)",
                [date_obj,title ])
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('moderator_add_appointment_dentist',error='Disabled Succesfully!!'))




@app.route('/moderator/calendar' , methods=['POST','GET'])
def moderator_calendar():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER BY id')
    appointments = appointment.fetchall()
    disabled = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    disabled.execute('SELECT * FROM disabled_dates ORDER BY ids')
    disable = disabled.fetchall()
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
    Notification = appointment.fetchall()
    return render_template('moderator/calendar.html', appointments=appointments, admin=admin,disable=disable,Notification=Notification)

@app.route('/moderator/compose' , methods=['POST','GET'])
def moderator_compose():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/compose.html', admin=admin,Notification=Notification)

@app.route('/moderator/send_email', methods=['POST'])
def moderator_send_email():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        recipient = request.form['recipient']
        message = request.form['textarea']

        # Create the message
        msg = Message(subject='New message from your school Clinic',
                      recipients=[recipient])  # Replace with your email address
        msg.body = f"You have received a new message from {name}: \n\n{message}"

        try:
            # Send the message
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending your message: {e}', 'error')

    return render_template('moderator/compose.html', admin=admin,Notification=Notification)


@app.route('/moderator/compose-cancel/<int:id>' , methods=['POST','GET'])
def moderator_compose_cancel(id):
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_appointments WHERE id = %s', (id,))
        mail = cursor.fetchone()
        status = 'Appointment Canceled'
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status = %s WHERE id = %s', (status, id))
        mysql.connection.commit()
        status1 = 8
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status1 = %s WHERE id = %s', (status1, id))
        mysql.connection.commit()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()

    return render_template('moderator/compose-cancel.html', admin=admin,mail=mail,Notification=Notification)


@app.route('/moderator/send_email/recipient', methods=['POST'])
def moderator_send_email_recipient():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        recipient = request.form['recipient']
        message = request.form['textarea']
        # Create the message
        msg = Message(subject='New message from your school Clinic',
                      recipients=[recipient])  # Replace with your email address
        msg.body = f"You have received a new message from :{name} \n\n{message}"

        try:
            # Send the message
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending your message: {e}', 'error')

    return redirect(url_for('moderator_appointments'))




@app.route('/moderator/blog', methods=['POST', 'GET'])
def moderator_blog():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/blog.html', admin=admin,Notification=Notification)

@app.route('/moderator/blog-details', methods=['POST','GET'])
def moderator_blog_deatails():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/blog-details.html', admin=admin,Notification=Notification)

@app.route('/moderator/add-blog' , methods=['POST','GET'])
def moderator_add_blog():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/add-blog.html', admin=admin,Notification=Notification)


@app.route('/moderator/add-blog/execute' , methods=['POST','GET'])
def moderator_add_blog_execute():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        now = datetime.now()
        if request.method == 'POST':
            files = request.files.getlist('files[]')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cur.execute("INSERT INTO tbl_images (file_name, uploaded_on) VALUES (%s, %s)", [filename, now])
                    mysql.connection.commit()
                print(file)
            cur.close()
            flash('File(s) successfully uploaded')
            return redirect(url_for('moderator_add_blog'))


@app.route('/moderator/edit-blog' , methods=['POST','GET'])
def moderator_edit_blog():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/edit-blog.html', admin=admin,Notification=Notification)


@app.route('/moderator/settings' , methods=['POST','GET'])
def moderator_settings():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/settings.html', admin=admin,Notification=Notification)


@app.route('/moderator/approve-student',methods=['POST','GET'])
def moderator_approve_student():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_students ORDER By id')
        approve = appointment.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/approve-students.html', admin=admin,approve=approve,Notification=Notification)


@app.route('/moderator/approve-faculty',methods=['POST','GET'])
def moderator_approve_faculty():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_students ORDER BY id')
        approve = appointment.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/approve-faculty.html', admin=admin,approve=approve,Notification=Notification)


@app.route('/moderator/announcement',methods=['POST','GET'])
def moderator_announcements():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_students ORDER BY id')
        approve = appointment.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('moderator/announcements.html', admin=admin,approve=approve,Notification=Notification)

@app.route('/moderator/announcement/execute', methods=['POST', 'GET'])
def moderator_announcements_execute():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        textarea = request.form['textarea']
        cur.execute("INSERT INTO tbl_announcements (name, title, textarea) VALUES (%s,%s,%s)",
                [name, title, textarea])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('moderator_announcements'))



@app.route('/moderator/announcement-view',methods=['POST','GET'])
def moderator_announcements_view():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        announcement = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        announcement.execute('SELECT * FROM tbl_announcements ORDER BY id')
        announcements = announcement.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments ORDER By Start_date_time')
        Notification = appointment.fetchall()
    return render_template('/moderator/announcements-view.html', admin=admin,announcements=announcements,Notification=Notification)









@app.route('/moderator/logout', methods=['POST', 'GET'])
def moderator_logout():
    if not session.get('id'):
        return redirect(url_for('moderator_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('moderator/login.html', error='You are not a Moderator!!')
    if session.get('id'):
        session['id'] = None
        session['idnumber'] = None
        return redirect(url_for('moderator_login'))





#----------------------------------------------------------------------------------STUDENT-----------------------------------------------------------
def generate_password(length=8):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Check if email exists in the database
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM tbl_students WHERE Email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            # Generate a new password
            new_password = generate_password()

            # Update the password in the database
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("UPDATE tbl_students SET Password = %s WHERE Email = %s", (new_password, email))
            mysql.connection.commit()
            cur.close()

            # Send the new password to the user's email
            msg = Message('Password Reset', sender='qsuclinic@gmail.com', recipients=[email])
            msg.body = f"Your new password is: {new_password}"
            mail.send(msg)

            flash("A new password has been sent to your email.")
            return render_template('/student/forgotpassword.html')
        else:
            flash("Email address not found.")
            return redirect('/forgot-password')

    return render_template('/student/forgotpassword.html')



@app.route('/student/register', methods=['POST','GET'])
def student_register():
    return render_template('student/register.html')

@app.route('/student/register/execute', methods=['post','get'])
def student_register_execute():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        Course = request.form['course']
        Year_level = request.form['yearlevel']
        First_name = request.form['firstname']
        Middle_name = request.form['middlename']
        Last_name = request.form['lastname']
        Gender = request.form['gender']
        Home_Address = request.form['homeaddress']
        Civil_status = request.form['civilstatus']
        Place_of_birth = request.form['placeofbirth']
        Birthdate = request.form['birthdate']
        Cp_number = request.form['mobile']
        Boarding_address = request.form['boardinghouse']
        Nationality = request.form['nationality']
        Religion = request.form['religion']
        Email = request.form['email']
        Password = request.form['password']
        Userlevel_ID = 3
        cur.execute('SELECT * FROM tbl_students WHERE Email = %s', (Email,))
        cur2.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (idnumber,))
        result = cur.fetchone()
        result2 = cur2.fetchone()
        if result2:
            return render_template('student/register.html', error2='ID-Number already exist!')
        if result:
            return render_template('student/register.html', error='Email already exist!')
        else:
            cur.execute(
                "INSERT INTO tbl_students (idnumber,Course,Year_level,First_name,Middle_name,Last_name,Gender,Home_Address,Civil_status,Place_of_birth,Birthdate,Cp_number,Boarding_address,Nationality,Religion,Email,Password,Userlevel_ID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [idnumber,Course,Year_level,First_name,Middle_name,Last_name,Gender,Home_Address,Civil_status,Place_of_birth,Birthdate,Cp_number,Boarding_address,Nationality,Religion,Email,Password,Userlevel_ID])
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('student_login'))

@app.route('/student/login', methods=['POST','GET'])
def student_login():
    return render_template('student/login.html')

@app.route('/student/loginexecute', methods=['POST','GET'])
def student_loginexecute():
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE idnumber =%s AND password = %s ', (idnumber, password))
        account = cursor.fetchone()
        if account:
            cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND idnumber = %s', (4, idnumber))
            not_approved = cursor.fetchone()
            cursor2.execute('SELECT * FROM tbl_students WHERE status =%s AND idnumber = %s', (0, idnumber))
            not_approved2 = cursor2.fetchone()
            if not_approved:
                return render_template('student/login.html', error='Your are not a faculty Member!!')
            if not_approved2:
                return render_template('student/login.html', error='Your Account is NOT Yet Approved')
            else:
                session['loggedin'] = True
                session['id'] = account['id']
                session['idnumber'] = account['idnumber']
                return redirect(url_for('student_dashboard'))
    return render_template('student/login.html',error='Invalid Username or Password')

@app.route('/student/dashboard', methods=['POST','GET'])
def student_dashboard():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')


    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        announcement = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        announcement.execute('SELECT * FROM tbl_announcements ORDER BY id')
        announcements = announcement.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/index.html', admin=admin,announcements=announcements,Notification=Notification)

@app.route('/student/profile', methods=['POST','GET'])
def student_profile():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')

    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        studentapproval = cursorapprove.fetchone()
        cursorapprove1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval1 = cursorapprove1.fetchone()
        cursorapprove2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval2 = cursorapprove2.fetchone()
        cursorapprove3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval3 = cursorapprove3.fetchone()
        cursorapprove4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval4 = cursorapprove4.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle  WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1  WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2  WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/profile.html', admin=admin,studentapproval4=studentapproval4,studentapproval=studentapproval,studentapproval1=studentapproval1,studentapproval2=studentapproval2,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2,studentapproval3=studentapproval3,Notification=Notification)



@app.route('/student/edit-profile', methods=['POST','GET'])
def student_edit_profile():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')

    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number= %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        appointments = appointment.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/edit-profile.html',Notification=Notification, appointments=appointments,admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)


@app.route('/student/edit-profile/execute/<int:id>', methods=['post','get'])
def student_edit_profile_execute(id):
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        birthdate = request.form['birthdate']
        gender = request.form['gender']
        course = request.form['course']
        yearlevel = request.form['yearlevel']
        homeaddress = request.form['homeaddress']
        civilstatus = request.form['civilstatus']
        placeofbirth = request.form['placeofbirth']
        mobile = request.form['mobile']
        boardinghouse = request.form['boardinghouse']
        nationality = request.form['nationality']
        religion = request.form['religion']
        email = request.form['email']
        cur.execute("UPDATE tbl_students SET 	First_name=%s,Middle_name=%s,Last_name=%s,Birthdate=%s,Gender=%s,Course=%s,Year_level=%s,Home_Address=%s,Civil_status=%s,Place_of_birth=%s,Cp_number=%s,Boarding_address=%s,Nationality=%s,Religion=%s,Email=%s WHERE id = %s",
                    (firstname,middlename,lastname,birthdate,gender,course,yearlevel,homeaddress,civilstatus,placeofbirth,mobile,boardinghouse,nationality,religion,email ,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_profile'))



@app.route('/student/edit-profilefamily', methods=['POST','GET'])
def student_edit_profilefamily():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')

    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1  WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/edit-profilefamily.html',Notification=Notification, admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)


@app.route('/student/add-profilefamily', methods=['POST','GET'])
def student_add_profilefamily():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')

    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1  WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/add-profilefamily.html', Notification=Notification,admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)


@app.route('/student/edit-profilefamily/execute/<int:id>', methods=['post','get'])
def student_edit_profilefamily_execute(id):
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['idnumber']
        Gaurdian = request.form['guardian']
        Father_name = request.form['fathersname']
        Father_address = request.form['fatheraddress']
        Father_age = request.form['fatherage']
        Father_occupation = request.form['fatheroccupation']
        Father_educational_attainment = request.form['fathereducational']
        Mother_name = request.form['mothersname']
        Mother_Address = request.form['motheraddress']
        Mother_age = request.form['motherage']
        Mother_occupation = request.form['motheroccupation']
        Mother_educational_attainment = request.form['mothereducational']
        status = request.form['status']
        cur.execute("UPDATE tbl_familybackground SET ID_Number=%s,Gaurdian=%s,Father_name=%s,Father_address=%s,Father_age=%s,Father_occupation=%s,Father_educational_attainment=%s,Mother_name=%s,Mother_Address=%s,Mother_age=%s,Mother_occupation=%s,Mother_educational_attainment=%s,status=%s WHERE id = %s",(ID_Number,Gaurdian,Father_name,Father_address,Father_age,Father_occupation,Father_educational_attainment,Mother_name,Mother_Address,Mother_age,Mother_occupation,Mother_educational_attainment,status,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_profile'))





@app.route('/student/add-profilefamily/execute', methods=['post','get'])
def student_add_profilefamily_execute():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['idnumber']
        Gaurdian = request.form['guardian']
        Father_name = request.form['fathersname']
        Father_address = request.form['fatheraddress']
        Father_age = request.form['fatherage']
        Father_occupation = request.form['fatheroccupation']
        Father_educational_attainment = request.form['fathereducational']
        Mother_name = request.form['mothersname']
        Mother_Address = request.form['motheraddress']
        Mother_age = request.form['motherage']
        Mother_occupation = request.form['motheroccupation']
        Mother_educational_attainment = request.form['mothereducational']
        status = request.form['status']
        cur.execute("INSERT INTO tbl_familybackground (ID_Number,Gaurdian,Father_name,Father_address,Father_age,Father_occupation,Father_educational_attainment,Mother_name,Mother_Address,Mother_age,Mother_occupation,Mother_educational_attainment,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[ID_Number,Gaurdian,Father_name,Father_address,Father_age,Father_occupation,Father_educational_attainment,Mother_name,Mother_Address,Mother_age,Mother_occupation,Mother_educational_attainment,status])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_profile'))


@app.route('/student/add-lifestyle', methods=['POST','GET'])
def student_add_lifestyle():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/add-lifestyle.html', Notification=Notification,admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/student/add-lifestyle/execute', methods=['post','get'])
def student_add_lifestyle_execute():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['idnumber']
        Do_you_Smoke = request.form['doyousmoke']
        How_many_stick = request.form['howmany']
        Do_someone = request.form['dosomeone']
        Do_drink_Alchohol = request.form['drinkalchohol']
        How_often = request.form['howoften']
        status = request.form['status']
        cur.execute("INSERT INTO tbl_lifestyle (ID_Number,Do_you_Smoke,How_many_stick,Do_someone,Do_drink_Alchohol ,How_often,status) VALUES (%s,%s,%s,%s,%s,%s,%s)",[ID_Number,Do_you_Smoke,How_many_stick,Do_someone,Do_drink_Alchohol ,How_often,status])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_profile'))


@app.route('/student/edit-lifestyle', methods=['POST','GET'])
def student_edit_lifestyle():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/edit-lifestyle.html', Notification=Notification,admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)


@app.route('/student/edit-lifestyle/execute/<int:id>', methods=['post','get'])
def student_edit_lifestyle_execute(id):
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        doyousmoke = request.form['doyousmoke']
        howmany = request.form['howmany']
        dosomeone = request.form['dosomeone']
        drinkalchohol = request.form['drinkalchohol']
        howoften = request.form['howoften']
        status = request.form['status']
        idnumber= request.form['idnumber']
        cur.execute("UPDATE tbl_lifestyle SET Do_you_Smoke=%s,How_many_stick=%s,Do_someone=%s,Do_drink_Alchohol=%s,How_often=%s,ID_Number=%s,status=%s WHERE id = %s",
                    (doyousmoke,howmany,dosomeone,drinkalchohol,howoften,idnumber,status,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_profile'))


@app.route('/student/add-healthinformation1', methods=['POST','GET'])
def student_add_healthinformation1():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        health = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/add-health.html', Notification=Notification,admin=admin,studentapproval=studentapproval,health=health,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/student/add-healthinformation1/execute', methods=['post','get'])
def student_add_healthinformation1_execute():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['ID_Number']
        Asthma= request.form['Asthma']
        Asthma_Age = request.form['Asthma_Age']
        Hepatitis = request.form['Hepatitis']
        Hepatitis_Age = request.form['Hepatitis_Age']
        High_Cholesterol = request.form['High_Cholesterol']
        High_Cholesterol_Age = request.form['High_Cholesterol_Age']
        Goiter = request.form['Goiter']
        Goiter_Age = request.form['Goiter_Age']
        Leukemia = request.form['Leukemia']
        Leukemia_Age = request.form['Leukemia_Age']
        Angina = request.form['Angina']
        Angina_Age = request.form['Angina_Age']
        Heart_Murmur = request.form['Heart_Murmur']
        Heart_Murmur_Age = request.form['Heart_Murmur_Age']
        Stroke = request.form['Stroke']
        Stroke_Age = request.form['Stroke_Age']
        Kidney_Disease= request.form['Kidney_Disease']
        Kidney_Disease_Age = request.form['Kidney_Disease_Age']
        Anemia = request.form['Anemia']
        Anemia_Age = request.form['Anemia_Age']
        Stomach_or_Peptic_Ulcer = request.form['Stomach_or_Peptic_Ulcer']
        Stomach_or_Peptic_Ulcer_Age = request.form['Stomach_or_Peptic_Ulcer_Age']
        status= request.form['status']
        cur.execute("INSERT INTO tbl_healthhistoryform1 (ID_Number,Asthma,Asthma_Age,Hepatitis,Hepatitis_Age ,High_Cholesterol,High_Cholesterol_Age,Goiter,Goiter_Age,Leukemia,Leukemia_Age,Angina,Angina_Age,Heart_Murmur,Heart_Murmur_Age,Stroke,Stroke_Age,Kidney_Disease,Kidney_Disease_Age,Anemia,Anemia_Age,Stomach_or_Peptic_Ulcer,Stomach_or_Peptic_Ulcer_Age,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [ID_Number,Asthma,Asthma_Age,Hepatitis,Hepatitis_Age ,High_Cholesterol,High_Cholesterol_Age,Goiter,Goiter_Age,Leukemia,Leukemia_Age,Angina,Angina_Age,Heart_Murmur,Heart_Murmur_Age,Stroke,Stroke_Age,Kidney_Disease,Kidney_Disease_Age,Anemia,Anemia_Age,Stomach_or_Peptic_Ulcer,Stomach_or_Peptic_Ulcer_Age,status])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_profile'))

@app.route('/student/edit-healthinformation1', methods=['POST','GET'])
def student_edit_healthinformation1():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        health = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/edit-health.html',Notificatio=Notification,admin=admin,studentapproval=studentapproval,health=health,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/student/edit-healthinformation1/execute/<int:id>', methods=['post','get'])
def student_edit_healthinformation1_execute(id):
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['ID_Number']
        Asthma= request.form['Asthma']
        Asthma_Age = request.form['Asthma_Age']
        Hepatitis = request.form['Hepatitis']
        Hepatitis_Age = request.form['Hepatitis_Age']
        High_Cholesterol = request.form['High_Cholesterol']
        High_Cholesterol_Age = request.form['High_Cholesterol_Age']
        Goiter = request.form['Goiter']
        Goiter_Age = request.form['Goiter_Age']
        Leukemia = request.form['Leukemia']
        Leukemia_Age = request.form['Leukemia_Age']
        Angina = request.form['Angina']
        Angina_Age = request.form['Angina_Age']
        Heart_Murmur = request.form['Heart_Murmur']
        Heart_Murmur_Age = request.form['Heart_Murmur_Age']
        Stroke = request.form['Stroke']
        Stroke_Age = request.form['Stroke_Age']
        Kidney_Disease= request.form['Kidney_Disease']
        Kidney_Disease_Age = request.form['Kidney_Disease_Age']
        Anemia = request.form['Anemia']
        Anemia_Age = request.form['Anemia_Age']
        Stomach_or_Peptic_Ulcer = request.form['Stomach_or_Peptic_Ulcer']
        Stomach_or_Peptic_Ulcer_Age = request.form['Stomach_or_Peptic_Ulcer_Age']
        status= request.form['status']
        cur.execute("UPDATE tbl_healthhistoryform1 SET ID_Number=%s,Asthma=%s,Asthma_Age=%s,Hepatitis=%s,Hepatitis_Age=%s ,High_Cholesterol=%s,High_Cholesterol_Age=%s,Goiter=%s,Goiter_Age=%s,Leukemia=%s,Leukemia_Age=%s,Angina=%s,Angina_Age=%s,Heart_Murmur=%s,Heart_Murmur_Age=%s,Stroke=%s,Stroke_Age=%s,Kidney_Disease=%s,Kidney_Disease_Age=%s,Anemia=%s,Anemia_Age=%s,Stomach_or_Peptic_Ulcer=%s,Stomach_or_Peptic_Ulcer_Age=%s,status=%s WHERE id = %s",(ID_Number,Asthma,Asthma_Age,Hepatitis,Hepatitis_Age ,High_Cholesterol,High_Cholesterol_Age,Goiter,Goiter_Age,Leukemia,Leukemia_Age,Angina,Angina_Age,Heart_Murmur,Heart_Murmur_Age,Stroke,Stroke_Age,Kidney_Disease,Kidney_Disease_Age,Anemia,Anemia_Age,Stomach_or_Peptic_Ulcer,Stomach_or_Peptic_Ulcer_Age,status,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_profile'))


@app.route('/student/add-healthinformation2', methods=['POST','GET'])
def student_add_healthinformation2():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        health = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/add-health2.html',Notification=Notification,admin=admin,studentapproval=studentapproval,health=health,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/student/add-healthinformation2/execute', methods=['post','get'])
def student_add_healthinformation2_execute():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['ID_Number']
        Head_Injury= request.form['Head_Injury']
        Head_Injury_Age = request.form['Head_Injury_Age']
        Surgery = request.form['Surgery']
        Surgery_Type = request.form['Surgery_Type']
        Surgery_Age = request.form['Surgery_Age']
        Allergies = request.form['Allergies']
        Allergies_Age = request.form['Allergies_Age']
        High_Blood_Pressure = request.form['High_Blood_Pressure']
        High_Blood_Pressure_Age = request.form['High_Blood_Pressure_Age']
        Hypothyroidism = request.form['Hypothyroidism']
        Hypothyroidism_Age = request.form['Hypothyroidism_Age']
        Cancer = request.form['Cancer']
        Cancer_Type = request.form['Cancer_Type']
        Cancer_Age = request.form['Cancer_Age']
        Psoriasis= request.form['Psoriasis']
        Psoriasis_Age= request.form['Psoriasis_Age']
        Heart_Problem= request.form['Heart_Problem']
        Heart_Problem_Age = request.form['Heart_Problem_Age']
        Pneumonia = request.form['Pneumonia']
        Pneumonia_Age = request.form['Pneumonia_Age']
        Epilepsy = request.form['Epilepsy']
        Epilepsy_Age = request.form['Epilepsy_Age']
        Kidney_Stone = request.form['Allergies']
        Kidney_Stone_Age = request.form['Allergies_Age']
        Jaundice = request.form['High_Blood_Pressure']
        Jaundice_Age= request.form['High_Blood_Pressure_Age']
        Tuberculosis = request.form['Hypothyroidism']
        Tuberculosis_Age = request.form['Hypothyroidism_Age']
        Fainting_Spell = request.form['Fainting_Spell']
        Fainting_Spell_Age= request.form['Fainting_Spell_Age']
        Seizures = request.form['Seizures']
        Seizures_Age = request.form['Seizures_Age']
        Allergies_Seasonal = request.form['Allergies_Seasonal']
        Allergies_Seasonal_Age= request.form['Allergies_Seasonal_Age']
        status= request.form['status']
        cur.execute("INSERT INTO tbl_healthhistoryform2 (ID_Number,Head_Injury,Head_Injury_Age,Surgery,Surgery_Type,Surgery_Age,Allergies,Allergies_Age,High_Blood_Pressure,High_Blood_Pressure_Age,Hypothyroidism,Hypothyroidism_Age,Cancer,Cancer_Type,Cancer_Age,Psoriasis,Psoriasis_Age,Heart_Problem,Heart_Problem_Age,Pneumonia ,Pneumonia_Age,Epilepsy,Epilepsy_Age,Kidney_Stone,Kidney_Stone_Age,Jaundice,Jaundice_Age,Tuberculosis,Tuberculosis_Age,Fainting_Spell,Fainting_Spell_Age,Seizures,Seizures_Age,Allergies_Seasonal,Allergies_Seasonal_Age,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [ID_Number,Head_Injury,Head_Injury_Age,Surgery,Surgery_Type,Surgery_Age,Allergies,Allergies_Age,High_Blood_Pressure,High_Blood_Pressure_Age,Hypothyroidism,Hypothyroidism_Age,
                     Cancer,Cancer_Type,Cancer_Age,Psoriasis,Psoriasis_Age,Heart_Problem,Heart_Problem_Age,Pneumonia ,Pneumonia_Age,Epilepsy,Epilepsy_Age,
                     Kidney_Stone,Kidney_Stone_Age,Jaundice,Jaundice_Age,Tuberculosis,Tuberculosis_Age,Fainting_Spell,Fainting_Spell_Age,Seizures,Seizures_Age,Allergies_Seasonal,Allergies_Seasonal_Age,status])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_profile'))


@app.route('/student/edit-healthinformation2', methods=['POST','GET'])
def student_edit_healthinformation2():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        health = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/edit-health2.html', Notification=Notification,admin=admin,studentapproval=studentapproval,health=health,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/student/edit-healthinformation2/execute/<int:id>', methods=['post','get'])
def student_edit_healthinformation2_execute(id):
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['ID_Number']
        Head_Injury= request.form['Head_Injury']
        Head_Injury_Age = request.form['Head_Injury_Age']
        Surgery = request.form['Surgery']
        Surgery_Type = request.form['Surgery_Type']
        Surgery_Age = request.form['Surgery_Age']
        Allergies = request.form['Allergies']
        Allergies_Age = request.form['Allergies_Age']
        High_Blood_Pressure = request.form['High_Blood_Pressure']
        High_Blood_Pressure_Age = request.form['High_Blood_Pressure_Age']
        Hypothyroidism = request.form['Hypothyroidism']
        Hypothyroidism_Age = request.form['Hypothyroidism_Age']
        Cancer = request.form['Cancer']
        Cancer_Type = request.form['Cancer_Type']
        Cancer_Age = request.form['Cancer_Age']
        Psoriasis= request.form['Psoriasis']
        Psoriasis_Age= request.form['Psoriasis_Age']
        Heart_Problem= request.form['Heart_Problem']
        Heart_Problem_Age = request.form['Heart_Problem_Age']
        Pneumonia = request.form['Pneumonia']
        Pneumonia_Age = request.form['Pneumonia_Age']
        Epilepsy = request.form['Epilepsy']
        Epilepsy_Age = request.form['Epilepsy_Age']
        Kidney_Stone = request.form['Allergies']
        Kidney_Stone_Age = request.form['Allergies_Age']
        Jaundice = request.form['High_Blood_Pressure']
        Jaundice_Age= request.form['High_Blood_Pressure_Age']
        Tuberculosis = request.form['Hypothyroidism']
        Tuberculosis_Age = request.form['Hypothyroidism_Age']
        Fainting_Spell = request.form['Fainting_Spell']
        Fainting_Spell_Age= request.form['Fainting_Spell_Age']
        Seizures = request.form['Seizures']
        Seizures_Age = request.form['Seizures_Age']
        Allergies_Seasonal = request.form['Allergies_Seasonal']
        Allergies_Seasonal_Age= request.form['Allergies_Seasonal_Age']
        status= request.form['status']
        cur.execute("UPDATE tbl_healthhistoryform2 SET ID_Number=%s,Head_Injury=%s,Head_Injury_Age=%s,Surgery=%s,Surgery_Type=%s,Surgery_Age=%s,Allergies=%s,Allergies_Age=%s,High_Blood_Pressure=%s,High_Blood_Pressure_Age=%s,Hypothyroidism=%s,Hypothyroidism_Age=%s,Cancer=%s,Cancer_Type=%s,Cancer_Age=%s,Psoriasis=%s,Psoriasis_Age=%s,Heart_Problem=%s,Heart_Problem_Age=%s,Pneumonia=%s ,Pneumonia_Age=%s,Epilepsy=%s,Epilepsy_Age=%s,Kidney_Stone=%s,Kidney_Stone_Age=%s,Jaundice=%s,Jaundice_Age=%s,Tuberculosis=%s,Tuberculosis_Age=%s,Fainting_Spell=%s,Fainting_Spell_Age=%s,Seizures=%s,Seizures_Age=%s,Allergies_Seasonal=%s,Allergies_Seasonal_Age=%s,status=%s WHERE id = %s", (ID_Number,Head_Injury,Head_Injury_Age,Surgery,Surgery_Type,Surgery_Age,Allergies,Allergies_Age,High_Blood_Pressure,High_Blood_Pressure_Age,Hypothyroidism,Hypothyroidism_Age,
                     Cancer,Cancer_Type,Cancer_Age,Psoriasis,Psoriasis_Age,Heart_Problem,Heart_Problem_Age,Pneumonia ,Pneumonia_Age,Epilepsy,Epilepsy_Age,
                     Kidney_Stone,Kidney_Stone_Age,Jaundice,Jaundice_Age,Tuberculosis,Tuberculosis_Age,Fainting_Spell,Fainting_Spell_Age,Seizures,Seizures_Age,Allergies_Seasonal,Allergies_Seasonal_Age,status,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_profile'))





@app.route('/student/medical-history' , methods=['POST','GET'])
def student_medical_history():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_medical WHERE idnumber = %s' , (session['idnumber'],))
    medical = appointment.fetchall()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s' , (session['idnumber'],))
    medicals = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    return render_template('student/medical-history.html',Notification=Notification, medical=medical, admin=admin,medicals=medicals)

@app.route('/student/appointments' , methods=['POST','GET'])
def student_appointments():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s' , (session['idnumber'],))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    return render_template('student/appointments.html',Notification=Notification ,appointments=appointments, admin=admin)





@app.route('/student/add-appointment' , methods=['POST','GET'])
def student_add_appointment():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
        # Query the database for disabled dates



    # Query the database for disabled dates
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT date FROM disabled_dates_dental")
        rows1 = cur1.fetchall()
        disabled_dates1 = []

    # Convert valid date objects to strings
        for row1 in rows1:
        # Query the database for disabled dates
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT date FROM disabled_dates_dental")
            rows1 = cur1.fetchall()
            disabled_dates1 = []

        # Convert valid date objects to strings
            for row1 in rows1:
                date = row1[0]
                if date is not None:
                    disabled_dates1.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT date FROM disabled_dates")
        rows2 = cur2.fetchall()
        disabled_dates2 = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT date FROM disabled_dates")
            rows2 = cur2.fetchall()
            disabled_dates2 = []

        # Convert valid date objects to strings
            for row2 in rows2:
                date = row2[0]
                if date is not None:
                    disabled_dates2.append(date.strftime("%Y-%m-%d"))


    return render_template('student/add-appointment.html',Notification=Notification, admin=admin,disabled_dates=disabled_dates,disabled_dates1=disabled_dates1,disabled_dates2=disabled_dates2)






@app.route('/student/add-appointment-dentist' , methods=['POST','GET'])
def student_add_appointment_dentist():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
        # Query the database for disabled dates
    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates_dental")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))

    return render_template('student/add-appointment-dentist.html', Notification=Notification,admin=admin,disabled_dates=disabled_dates)



@app.route('/student/add-appointment-nurse' , methods=['POST','GET'])
def student_add_appointment_nurse():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
        # Query the database for disabled dates
    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))

    return render_template('student/add-appointment-nurse.html',Notification=Notification, admin=admin,disabled_dates=disabled_dates)



@app.route('/student/add-appointment-supplementary' , methods=['POST','GET'])
def student_add_appointment_supplementary():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
        # Query the database for disabled dates
    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))

    return render_template('student/add-appointment-supplementary.html', Notification=Notification,admin=admin,disabled_dates=disabled_dates)




@app.route('/student/add-appointment-execute_dental', methods=['post','get'])
def student_add_appointment_execute_dental():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
        # Query the database for disabled dates



    # Query the database for disabled dates
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT date FROM disabled_dates_dental")
        rows1 = cur1.fetchall()
        disabled_dates1 = []

    # Convert valid date objects to strings
        for row1 in rows1:
        # Query the database for disabled dates
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT date FROM disabled_dates_dental")
            rows1 = cur1.fetchall()
            disabled_dates1 = []

        # Convert valid date objects to strings
            for row1 in rows1:
                date = row1[0]
                if date is not None:
                    disabled_dates1.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT date FROM disabled_dates")
        rows2 = cur2.fetchall()
        disabled_dates2 = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT date FROM disabled_dates")
            rows2 = cur2.fetchall()
            disabled_dates2 = []

        # Convert valid date objects to strings
            for row2 in rows2:
                date = row2[0]
                if date is not None:
                    disabled_dates2.append(date.strftime("%Y-%m-%d"))

    if request.method == 'POST':
        idnumber = request.form['idnumber']
        yearlevel = request.form['yearlevel']
        course = request.form['course']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        title = request.form['treatment']
        tiime = request.form['time']
        Start_date = request.form['dateappointment']
        cur.execute('SELECT * FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s', (Start_date,tiime,title))
        result = cur.fetchone()

        # Check the count of the data
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT COUNT(*) FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s", (Start_date,tiime,title))
        count = cur2.fetchone()[0]


        if count == 1:
            return render_template('student/add-appointment.html',error='Appointment is Already FULL!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)
        else:
            # Increment the count by 1 and update the count table
            cur.execute(
                "INSERT INTO tbl_appointments (ID_Number,yearlevel,course,firstname,middlename,lastname,email,gender,mobile,address,Title,Start_date_time,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [idnumber, yearlevel, course, firstname, middlename, lastname, email, gender, mobile, address, title,
                 Start_date, tiime])
            mysql.connection.commit()
            cur.close()

            return render_template('student/add-appointment.html',error2='Appointment is Successful!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)


@app.route('/student/add-appointment-execute_nurse', methods=['post','get'])
def student_add_appointment_execute_nurse():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
        # Query the database for disabled dates



    # Query the database for disabled dates
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT date FROM disabled_dates_dental")
        rows1 = cur1.fetchall()
        disabled_dates1 = []

    # Convert valid date objects to strings
        for row1 in rows1:
        # Query the database for disabled dates
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT date FROM disabled_dates_dental")
            rows1 = cur1.fetchall()
            disabled_dates1 = []

        # Convert valid date objects to strings
            for row1 in rows1:
                date = row1[0]
                if date is not None:
                    disabled_dates1.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT date FROM disabled_dates")
        rows2 = cur2.fetchall()
        disabled_dates2 = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT date FROM disabled_dates")
            rows2 = cur2.fetchall()
            disabled_dates2 = []

        # Convert valid date objects to strings
            for row2 in rows2:
                date = row2[0]
                if date is not None:
                    disabled_dates2.append(date.strftime("%Y-%m-%d"))

    if request.method == 'POST':
        idnumber = request.form['idnumber']
        yearlevel = request.form['yearlevel']
        course = request.form['course']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        title = request.form['treatment']
        tiime = request.form['time']
        Start_date = request.form['dateappointment']
        cur.execute('SELECT * FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s', (Start_date,tiime,title))
        result = cur.fetchone()
        # Check the count of the data
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT COUNT(*) FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s", (Start_date,tiime,title))
        count = cur2.fetchone()[0]


        if count == 10:
            return render_template('student/add-appointment.html',error='Appointment is Already FULL!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)
        else:
            cur.execute(
                "INSERT INTO tbl_appointments (ID_Number,yearlevel,course,firstname,middlename,lastname,email,gender,mobile,address,Title,Start_date_time,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [idnumber,yearlevel,course,firstname,middlename,lastname,email,gender,mobile,address,title,Start_date,tiime])
            mysql.connection.commit()
            cur.close()
            return render_template('student/add-appointment.html',error2='Appointment is Successful!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)


@app.route('/student/add-appointment-execute-supplementary', methods=['post','get'])
def student_add_appointment_execute_supplementary():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
        # Query the database for disabled dates



    # Query the database for disabled dates
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT date FROM disabled_dates_dental")
        rows1 = cur1.fetchall()
        disabled_dates1 = []

    # Convert valid date objects to strings
        for row1 in rows1:
        # Query the database for disabled dates
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT date FROM disabled_dates_dental")
            rows1 = cur1.fetchall()
            disabled_dates1 = []

        # Convert valid date objects to strings
            for row1 in rows1:
                date = row1[0]
                if date is not None:
                    disabled_dates1.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT date FROM disabled_dates")
        rows2 = cur2.fetchall()
        disabled_dates2 = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT date FROM disabled_dates")
            rows2 = cur2.fetchall()
            disabled_dates2 = []

        # Convert valid date objects to strings
            for row2 in rows2:
                date = row2[0]
                if date is not None:
                    disabled_dates2.append(date.strftime("%Y-%m-%d"))

    if request.method == 'POST':
        idnumber = request.form['idnumber']
        yearlevel = request.form['yearlevel']
        course = request.form['course']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        title = request.form['treatment']
        tiime = request.form['time']
        Start_date = request.form['dateappointment']
        cur.execute('SELECT * FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s', (Start_date,tiime,title))
        result = cur.fetchone()
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT COUNT(*) FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s", (Start_date,tiime,title))
        count = cur2.fetchone()[0]
        if count == 10:
            return render_template('student/add-appointment.html',error='Appointment is Already FULL!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)
        else:
            cur.execute(
                "INSERT INTO tbl_appointments (ID_Number,yearlevel,course,firstname,middlename,lastname,email,gender,mobile,address,Title,Start_date_time,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [idnumber,yearlevel,course,firstname,middlename,lastname,email,gender,mobile,address,title,Start_date,tiime])
            mysql.connection.commit()
            cur.close()
            return render_template('student/add-appointment.html',error2='Appointment is Successful!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)








@app.route('/student/add-appointment-execute', methods=['post','get'])
def student_add_appointment_execute():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        yearlevel = request.form['yearlevel']
        course = request.form['course']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        title = request.form['treatment']
        Start_date = request.form['dateappointment']
        cur.execute(
                "INSERT INTO tbl_appointments (ID_Number,yearlevel,course,firstname,middlename,lastname,email,gender,mobile,address,Title,Start_date_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [idnumber,yearlevel,course,firstname,middlename,lastname,email,gender,mobile,address,title,Start_date])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_add_appointment'))

@app.route('/student/calendar' , methods=['POST','GET'])
def student_calendar():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER BY id')
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    return render_template('student/calendar.html', appointments=appointments, admin=admin,Notification=Notification)

@app.route('/student/compose' , methods=['POST','GET'])
def student_compose():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/compose.html', admin=admin,Notification=Notification)

@app.route('/student/send_email', methods=['POST'])
def student_send_email():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        recipient = request.form['recipient']
        message = request.form['textarea']

        # Create the message
        msg = Message(subject='New message from your school Clinic',
                      recipients=[recipient])  # Replace with your email address
        msg.body = f"You have received a new message from {name}: \n\n{message}"

        try:
            # Send the message
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending your message: {e}', 'error')

    return render_template('student/compose.html', admin=admin,Notification=Notification)



@app.route('/student/compose-cancel/<int:id>' , methods=['POST','GET'])
def student_compose_cancel(id):
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_appointments WHERE id = %s', (id,))
        mail = cursor.fetchone()
        status = 'Appointment Canceled'
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status = %s WHERE id = %s', (status, id))
        mysql.connection.commit()
        status1 = 8
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status1 = %s WHERE id = %s', (status1, id))
        mysql.connection.commit()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()

    return render_template('student/compose-cancel.html', admin=admin,mail=mail,Notification=Notification)






@app.route('/student/inbox' , methods=['POST','GET'])
def student_inbox():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/inbox.html', admin=admin,Notification=Notification)

@app.route('/student/mail-view' , methods=['POST','GET'])
def student_mail_view():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()

    return render_template('student/mail-view.html', admin=admin,Notification=Notification)


@app.route('/student/settings' , methods=['POST','GET'])
def student_settings():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('student/settings.html', admin=admin,Notification=Notification)


@app.route('/student/logout', methods=['POST', 'GET'])
def student_logout():
    if not session.get('id'):
        return redirect(url_for('student_login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (4, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('student/login.html', error='Your are not a STUDENT Member!!')
    if session.get('id'):
        session['id'] = None
        session['idnumber'] = None
        return redirect(url_for('landingpage'))



#--------------------------------------------------------------------------------------------------faculty Area-----------------------------------------------------------

@app.route('/faculty/forgot-password', methods=['GET', 'POST'])
def faculty_forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Check if email exists in the database
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM tbl_students WHERE Email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            # Generate a new password
            new_password = generate_password()

            # Update the password in the database
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("UPDATE tbl_students SET Password = %s WHERE Email = %s", (new_password, email))
            mysql.connection.commit()
            cur.close()

            # Send the new password to the user's email
            msg = Message('Password Reset', sender='qsuclinic@gmail.com', recipients=[email])
            msg.body = f"Your new password is: {new_password}"
            mail.send(msg)

            flash("A new password has been sent to your email.")
            return render_template('/faculty/forgotpassword.html')
        else:
            flash("Email address not found.")
            return redirect(url_for('faculty_forgot_password'))

    return render_template('/faculty/forgotpassword.html')


@app.route('/faculty/register', methods=['POST','GET'])
def faculty_register():
    return render_template('faculty/register.html')

@app.route('/faculty/register/execute', methods=['post','get'])
def faculty_register_execute():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        Position = request.form['Position']
        Course = request.form['Course']
        First_name = request.form['firstname']
        Middle_name = request.form['middlename']
        Last_name = request.form['lastname']
        Gender = request.form['gender']
        Home_Address = request.form['homeaddress']
        Civil_status = request.form['civilstatus']
        Place_of_birth = request.form['placeofbirth']
        Birthdate = request.form['birthdate']
        Cp_number = request.form['mobile']
        Boarding_address = request.form['boardinghouse']
        Nationality = request.form['nationality']
        Religion = request.form['religion']
        Email = request.form['email']
        Password = request.form['password']
        cur.execute('SELECT * FROM tbl_students WHERE Email = %s', (Email,))
        cur2.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (idnumber,))
        result = cur.fetchone()
        result2 = cur2.fetchone()
        Userlevel_ID = 4
        if result2:
            return render_template('faculty/register.html', error2='ID-Number already exist!')
        if result:
            return render_template('faculty/register.html', error='Email already exist!')
        else:
            cur.execute(
                "INSERT INTO tbl_students (idnumber,Position,Course,First_name,Middle_name,Last_name,Gender,Home_Address,Civil_status,Place_of_birth,Birthdate,Cp_number,Boarding_address,Nationality,Religion,Email,Password,Userlevel_ID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [idnumber,Position,Course,First_name,Middle_name,Last_name,Gender,Home_Address,Civil_status,Place_of_birth,Birthdate,Cp_number,Boarding_address,Nationality,Religion,Email,Password,Userlevel_ID])
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('faculty_login'))

@app.route('/faculty/login', methods=['POST','GET'])
def faculty_login():
    return render_template('faculty/login.html')

@app.route('/faculty/loginexecute', methods=['POST','GET'])
def faculty_loginexecute():
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE idnumber =%s AND password = %s ', (idnumber, password))
        account = cursor.fetchone()
        if account:
            cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND idnumber = %s', (3, idnumber))
            not_approved = cursor.fetchone()
            cursor2.execute('SELECT * FROM tbl_students WHERE status =%s AND idnumber = %s', (0, idnumber))
            not_approved2 = cursor2.fetchone()
            if not_approved:
                return render_template('faculty/login.html',error='Your are not a faculty Member!!')
            if not_approved2:
                return render_template('faculty/login.html',error='Your Account is NOT Yet Approved')
            else:
                session['loggedin'] = True
                session['id'] = account['id']
                session['idnumber'] = account['idnumber']
                return redirect(url_for('faculty_dashboard'))
    return render_template('faculty/login.html',error='Invalid Username or Password')

@app.route('/faculty/dashboard', methods=['POST','GET'])
def faculty_dashboard():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')

    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        announcement = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        announcement.execute('SELECT * FROM tbl_announcements ORDER BY id')
        announcements = announcement.fetchall()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/index.html', admin=admin,announcements=announcements,Notification=Notification)

@app.route('/faculty/profile', methods=['POST','GET'])
def faculty_profile():
    if not session.get('id'):
        return redirect(url_for('student_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')

    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        studentapproval = cursorapprove.fetchone()
        cursorapprove1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval1 = cursorapprove1.fetchone()
        cursorapprove2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval2 = cursorapprove2.fetchone()
        cursorapprove3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval3 = cursorapprove3.fetchone()
        cursorapprove4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        studentapproval4 = cursorapprove4.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle  WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1  WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2  WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/profile.html',Notification=Notification,admin=admin,studentapproval4=studentapproval4,studentapproval=studentapproval,studentapproval1=studentapproval1,studentapproval2=studentapproval2,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2,studentapproval3=studentapproval3)

@app.route('/faculty/edit-profile', methods=['POST','GET'])
def faculty_edit_profile():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number= %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/edit-profile.html',Notification=Notification,admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)


@app.route('/faculty/edit-profile/execute/<int:id>', methods=['post','get'])
def faculty_edit_profile_execute(id):
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        birthdate = request.form['birthdate']
        gender = request.form['gender']
        position = request.form['position']
        homeaddress = request.form['homeaddress']
        civilstatus = request.form['civilstatus']
        placeofbirth = request.form['placeofbirth']
        mobile = request.form['mobile']
        boardinghouse = request.form['boardinghouse']
        nationality = request.form['nationality']
        religion = request.form['religion']
        email = request.form['email']
        cur.execute("UPDATE tbl_students SET 	First_name=%s,Middle_name=%s,Last_name=%s,Birthdate=%s,Gender=%s,position=%s,Home_Address=%s,Civil_status=%s,Place_of_birth=%s,Cp_number=%s,Boarding_address=%s,Nationality=%s,Religion=%s,Email=%s WHERE id = %s",
                    (firstname,middlename,lastname,birthdate,gender,position,homeaddress,civilstatus,placeofbirth,mobile,boardinghouse,nationality,religion,email ,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('faculty_profile'))

@app.route('/faculty/edit-profilefamily', methods=['POST','GET'])
def faculty_edit_profilefamily():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1  WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/edit-profilefamily.html', Notification=Notification,admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)


@app.route('/faculty/add-profilefamily', methods=['POST','GET'])
def faculty_add_profilefamily():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1  WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/add-profilefamily.html',Notification=Notification,admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)


@app.route('/faculty/edit-profilefamily/execute/<int:id>', methods=['post','get'])
def faculty_edit_profilefamily_execute(id):
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['idnumber']
        Gaurdian = request.form['guardian']
        Father_name = request.form['fathersname']
        Father_address = request.form['fatheraddress']
        Father_age = request.form['fatherage']
        Father_occupation = request.form['fatheroccupation']
        Father_educational_attainment = request.form['fathereducational']
        Mother_name = request.form['mothersname']
        Mother_Address = request.form['motheraddress']
        Mother_age = request.form['motherage']
        Mother_occupation = request.form['motheroccupation']
        Mother_educational_attainment = request.form['mothereducational']
        status = request.form['status']
        cur.execute("UPDATE tbl_familybackground SET ID_Number=%s,Gaurdian=%s,Father_name=%s,Father_address=%s,Father_age=%s,Father_occupation=%s,Father_educational_attainment=%s,Mother_name=%s,Mother_Address=%s,Mother_age=%s,Mother_occupation=%s,Mother_educational_attainment=%s,status=%s WHERE id = %s",(ID_Number,Gaurdian,Father_name,Father_address,Father_age,Father_occupation,Father_educational_attainment,Mother_name,Mother_Address,Mother_age,Mother_occupation,Mother_educational_attainment,status,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('faculty_profile'))





@app.route('/faculty/add-profilefamily/execute', methods=['post','get'])
def faculty_add_profilefamily_execute():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['idnumber']
        Gaurdian = request.form['guardian']
        Father_name = request.form['fathersname']
        Father_address = request.form['fatheraddress']
        Father_age = request.form['fatherage']
        Father_occupation = request.form['fatheroccupation']
        Father_educational_attainment = request.form['fathereducational']
        Mother_name = request.form['mothersname']
        Mother_Address = request.form['motheraddress']
        Mother_age = request.form['motherage']
        Mother_occupation = request.form['motheroccupation']
        Mother_educational_attainment = request.form['mothereducational']
        status = request.form['status']
        cur.execute("INSERT INTO tbl_familybackground (ID_Number,Gaurdian,Father_name,Father_address,Father_age,Father_occupation,Father_educational_attainment,Mother_name,Mother_Address,Mother_age,Mother_occupation,Mother_educational_attainment,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[ID_Number,Gaurdian,Father_name,Father_address,Father_age,Father_occupation,Father_educational_attainment,Mother_name,Mother_Address,Mother_age,Mother_occupation,Mother_educational_attainment,status])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('faculty_profile'))


@app.route('/faculty/add-lifestyle', methods=['POST','GET'])
def faculty_add_lifestyle():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/add-lifestyle.html', Notification=Notification,admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/faculty/add-lifestyle/execute', methods=['post','get'])
def faculty_add_lifestyle_execute():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['idnumber']
        Do_you_Smoke = request.form['doyousmoke']
        How_many_stick = request.form['howmany']
        Do_someone = request.form['dosomeone']
        Do_drink_Alchohol = request.form['drinkalchohol']
        How_often = request.form['howoften']
        status = request.form['status']
        cur.execute("INSERT INTO tbl_lifestyle (ID_Number,Do_you_Smoke,How_many_stick,Do_someone,Do_drink_Alchohol ,How_often,status) VALUES (%s,%s,%s,%s,%s,%s,%s)",[ID_Number,Do_you_Smoke,How_many_stick,Do_someone,Do_drink_Alchohol ,How_often,status])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('faculty_profile'))


@app.route('/faculty/edit-lifestyle', methods=['POST','GET'])
def faculty_edit_lifestyle():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM tbl_familybackground WHERE ID_Number = %s', (session['idnumber'],))
        familybackgroundinfos = cursor1.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_lifestyle WHERE ID_Number = %s', (session['idnumber'],))
        lifestyleinfos = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/edit-lifestyle.html',Notification=Notification,admin=admin,studentapproval=studentapproval,familybackgroundinfos=familybackgroundinfos,lifestyleinfos=lifestyleinfos,healthinformation1=healthinformation1,healthinformation2=healthinformation2)


@app.route('/faculty/edit-lifestyle/execute/<int:id>', methods=['post','get'])
def faculty_edit_lifestyle_execute(id):
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        doyousmoke = request.form['doyousmoke']
        howmany = request.form['howmany']
        dosomeone = request.form['dosomeone']
        drinkalchohol = request.form['drinkalchohol']
        howoften = request.form['howoften']
        status = request.form['status']
        idnumber= request.form['idnumber']
        cur.execute("UPDATE tbl_lifestyle SET Do_you_Smoke=%s,How_many_stick=%s,Do_someone=%s,Do_drink_Alchohol=%s,How_often=%s,ID_Number=%s,status=%s WHERE id = %s",
                    (doyousmoke,howmany,dosomeone,drinkalchohol,howoften,idnumber,status,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('faculty_profile'))




@app.route('/faculty/add-healthinformation1', methods=['POST','GET'])
def faculty_add_healthinformation1():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        health = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/add-health.html',Notification=Notification, admin=admin,studentapproval=studentapproval,health=health,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/faculty/add-healthinformation1/execute', methods=['post','get'])
def faculty_add_healthinformation1_execute():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['ID_Number']
        Asthma= request.form['Asthma']
        Asthma_Age = request.form['Asthma_Age']
        Hepatitis = request.form['Hepatitis']
        Hepatitis_Age = request.form['Hepatitis_Age']
        High_Cholesterol = request.form['High_Cholesterol']
        High_Cholesterol_Age = request.form['High_Cholesterol_Age']
        Goiter = request.form['Goiter']
        Goiter_Age = request.form['Goiter_Age']
        Leukemia = request.form['Leukemia']
        Leukemia_Age = request.form['Leukemia_Age']
        Angina = request.form['Angina']
        Angina_Age = request.form['Angina_Age']
        Heart_Murmur = request.form['Heart_Murmur']
        Heart_Murmur_Age = request.form['Heart_Murmur_Age']
        Stroke = request.form['Stroke']
        Stroke_Age = request.form['Stroke_Age']
        Kidney_Disease= request.form['Kidney_Disease']
        Kidney_Disease_Age = request.form['Kidney_Disease_Age']
        Anemia = request.form['Anemia']
        Anemia_Age = request.form['Anemia_Age']
        Stomach_or_Peptic_Ulcer = request.form['Stomach_or_Peptic_Ulcer']
        Stomach_or_Peptic_Ulcer_Age = request.form['Stomach_or_Peptic_Ulcer_Age']
        status= request.form['status']
        cur.execute("INSERT INTO tbl_healthhistoryform1 (ID_Number,Asthma,Asthma_Age,Hepatitis,Hepatitis_Age ,High_Cholesterol,High_Cholesterol_Age,Goiter,Goiter_Age,Leukemia,Leukemia_Age,Angina,Angina_Age,Heart_Murmur,Heart_Murmur_Age,Stroke,Stroke_Age,Kidney_Disease,Kidney_Disease_Age,Anemia,Anemia_Age,Stomach_or_Peptic_Ulcer,Stomach_or_Peptic_Ulcer_Age,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [ID_Number,Asthma,Asthma_Age,Hepatitis,Hepatitis_Age ,High_Cholesterol,High_Cholesterol_Age,Goiter,Goiter_Age,Leukemia,Leukemia_Age,Angina,Angina_Age,Heart_Murmur,Heart_Murmur_Age,Stroke,Stroke_Age,Kidney_Disease,Kidney_Disease_Age,Anemia,Anemia_Age,Stomach_or_Peptic_Ulcer,Stomach_or_Peptic_Ulcer_Age,status])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('faculty_profile'))

@app.route('/faculty/edit-healthinformation1', methods=['POST','GET'])
def faculty_edit_healthinformation1():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        health = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/edit-health.html', Notification=Notification,admin=admin,studentapproval=studentapproval,health=health,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/faculty/edit-healthinformation1/execute/<int:id>', methods=['post','get'])
def faculty_edit_healthinformation1_execute(id):
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['ID_Number']
        Asthma= request.form['Asthma']
        Asthma_Age = request.form['Asthma_Age']
        Hepatitis = request.form['Hepatitis']
        Hepatitis_Age = request.form['Hepatitis_Age']
        High_Cholesterol = request.form['High_Cholesterol']
        High_Cholesterol_Age = request.form['High_Cholesterol_Age']
        Goiter = request.form['Goiter']
        Goiter_Age = request.form['Goiter_Age']
        Leukemia = request.form['Leukemia']
        Leukemia_Age = request.form['Leukemia_Age']
        Angina = request.form['Angina']
        Angina_Age = request.form['Angina_Age']
        Heart_Murmur = request.form['Heart_Murmur']
        Heart_Murmur_Age = request.form['Heart_Murmur_Age']
        Stroke = request.form['Stroke']
        Stroke_Age = request.form['Stroke_Age']
        Kidney_Disease= request.form['Kidney_Disease']
        Kidney_Disease_Age = request.form['Kidney_Disease_Age']
        Anemia = request.form['Anemia']
        Anemia_Age = request.form['Anemia_Age']
        Stomach_or_Peptic_Ulcer = request.form['Stomach_or_Peptic_Ulcer']
        Stomach_or_Peptic_Ulcer_Age = request.form['Stomach_or_Peptic_Ulcer_Age']
        status= request.form['status']
        cur.execute("UPDATE tbl_healthhistoryform1 SET ID_Number=%s,Asthma=%s,Asthma_Age=%s,Hepatitis=%s,Hepatitis_Age=%s ,High_Cholesterol=%s,High_Cholesterol_Age=%s,Goiter=%s,Goiter_Age=%s,Leukemia=%s,Leukemia_Age=%s,Angina=%s,Angina_Age=%s,Heart_Murmur=%s,Heart_Murmur_Age=%s,Stroke=%s,Stroke_Age=%s,Kidney_Disease=%s,Kidney_Disease_Age=%s,Anemia=%s,Anemia_Age=%s,Stomach_or_Peptic_Ulcer=%s,Stomach_or_Peptic_Ulcer_Age=%s,status=%s WHERE id = %s",(ID_Number,Asthma,Asthma_Age,Hepatitis,Hepatitis_Age ,High_Cholesterol,High_Cholesterol_Age,Goiter,Goiter_Age,Leukemia,Leukemia_Age,Angina,Angina_Age,Heart_Murmur,Heart_Murmur_Age,Stroke,Stroke_Age,Kidney_Disease,Kidney_Disease_Age,Anemia,Anemia_Age,Stomach_or_Peptic_Ulcer,Stomach_or_Peptic_Ulcer_Age,status,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('faculty_profile'))


@app.route('/faculty/add-healthinformation2', methods=['POST','GET'])
def faculty_add_healthinformation2():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        health = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/add-health2.html',Notification=Notification, admin=admin,studentapproval=studentapproval,health=health,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/faculty/add-healthinformation2/execute', methods=['post','get'])
def faculty_add_healthinformation2_execute():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['ID_Number']
        Head_Injury= request.form['Head_Injury']
        Head_Injury_Age = request.form['Head_Injury_Age']
        Surgery = request.form['Surgery']
        Surgery_Type = request.form['Surgery_Type']
        Surgery_Age = request.form['Surgery_Age']
        Allergies = request.form['Allergies']
        Allergies_Age = request.form['Allergies_Age']
        High_Blood_Pressure = request.form['High_Blood_Pressure']
        High_Blood_Pressure_Age = request.form['High_Blood_Pressure_Age']
        Hypothyroidism = request.form['Hypothyroidism']
        Hypothyroidism_Age = request.form['Hypothyroidism_Age']
        Cancer = request.form['Cancer']
        Cancer_Type = request.form['Cancer_Type']
        Cancer_Age = request.form['Cancer_Age']
        Psoriasis= request.form['Psoriasis']
        Psoriasis_Age= request.form['Psoriasis_Age']
        Heart_Problem= request.form['Heart_Problem']
        Heart_Problem_Age = request.form['Heart_Problem_Age']
        Pneumonia = request.form['Pneumonia']
        Pneumonia_Age = request.form['Pneumonia_Age']
        Epilepsy = request.form['Epilepsy']
        Epilepsy_Age = request.form['Epilepsy_Age']
        Kidney_Stone = request.form['Allergies']
        Kidney_Stone_Age = request.form['Allergies_Age']
        Jaundice = request.form['High_Blood_Pressure']
        Jaundice_Age= request.form['High_Blood_Pressure_Age']
        Tuberculosis = request.form['Hypothyroidism']
        Tuberculosis_Age = request.form['Hypothyroidism_Age']
        Fainting_Spell = request.form['Fainting_Spell']
        Fainting_Spell_Age= request.form['Fainting_Spell_Age']
        Seizures = request.form['Seizures']
        Seizures_Age = request.form['Seizures_Age']
        Allergies_Seasonal = request.form['Allergies_Seasonal']
        Allergies_Seasonal_Age= request.form['Allergies_Seasonal_Age']
        status= request.form['status']
        cur.execute("INSERT INTO tbl_healthhistoryform2 (ID_Number,Head_Injury,Head_Injury_Age,Surgery,Surgery_Type,Surgery_Age,Allergies,Allergies_Age,High_Blood_Pressure,High_Blood_Pressure_Age,Hypothyroidism,Hypothyroidism_Age,Cancer,Cancer_Type,Cancer_Age,Psoriasis,Psoriasis_Age,Heart_Problem,Heart_Problem_Age,Pneumonia ,Pneumonia_Age,Epilepsy,Epilepsy_Age,Kidney_Stone,Kidney_Stone_Age,Jaundice,Jaundice_Age,Tuberculosis,Tuberculosis_Age,Fainting_Spell,Fainting_Spell_Age,Seizures,Seizures_Age,Allergies_Seasonal,Allergies_Seasonal_Age,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [ID_Number,Head_Injury,Head_Injury_Age,Surgery,Surgery_Type,Surgery_Age,Allergies,Allergies_Age,High_Blood_Pressure,High_Blood_Pressure_Age,Hypothyroidism,Hypothyroidism_Age,
                     Cancer,Cancer_Type,Cancer_Age,Psoriasis,Psoriasis_Age,Heart_Problem,Heart_Problem_Age,Pneumonia ,Pneumonia_Age,Epilepsy,Epilepsy_Age,
                     Kidney_Stone,Kidney_Stone_Age,Jaundice,Jaundice_Age,Tuberculosis,Tuberculosis_Age,Fainting_Spell,Fainting_Spell_Age,Seizures,Seizures_Age,Allergies_Seasonal,Allergies_Seasonal_Age,status])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('faculty_profile'))


@app.route('/faculty/edit-healthinformation2', methods=['POST','GET'])
def faculty_edit_healthinformation2():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('SELECT * FROM tbl_students WHERE idnumber = %s', (session['idnumber'],))
        studentapproval = cursorapprove.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students  WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        health = cursor2.fetchone()
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute('SELECT * FROM tbl_healthhistoryform1 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation1 = cursor3.fetchone()
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute('SELECT * FROM tbl_healthhistoryform2 WHERE ID_Number = %s', (session['idnumber'],))
        healthinformation2 = cursor4.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/edit-health2.html',Notification=Notification, admin=admin,studentapproval=studentapproval,health=health,healthinformation1=healthinformation1,healthinformation2=healthinformation2)

@app.route('/faculty/edit-healthinformation2/execute/<int:id>', methods=['post','get'])
def faculty_edit_healthinformation2_execute(id):
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        ID_Number = request.form['ID_Number']
        Head_Injury= request.form['Head_Injury']
        Head_Injury_Age = request.form['Head_Injury_Age']
        Surgery = request.form['Surgery']
        Surgery_Type = request.form['Surgery_Type']
        Surgery_Age = request.form['Surgery_Age']
        Allergies = request.form['Allergies']
        Allergies_Age = request.form['Allergies_Age']
        High_Blood_Pressure = request.form['High_Blood_Pressure']
        High_Blood_Pressure_Age = request.form['High_Blood_Pressure_Age']
        Hypothyroidism = request.form['Hypothyroidism']
        Hypothyroidism_Age = request.form['Hypothyroidism_Age']
        Cancer = request.form['Cancer']
        Cancer_Type = request.form['Cancer_Type']
        Cancer_Age = request.form['Cancer_Age']
        Psoriasis= request.form['Psoriasis']
        Psoriasis_Age= request.form['Psoriasis_Age']
        Heart_Problem= request.form['Heart_Problem']
        Heart_Problem_Age = request.form['Heart_Problem_Age']
        Pneumonia = request.form['Pneumonia']
        Pneumonia_Age = request.form['Pneumonia_Age']
        Epilepsy = request.form['Epilepsy']
        Epilepsy_Age = request.form['Epilepsy_Age']
        Kidney_Stone = request.form['Allergies']
        Kidney_Stone_Age = request.form['Allergies_Age']
        Jaundice = request.form['High_Blood_Pressure']
        Jaundice_Age= request.form['High_Blood_Pressure_Age']
        Tuberculosis = request.form['Hypothyroidism']
        Tuberculosis_Age = request.form['Hypothyroidism_Age']
        Fainting_Spell = request.form['Fainting_Spell']
        Fainting_Spell_Age= request.form['Fainting_Spell_Age']
        Seizures = request.form['Seizures']
        Seizures_Age = request.form['Seizures_Age']
        Allergies_Seasonal = request.form['Allergies_Seasonal']
        Allergies_Seasonal_Age= request.form['Allergies_Seasonal_Age']
        status= request.form['status']
        cur.execute("UPDATE tbl_healthhistoryform2 SET ID_Number=%s,Head_Injury=%s,Head_Injury_Age=%s,Surgery=%s,Surgery_Type=%s,Surgery_Age=%s,Allergies=%s,Allergies_Age=%s,High_Blood_Pressure=%s,High_Blood_Pressure_Age=%s,Hypothyroidism=%s,Hypothyroidism_Age=%s,Cancer=%s,Cancer_Type=%s,Cancer_Age=%s,Psoriasis=%s,Psoriasis_Age=%s,Heart_Problem=%s,Heart_Problem_Age=%s,Pneumonia=%s ,Pneumonia_Age=%s,Epilepsy=%s,Epilepsy_Age=%s,Kidney_Stone=%s,Kidney_Stone_Age=%s,Jaundice=%s,Jaundice_Age=%s,Tuberculosis=%s,Tuberculosis_Age=%s,Fainting_Spell=%s,Fainting_Spell_Age=%s,Seizures=%s,Seizures_Age=%s,Allergies_Seasonal=%s,Allergies_Seasonal_Age=%s,status=%s WHERE id = %s", (ID_Number,Head_Injury,Head_Injury_Age,Surgery,Surgery_Type,Surgery_Age,Allergies,Allergies_Age,High_Blood_Pressure,High_Blood_Pressure_Age,Hypothyroidism,Hypothyroidism_Age,
                     Cancer,Cancer_Type,Cancer_Age,Psoriasis,Psoriasis_Age,Heart_Problem,Heart_Problem_Age,Pneumonia ,Pneumonia_Age,Epilepsy,Epilepsy_Age,
                     Kidney_Stone,Kidney_Stone_Age,Jaundice,Jaundice_Age,Tuberculosis,Tuberculosis_Age,Fainting_Spell,Fainting_Spell_Age,Seizures,Seizures_Age,Allergies_Seasonal,Allergies_Seasonal_Age,status,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('faculty_profile'))





@app.route('/faculty/medical-history' , methods=['POST','GET'])
def faculty_medical_history():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_medical WHERE idnumber = %s' , (session['idnumber'],))
    medical = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    return render_template('faculty/medical-history.html', medical=medical, admin=admin,Notification=Notification)

@app.route('/faculty/appointments' , methods=['POST','GET'])
def faculty_appointments():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s' , (session['idnumber'],))
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    return render_template('faculty/appointments.html', appointments=appointments, admin=admin,Notification=Notification)





@app.route('/faculty/add-appointment' , methods=['POST','GET'])
def faculty_add_appointment():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        # Query the database for disabled dates
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()



    # Query the database for disabled dates
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT date FROM disabled_dates_dental")
        rows1 = cur1.fetchall()
        disabled_dates1 = []

    # Convert valid date objects to strings
        for row1 in rows1:
        # Query the database for disabled dates
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT date FROM disabled_dates_dental")
            rows1 = cur1.fetchall()
            disabled_dates1 = []

        # Convert valid date objects to strings
            for row1 in rows1:
                date = row1[0]
                if date is not None:
                    disabled_dates1.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT date FROM disabled_dates")
        rows2 = cur2.fetchall()
        disabled_dates2 = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT date FROM disabled_dates")
            rows2 = cur2.fetchall()
            disabled_dates2 = []

        # Convert valid date objects to strings
            for row2 in rows2:
                date = row2[0]
                if date is not None:
                    disabled_dates2.append(date.strftime("%Y-%m-%d"))


    return render_template('faculty/add-appointment.html',Notification=Notification, admin=admin,disabled_dates=disabled_dates,disabled_dates1=disabled_dates1,disabled_dates2=disabled_dates2)









@app.route('/faculty/add-appointment-execute', methods=['post','get'])
def faculty_add_appointment_execute():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        yearlevel = request.form['yearlevel']
        course = request.form['course']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        title = request.form['treatment']
        Start_date = request.form['dateappointment']
        cur.execute('SELECT * FROM tbl_appointments WHERE Start_date_time = %s', (Start_date,))
        result = cur.fetchone()
        if result:
            return redirect(url_for('student_add_appointment',admin=admin, error='Appointment already taken!!'))
        else:
            cur.execute(
                "INSERT INTO tbl_appointments (ID_Number,yearlevel,course,firstname,middlename,lastname,email,gender,mobile,address,Title,Start_date_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [idnumber,yearlevel,course,firstname,middlename,lastname,email,gender,mobile,address,title,Start_date])
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('faculty_add_appointment'))






@app.route('/faculty/add-appointment-dentist' , methods=['POST','GET'])
def faculty_add_appointment_dentist():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        # Query the database for disabled dates
    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates_dental")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))

    return render_template('faculty/add-appointment-dentist.html', admin=admin,disabled_dates=disabled_dates,Notification=Notification)




@app.route('/faculty/add-appointment-execute_dental', methods=['post','get'])
def faculty_add_appointment_execute_dental():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        # Query the database for disabled dates



    # Query the database for disabled dates
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT date FROM disabled_dates_dental")
        rows1 = cur1.fetchall()
        disabled_dates1 = []

    # Convert valid date objects to strings
        for row1 in rows1:
        # Query the database for disabled dates
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT date FROM disabled_dates_dental")
            rows1 = cur1.fetchall()
            disabled_dates1 = []

        # Convert valid date objects to strings
            for row1 in rows1:
                date = row1[0]
                if date is not None:
                    disabled_dates1.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT date FROM disabled_dates")
        rows2 = cur2.fetchall()
        disabled_dates2 = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT date FROM disabled_dates")
            rows2 = cur2.fetchall()
            disabled_dates2 = []

        # Convert valid date objects to strings
            for row2 in rows2:
                date = row2[0]
                if date is not None:
                    disabled_dates2.append(date.strftime("%Y-%m-%d"))

    if request.method == 'POST':
        idnumber = request.form['idnumber']
        position = request.form['position']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        title = request.form['treatment']
        tiime = request.form['time']
        Start_date = request.form['dateappointment']
        cur.execute('SELECT * FROM tbl_appointments WHERE Start_date_time = %s AND time = %s', (Start_date,tiime))
        result = cur.fetchone()
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT COUNT(*) FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s", (Start_date,tiime,title))
        count = cur2.fetchone()[0]
        if count == 1:
            return render_template('student/add-appointment.html',error='Appointment is Already FULL!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)
        else:
            cur.execute(
                "INSERT INTO tbl_appointments (ID_Number,position,firstname,middlename,lastname,email,gender,mobile,address,Title,Start_date_time,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [idnumber, position, firstname, middlename, lastname, email, gender, mobile, address, title, Start_date,
                 tiime])
            mysql.connection.commit()
            cur.close()
            return render_template('faculty/add-appointment.html',error2='Appointment is Successful!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2)






@app.route('/faculty/add-appointment-nurse' , methods=['POST','GET'])
def faculty_add_appointment_nurse():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        # Query the database for disabled dates
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))

    return render_template('faculty/add-appointment-nurse.html', admin=admin,disabled_dates=disabled_dates,Notification=Notification)



@app.route('/faculty/add-appointment-supplementary' , methods=['POST','GET'])
def faculty_add_appointment_supplementary():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        # Query the database for disabled dates
    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))

    return render_template('faculty/add-appointment-supplementary.html', admin=admin,disabled_dates=disabled_dates,Notification=Notification)



@app.route('/faculty/add-appointment-execute_nurse', methods=['post','get'])
def faculty_add_appointment_execute_nurse():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        # Query the database for disabled dates
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()



    # Query the database for disabled dates
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT date FROM disabled_dates_dental")
        rows1 = cur1.fetchall()
        disabled_dates1 = []

    # Convert valid date objects to strings
        for row1 in rows1:
        # Query the database for disabled dates
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT date FROM disabled_dates_dental")
            rows1 = cur1.fetchall()
            disabled_dates1 = []

        # Convert valid date objects to strings
            for row1 in rows1:
                date = row1[0]
                if date is not None:
                    disabled_dates1.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT date FROM disabled_dates")
        rows2 = cur2.fetchall()
        disabled_dates2 = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT date FROM disabled_dates")
            rows2 = cur2.fetchall()
            disabled_dates2 = []

        # Convert valid date objects to strings
            for row2 in rows2:
                date = row2[0]
                if date is not None:
                    disabled_dates2.append(date.strftime("%Y-%m-%d"))

    if request.method == 'POST':
        idnumber = request.form['idnumber']
        position = request.form['position']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        title = request.form['treatment']
        tiime = request.form['time']
        Start_date = request.form['dateappointment']
        cur.execute('SELECT * FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s', (Start_date,tiime,title))
        result = cur.fetchone()
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT COUNT(*) FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s", (Start_date,tiime,title))
        count = cur2.fetchone()[0]
        if count == 10:
            return render_template('student/add-appointment.html',error='Appointment is Already FULL!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)
        else:
            cur.execute("INSERT INTO tbl_appointments (ID_Number,position,firstname,middlename,lastname,email,gender,mobile,address,Title,Start_date_time,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idnumber,position,firstname,middlename,lastname,email,gender,mobile,address,title,Start_date,tiime])
            mysql.connection.commit()
            cur.close()
            return render_template('faculty/add-appointment.html',error2='Appointment is Successful!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)



@app.route('/faculty/add-appointment-execute-supplementary', methods=['post','get'])
def faculty_add_appointment_execute_supplementary():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        # Query the database for disabled dates
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()





    # Query the database for disabled dates
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT date FROM disabled_dates_dental")
        rows1 = cur1.fetchall()
        disabled_dates1 = []

    # Convert valid date objects to strings
        for row1 in rows1:
        # Query the database for disabled dates
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT date FROM disabled_dates_dental")
            rows1 = cur1.fetchall()
            disabled_dates1 = []

        # Convert valid date objects to strings
            for row1 in rows1:
                date = row1[0]
                if date is not None:
                    disabled_dates1.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT date FROM disabled_dates")
        rows2 = cur2.fetchall()
        disabled_dates2 = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT date FROM disabled_dates")
            rows2 = cur2.fetchall()
            disabled_dates2 = []

        # Convert valid date objects to strings
            for row2 in rows2:
                date = row2[0]
                if date is not None:
                    disabled_dates2.append(date.strftime("%Y-%m-%d"))

    if request.method == 'POST':
        idnumber = request.form['idnumber']
        position = request.form['position']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        title = request.form['treatment']
        tiime = request.form['time']
        Start_date = request.form['dateappointment']
        cur.execute('SELECT * FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s', (Start_date,tiime,title))
        result = cur.fetchone()
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT COUNT(*) FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s", (Start_date,tiime,title))
        count = cur2.fetchone()[0]
        if count == 10:
            return render_template('student/add-appointment.html',error='Appointment is Already FULL!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)
        else:
            cur.execute("INSERT INTO tbl_appointments (ID_Number,position,firstname,middlename,lastname,email,gender,mobile,address,Title,Start_date_time,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idnumber,position,firstname,middlename,lastname,email,gender,mobile,address,title,Start_date,tiime])
            mysql.connection.commit()
            cur.close()
            return render_template('faculty/add-appointment.html',error2='Appointment is Successful!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)


@app.route('/faculty/add-appointment-execute-class', methods=['post','get'])
def faculty_add_appointment_execute_class():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()

    # Query the database for disabled dates
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT date FROM disabled_dates_dental")
    rows1 = cur1.fetchall()
    disabled_dates1 = []
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()

    # Convert valid date objects to strings
    for row1 in rows1:
        # Query the database for disabled dates
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT date FROM disabled_dates_dental")
        rows1 = cur1.fetchall()
        disabled_dates1 = []

        # Convert valid date objects to strings
        for row1 in rows1:
            date = row1[0]
            if date is not None:
                disabled_dates1.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM disabled_dates")
        rows = cur.fetchall()
        disabled_dates = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur = mysql.connection.cursor()
            cur.execute("SELECT date FROM disabled_dates")
            rows = cur.fetchall()
            disabled_dates = []

        # Convert valid date objects to strings
            for row in rows:
                date = row[0]
                if date is not None:
                    disabled_dates.append(date.strftime("%Y-%m-%d"))





    # Query the database for disabled dates
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT date FROM disabled_dates")
        rows2 = cur2.fetchall()
        disabled_dates2 = []

    # Convert valid date objects to strings
        for row in rows:
        # Query the database for disabled dates
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT date FROM disabled_dates")
            rows2 = cur2.fetchall()
            disabled_dates2 = []

        # Convert valid date objects to strings
            for row2 in rows2:
                date = row2[0]
                if date is not None:
                    disabled_dates2.append(date.strftime("%Y-%m-%d"))
    if request.method == 'POST':
        idnumber = request.form['idnumber']
        position = request.form['position']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        title = request.form['treatment']
        tiime = request.form['time']
        Start_date = request.form['dateappointment']
        cur.execute('SELECT * FROM tbl_appointments WHERE Start_date_time = %s AND time = %s AND Title = %s', (Start_date,tiime,title))
        result = cur.fetchone()
        if result:
                return render_template('faculty/add-appointment.html',error='Appointment is Taken!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)
        else:
            cur.execute("INSERT INTO tbl_appointments (ID_Number,position,firstname,middlename,lastname,email,gender,mobile,address,Title,Start_date_time,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idnumber,position,firstname,middlename,lastname,email,gender,mobile,address,title,Start_date,tiime])
            mysql.connection.commit()
            cur.close()
            return render_template('faculty/add-appointment.html',error2='Appointment is Successful!', admin=admin, disabled_dates=disabled_dates,
                                   disabled_dates1=disabled_dates1, disabled_dates2=disabled_dates2,Notification=Notification)






@app.route('/faculty/calendar' , methods=['POST','GET'])
def faculty_calendar():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments ORDER BY id')
    appointments = appointment.fetchall()
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    admin = cursor.fetchone()
    appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
    Notification = appointment.fetchall()
    return render_template('faculty/calendar.html', appointments=appointments, admin=admin,Notification=Notification)

@app.route('/faculty/compose' , methods=['POST','GET'])
def faculty_compose():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/compose.html', admin=admin,Notification=Notification)

@app.route('/faculty/send_email', methods=['POST'])
def faculty_send_email():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        recipient = request.form['recipient']
        message = request.form['textarea']

        # Create the message
        msg = Message(subject='New message from your school Clinic',
                      recipients=[recipient])  # Replace with your email address
        msg.body = f"You have received a new message from {name}: \n\n{message}"

        try:
            # Send the message
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending your message: {e}', 'error')

    return render_template('faculty/compose.html', admin=admin,Notification=Notification)





@app.route('/faculty/compose-cancel/<int:id>' , methods=['POST','GET'])
def faculty_compose_cancel(id):
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_appointments WHERE id = %s', (id,))
        mail = cursor.fetchone()
        status = 'Appointment Canceled'
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status = %s WHERE id = %s', (status, id))
        mysql.connection.commit()
        status1 = 8
        cursorapprove = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorapprove.execute('UPDATE tbl_appointments SET status1 = %s WHERE id = %s', (status1, id))
        mysql.connection.commit()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()

    return render_template('faculty/compose-cancel.html', admin=admin,mail=mail,Notification=Notification)








@app.route('/faculty/inbox' , methods=['POST','GET'])
def faculty_inbox():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('facultyt/inbox.html', admin=admin,Notification=Notification)

@app.route('/faculty/mail-view' , methods=['POST','GET'])
def faculty_mail_view():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/mail-view.html', admin=admin,Notification=Notification)


@app.route('/faculty/settings' , methods=['POST','GET'])
def faculty_settings():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
        admin = cursor.fetchone()
        appointment = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        appointment.execute('SELECT * FROM tbl_appointments WHERE ID_Number = %s', (session['idnumber'],))
        Notification = appointment.fetchall()
    return render_template('faculty/settings.html', admin=admin,Notification=Notification)


@app.route('/faculty/logout', methods=['POST', 'GET'])
def faculty_logout():
    if not session.get('id'):
        return redirect(url_for('faculty_login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_students WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_students WHERE Userlevel_ID =%s AND id = %s', (3, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_moderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_moderator WHERE status =%s AND id = %s', (2, session['id'],))
        not_approved1 = cursor.fetchone()
        if not_approved1:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_headmoderator WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        cursor.execute('SELECT * FROM tbl_headmoderator WHERE status =%s AND id = %s', (1, session['id'],))
        not_approved = cursor.fetchone()
        if not_approved:
            return render_template('faculty/login.html', error='Your are not a FACULTY Member!!')
    if session.get('id'):
        session['id'] = None
        session['idnumber'] = None
        return redirect(url_for('landingpage'))



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

