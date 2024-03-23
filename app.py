from flask import Flask, render_template, request, redirect, session, make_response
import sqlite3
import bcrypt
import pdfkit

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    if request.method == 'POST':
        idno = request.form.get('User ID')
        password = request.form.get('User Password')

        session['user_id'] = idno

        cur.execute('SELECT name, password FROM Student_Details WHERE id = ?', (idno, ))
        result = cur.fetchone()
        if bcrypt.checkpw(password.encode(), result[1]):
            return render_template('home.html', name=result[0].split()[0].capitalize())
        else:
            return "Invalid Login Credentials"
        
    
    else:
        return "Unsuccessful try again"
    
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin.html')

@app.route('/student_admin', methods=['GET', 'POST'])
def student_admin():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    cur.execute('SELECT Student_Details.name, Student_Details.id, Student_Details.contact, Student_Details.dob, Student_Details.email_id, Student_Details.blood_group, Student_Details.condition, Student_Details.address, Student_Details.father_name, Student_Details.father_email, Student_Details.father_contact, Student_Details.mother_name, Student_Details.mother_email, Student_Details.mother_contact, Student_Details.guardian_name, Student_Details.guardian_email, Student_Details.guardian_contact, Branch.name, Course.name, Student_Details.adm_year, Student_Details.category, Student_Details.type, Student_Details.subjects, Student_Details.grades FROM Student_Details JOIN Branch JOIN Course ON Student_Details.branch_id = Branch.id AND Student_Details.course_id = Course.id ORDER BY Student_Details.id')
    rows = cur.fetchall()
    return render_template('student_admin.html', rows=rows)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('add_student.html')

@app.route('/registered', methods=['GET', 'POST'])
def add_registration():

    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    global idno
    if request.method == 'POST':
        name = request.form.get("Student Name")
        contact = request.form.get("Student Contact Number")
        dob = request.form.get('Student Birthday')
        email = request.form.get('Student E-Mail')
        blood_group = request.form.get('Blood Group')
        condition = request.form.get('Student Health Conditions')
        address = request.form.get('Student Address')
        password = request.form.get('Password')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        father_name = request.form.get('Father Name')
        father_contact = request.form.get('Father Contact')
        father_email = request.form.get('Father Email')
        
        mother_name = request.form.get('Mother Name')
        mother_contact = request.form.get('Mother Contact')
        mother_email = request.form.get('Mother Email')

        guardian_name = request.form.get('Guardian Name')
        guardian_contact = request.form.get('Guardian Contact')
        guardian_email = request.form.get('Guardian Email')

        branch = request.form.get('Branch')
        cur.execute('SELECT id FROM Branch WHERE name=?', (branch, ))
        
        result = cur.fetchone()
        branch_id = result[0]
        course = request.form.get('Course')
        cur.execute('SELECT id FROM Course WHERE name = ?',(course, ))
        result = cur.fetchone()
        course_id = result[0]
        idno = request.form.get('Registration Num')
        adm_yr = request.form.get('Admission Year')
        category = request.form.get('Category')      
        type = request.form.get('Type')
        subject = request.form.get('Course Subjects')
        grades = request.form.get('Course Grades')

        cur.execute('INSERT INTO Student_Details (name, id, contact, dob, email_id, blood_group, condition, address, password, father_name, father_email, father_contact, mother_name, mother_email, mother_contact, guardian_name, guardian_email, guardian_contact, branch_id, course_id, adm_year, category, type, subjects, grades) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(name, id, contact, dob, email, blood_group, condition, address, hashed_password, father_name, father_email, father_contact, mother_name, mother_email, mother_contact, guardian_name, guardian_email, guardian_contact, branch_id, course_id, adm_yr, category, type, subject, grades))
        conn.commit()

        return "Registered successfully"    
    
    else:
        return "Sorry unsuccessful try again"

@app.route('/performance', methods=['GET', 'POST'])
def performance():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT Student_Details.name, Branch.name, Student_Details.adm_year, Student_Details.id, Student_Details.subjects, Student_Details.grades FROM Student_Details JOIN Branch ON Branch.id = Student_Details.branch_id WHERE Student_Details.id = ?', (session['user_id'], ))
    
    result = cur.fetchone()
    if result is not None:
        return render_template('per_sheet.html', name=result[0].capitalize(), branch=result[1], year=result[2], id=session['user_id'], subjects=result[4], grades=result[5])
    else:
        return "Your performance sheet doesnt exist"

@app.route('/print', methods=['GET', 'POST'])
def generate_pdf():
    html = render_template('per_sheet.html')
    
    # Convert HTML to PDF
    pdf = pdfkit.from_string(html, False)

    # Create response with PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=marksheet.pdf'

    return response

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)