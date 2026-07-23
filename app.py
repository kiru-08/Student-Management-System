from flask import Flask, render_template, request, redirect, url_for
from database import cursor, db
from openpyxl import Workbook
from flask import send_file
import os


app = Flask(__name__)

# ===================== LOGIN =====================

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        sql = "SELECT * FROM admin WHERE username=%s AND password=%s"
        values = (username, password)

        cursor.execute(sql, values)
        admin = cursor.fetchone()

        if admin:
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Username or Password")

    return render_template('login.html')


# ===================== DASHBOARD =====================

# ---------------------- DASHBOARD ----------------------

@app.route('/dashboard')
def dashboard():

    # Total Students
    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()['total']

    # Male Students
    cursor.execute("SELECT COUNT(*) AS male FROM students WHERE gender='Male'")
    male_students = cursor.fetchone()['male']

    # Female Students
    cursor.execute("SELECT COUNT(*) AS female FROM students WHERE gender='Female'")
    female_students = cursor.fetchone()['female']

    # Total Departments
    cursor.execute("SELECT COUNT(DISTINCT department) AS departments FROM students")
    total_departments = cursor.fetchone()['departments']

    return render_template(
        'dashboard.html',
        total_students=total_students,
        male_students=male_students,
        female_students=female_students,
        total_departments=total_departments
    )

# ===================== ADD STUDENT PAGE =====================

@app.route('/add_student')
def add_student():
    return render_template('add_student.html')

# ---------------------- EDIT STUDENT PAGE ----------------------

@app.route('/edit_student/<student_id>')
def edit_student(student_id):

    sql = "SELECT * FROM students WHERE student_id=%s"

    cursor.execute(sql, (student_id,))

    student = cursor.fetchone()

    return render_template("edit_student.html", student=student)


# ===================== VIEW STUDENTS =====================

@app.route('/students')
def students():

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    return render_template("students.html", students=students)

# ---------------------- UPDATE STUDENT ----------------------

@app.route('/update_student', methods=['POST'])
def update_student():

    student_id = request.form['student_id']
    roll_no = request.form['roll_no']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    department = request.form['department']
    year = request.form['year']
    mobile = request.form['mobile']

    sql = """
    UPDATE students
    SET
        roll_no=%s,
        first_name=%s,
        last_name=%s,
        department=%s,
        year=%s,
        mobile=%s
    WHERE student_id=%s
    """

    values = (
        roll_no,
        first_name,
        last_name,
        department,
        year,
        mobile,
        student_id
    )

    cursor.execute(sql, values)
    db.commit()

    return redirect(url_for('students'))

# ===================== DELETE STUDENT =====================

@app.route('/delete_student/<student_id>')
def delete_student(student_id):

    sql = "DELETE FROM students WHERE student_id=%s"

    cursor.execute(sql, (student_id,))
    db.commit()

    return redirect(url_for('students'))

# ===================== SAVE STUDENT =====================

@app.route('/save_student', methods=['POST'])
def save_student():

    # Generate Student ID Automatically
    cursor.execute("SELECT MAX(id) AS last_id FROM students")
    result = cursor.fetchone()

    if result["last_id"] is None:
        student_id = "ST001"
    else:
        student_id = f"ST{result['last_id'] + 1:03d}"

    
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    gender = request.form['gender']
    dob = request.form['dob'] or None
    roll_no = request.form['roll_no']
    department = request.form['department']
    year = request.form['year']
    mobile = request.form['mobile']
    email = request.form['email']
    address = request.form['address']
    parent_name = request.form['parent_name']
    parent_mobile = request.form['parent_mobile']
    admission_date = request.form['admission_date'] or None

    sql = """
    INSERT INTO students
    (
        student_id,
        roll_no,
        first_name,
        last_name,
        gender,
        dob,
        department,
        year,
        mobile,
        email,
        address,
        parent_name,
        parent_mobile,
        admission_date
    )
    VALUES
    (
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
    )
    """

    values = (
        student_id,
        roll_no,
        first_name,
        last_name,
        gender,
        dob,
        department,
        year,
        mobile,
        email,
        address,
        parent_name,
        parent_mobile,
        admission_date
    )

    cursor.execute(sql, values)
    db.commit()

    return redirect(url_for('students'))

# ===================== REPORTS =====================
@app.route('/reports')
def reports():

    # Total Students
    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()['total']

    # Male Students
    cursor.execute("SELECT COUNT(*) AS male FROM students WHERE gender='Male'")
    male_students = cursor.fetchone()['male']

    # Female Students
    cursor.execute("SELECT COUNT(*) AS female FROM students WHERE gender='Female'")
    female_students = cursor.fetchone()['female']

    # Department-wise Report
    cursor.execute("""
        SELECT department, COUNT(*) AS total
        FROM students
        GROUP BY department
    """)
    departments = cursor.fetchall()

    # Year-wise Report
    cursor.execute("""
        SELECT year, COUNT(*) AS total
        FROM students
        GROUP BY year
    """)
    years = cursor.fetchall()

    # Data for Chart.js
    department_names = [d['department'] for d in departments]
    department_counts = [d['total'] for d in departments]

    return render_template(
        "reports.html",
        total_students=total_students,
        male_students=male_students,
        female_students=female_students,
        departments=departments,
        years=years,
        department_names=department_names,
        department_counts=department_counts
    )


# ===================== EXPORT TO EXCEL =====================

@app.route('/export_excel')
def export_excel():

    cursor.execute("""
        SELECT
        student_id,
        roll_no,
        first_name,
        last_name,
        gender,
        department,
        year,
        mobile,
        email
        FROM students
    """)

    students = cursor.fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    # Headers
    ws.append([
        "Student ID",
        "Roll No",
        "First Name",
        "Last Name",
        "Gender",
        "Department",
        "Year",
        "Mobile",
        "Email"
    ])

    # Data
    for student in students:

        ws.append([
            student["student_id"],
            student["roll_no"],
            student["first_name"],
            student["last_name"],
            student["gender"],
            student["department"],
            student["year"],
            student["mobile"],
            student["email"]
        ])

    file_path = "students_report.xlsx"
    wb.save(file_path)

    return send_file(file_path, as_attachment=True)
# ===================== RUN APP =====================

if __name__ == '__main__':
    app.run(debug=True)