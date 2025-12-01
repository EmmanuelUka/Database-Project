from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
import mysql.connector


app = Flask(__name__)
app.secret_key = "Nittny_Lions"
bcrypt = Bcrypt(app)

db_config = {
    'host': 'localhost',
    'user': 'root',         
    'password': '',        
    'database': 'euka'
}


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = None
        cursor = None
        
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

        except mysql.connector.Error as err:
            print("Database Error:", err)
            flash("Database connection failed.")
            return redirect(url_for('login'))

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        # Authentication logic
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!')

            # Routing based on role
            return redirect(url_for(f"{user['role']}_dashboard"))
            
        else:
            flash('Invalid username or password')

    return render_template('login.html')



@app.route('/admin')
def admin_dashboard():
    if not session.get('user_id') or session.get('role') != 'admin':
        flash('Unauthorized access. Please log in as admin.')
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', username=session['username'])


@app.route('/instructor')
def instructor_dashboard():
    if not session.get('user_id') or session.get('role') != 'instructor':
        flash('Unauthorized access. Please log in as instructor.')
        return redirect(url_for('login'))
    return render_template('instructor_dashboard.html', username=session['username'])


@app.route('/student')
def student_dashboard():
    if not session.get('user_id') or session.get('role') != 'student':
        flash('Unauthorized access. Please log in as student.')
        return redirect(url_for('login'))       
    return render_template('student_dashboard.html', username=session['username'])


@app.route("/student/register")
def show_sections():
    if not session.get('user_id') or session.get('role') != 'student':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch sections student hasn't registered for yet
        cursor.execute("""
            SELECT s.section_number, s.course_id, s.semester, s.year, s.days, s.time, c.c_name
            FROM section s
            JOIN course c ON s.course_id = c.course_id
            WHERE s.section_number NOT IN (
                SELECT section_number FROM takes WHERE student_id = %s
            )
        """, (session['user_id'],))
        sections = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template("register.html", sections=sections)



@app.route("/student/register/submit", methods=["POST"])
def register_submit():
    if not session.get('user_id') or session.get('role') != 'student':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    student_id = session['user_id']
    section_number = request.form['section_id']

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Check if already registered
        cursor.execute("""
            SELECT * FROM takes
            WHERE student_id = %s AND section_number = %s
        """, (student_id, section_number))
        if cursor.fetchone():
            flash("Already registered in this class.")
            return redirect(url_for('show_sections'))

        # Insert into takes with grade = NULL
        cursor.execute("""
            INSERT INTO takes (student_id, section_number, letter, course_ID)
            SELECT %s, section_number, NULL, course_id
            FROM section
            WHERE section_number = %s
        """, (student_id, section_number))
        connection.commit()
        flash("Successfully registered!")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('student_dashboard'))

from datetime import datetime

def get_status(row):
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Convert month to semester
    if current_month in [1, 2, 3, 4, 5]:
        current_semester = "Spring"
    elif current_month in [6, 7, 8]:
        current_semester = "Summer"
    else:
        current_semester = "Fall"

    year = row["year"]
    semester = row["semester"]

    # Compare year first
    if year < current_year:
        return "Completed"
    if year > current_year:
        return "Upcoming"

    # Same year → compare semester order
    order = {"Spring": 1, "Summer": 2, "Fall": 3}
    if order[semester] < order[current_semester]:
        return "Completed"
    if order[semester] > order[current_semester]:
        return "Upcoming"

    return "In Progress"


@app.route("/student/register/class_list", methods=["GET", "POST"])
def class_list():
    if not session.get('user_id') or session.get('role') != 'student':
        flash("Unauthorized access.")
        return redirect(url_for('login'))
    
    student_id = session['user_id']
    selected_semester = None

    if request.method == "POST":
        selected_semester = request.form.get("semester")

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT t.section_number, t.course_id, 
                   s.semester, s.year, s.days, s.time
            FROM takes t
            JOIN section s ON t.section_number = s.section_number
            WHERE t.student_id = %s
        """
        params = [student_id]

        # Add semester filter only if selected
        if selected_semester and selected_semester != "all":
            query += " AND s.semester = %s"
            params.append(selected_semester)

        cursor.execute(query, params)
        registered_sections = cursor.fetchall()
        
        for row in registered_sections:
            row["status"] = get_status(row)

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'class_list.html',
        registered_sections=registered_sections,
        selected_semester=selected_semester
    )


@app.route("/student/register/drop_class", methods=["POST"])
def drop_class():
    if not session.get('user_id') or session.get('role') != 'student':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    student_id = session['user_id']
    section_number = request.form['section_id']  

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM takes 
            WHERE section_number = %s AND student_id = %s
        """, (section_number, student_id))

        connection.commit()
        flash("Class dropped successfully.")

    except Exception as e:
        flash(f"Error dropping class: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('class_list'))   


@app.route('/student/register/final_grade', methods=['GET'])
def final_grade():
    if not session.get('user_id') or session.get('role') != 'student':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    student_id = session['user_id']

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT t.section_number, t.course_id, t.letter, s.semester, s.year
            FROM takes t
            JOIN section s ON t.section_number = s.section_number
            WHERE t.student_id = %s
        """, (student_id,))

        grades = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template('final_grades.html', grades=grades)


@app.route('/student/profile')
def student_profile():
    if not session.get('user_id') or session.get('role') != 'student':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    student_id = session['user_id']
    student_info = {}

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""                                                                          
            SELECT s.student_id, s.s_name, s.tot_credits, s.gpa, s.email, d.d_name,
                s.address_houseNumber, s.address_street, s.address_city, s.address_state, s.address_zip,
                p.professor_id, p.p_name
            FROM student s
            LEFT JOIN department d ON s.dept_id = d.department_id
            LEFT JOIN professor p ON s.advisor = p.professor_id
            WHERE s.student_id = %s

        """, (student_id,))

        student_info = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    return render_template('student_profile.html', student=student_info)


@app.route('/student/profile/edit', methods=['GET'])
def edit_profile():
    if not session.get('user_id') or session.get('role') != 'student':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    student_id = session['user_id']

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT email, address_houseNumber, address_street,
               address_city, address_state, address_zip
        FROM student
        WHERE student_id = %s
    """, (student_id,))
    
    student_info = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('student_profile_edit.html', student=student_info)


@app.route('/student/profile/update', methods=['POST'])
def update_profile():
    if not session.get('user_id') or session.get('role') != 'student':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    student_id = session['user_id']

    email = request.form['email']
    house = request.form['house']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    zip_code = request.form['zip']

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE student
        SET email=%s, address_houseNumber=%s, address_street=%s,
            address_city=%s, address_state=%s, address_zip=%s
        WHERE student_id=%s
    """, (email, house, street, city, state, zip_code, student_id))

    connection.commit()

    cursor.close()
    connection.close()

    flash("Profile updated successfully.")
    return redirect("/student/profile")


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))


@app.route('/admin/departments')
def manage_departments():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT department_ID, d_name, b_name, budget FROM department")
        departments = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template('manage_departments.html', departments=departments)

@app.route('/admin/departments/add', methods=['GET', 'POST'])
def add_department():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        department_ID = request.form['department_ID']
        d_name = request.form['d_name']
        b_name = request.form['b_name']
        budget = request.form['budget']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO department (department_ID, d_name, b_name, budget) VALUES (%s, %s, %s, %s)",
                (department_ID, d_name, b_name, budget)
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()

        flash("Department added successfully!")
        return redirect(url_for('manage_departments'))

    return render_template('add_department.html')

@app.route('/admin/departments/delete/<int:department_id>')
def delete_department(department_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM department WHERE department_ID = %s", (department_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

    flash("Department deleted successfully!")
    return redirect(url_for('manage_departments'))


@app.route('/admin/departments/search', methods=['GET', 'POST'])
def search_department_name():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('search_department.html')

    term = request.form.get('term', '').strip()
    if not term:
        flash("Please enter a search term.")
        return redirect(url_for('search_department_name'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        pattern = f"%{term}%"

        cursor.execute("""
            SELECT department_ID, d_name, b_name, budget
            FROM department
            WHERE d_name LIKE %s
            ORDER BY d_name
        """, (pattern,))

        results = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'manage_departments.html',
        departments=results,
        search_term=term
    )


@app.route('/admin/departments/update/<int:department_id>', methods=['GET', 'POST'])
def update_department(department_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Get current values
        cursor.execute("SELECT * FROM department WHERE department_ID = %s", (department_id,))
        department = cursor.fetchone()

        if not department:
            flash("Department not found.")
            return redirect(url_for('manage_departments'))

        if request.method == 'POST':
            # Only update fields that are not blank
            new_d_name = request.form.get('d_name') or department['d_name']
            new_b_name = request.form.get('b_name') or department['b_name']
            new_budget = request.form.get('budget') or department['budget']

            cursor.execute("""
                UPDATE department
                SET d_name = %s, b_name = %s, budget = %s
                WHERE department_ID = %s
            """, (new_d_name, new_b_name, new_budget, department_id))
            connection.commit()
            flash("Department updated successfully!")
            return redirect(url_for('manage_departments'))

    finally:
        cursor.close()
        connection.close()

    return render_template('update_department.html', department=department)


@app.route('/admin/classrooms')
def manage_classrooms():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT b_name, room_number, capacity FROM classroom")
        classrooms = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template('manage_classrooms.html', classrooms=classrooms)


@app.route('/admin/classrooms/add', methods=['GET', 'POST'])
def add_classroom():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        b_name = request.form['b_name']
        room_number = request.form['room_number']
        capacity = request.form['capacity']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO classroom (b_name, room_number, capacity) VALUES (%s, %s, %s)",
                (b_name, room_number, capacity)
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()

        flash("Classroom added successfully!")
        return redirect(url_for('manage_classrooms'))

    return render_template('add_classroom.html')


@app.route('/admin/classrooms/delete/<b_name>/<room_number>')
def delete_classroom(b_name, room_number):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM classroom WHERE b_name = %s AND room_number = %s",
            (b_name, room_number)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

    flash("Classroom deleted successfully!")
    return redirect(url_for('manage_classrooms'))


@app.route('/admin/classrooms/update/<b_name>/<room_number>', methods=['GET', 'POST'])
def update_classroom(b_name, room_number):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch existing classroom info
        cursor.execute(
            "SELECT * FROM classroom WHERE b_name = %s AND room_number = %s",
            (b_name, room_number)
        )
        classroom = cursor.fetchone()

        if not classroom:
            flash("Classroom not found.")
            return redirect(url_for('manage_classrooms'))

        if request.method == 'POST':
            new_capacity = request.form.get('capacity', '').strip()

            if new_capacity != "":
                cursor.execute(
                    "UPDATE classroom SET capacity = %s WHERE b_name = %s AND room_number = %s",
                    (new_capacity, b_name, room_number)
                )
                connection.commit()
                flash("Classroom updated successfully!")
                return redirect(url_for('manage_classrooms'))

    finally:
        cursor.close()
        connection.close()

    return render_template('update_classroom.html', classroom=classroom)


@app.route('/admin/classrooms/search', methods=['GET', 'POST'])
def search_classrooms():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('search_classroom.html')

    term = request.form.get('term', '').strip()

    if not term:
        flash("Please enter a search term.")
        return redirect(url_for('search_classrooms'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)   # ← FIXED!

        pattern = f"%{term}%"
        cursor.execute("""
            SELECT b_name, room_number, capacity
            FROM classroom
            WHERE b_name LIKE %s
            ORDER BY b_name, room_number
        """, (pattern,))
        results = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'manage_classrooms.html',
        classrooms=results,
        search_term=term
    )


@app.route('/admin/students')
def manage_students():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()

        cursor.execute("""
            SELECT student_id, s_name, dept_id, tot_credits, gpa
            FROM student
            ORDER BY student_id
        """)
        students = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template('manage_students.html', students=students)


@app.route('/admin/students/search', methods=['GET', 'POST'])
def search_students():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('search_student.html')

    term = request.form.get('term', '').strip()
    if not term:
        flash("Please enter a search term.")
        return redirect(url_for('search_students'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()

        pattern = f"%{term}%"
        cursor.execute("""
            SELECT student_id, s_name, dept_id, tot_credits, gpa
            FROM student
            WHERE s_name LIKE %s OR student_id LIKE %s
            ORDER BY s_name
        """, (pattern, pattern))
        results = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'manage_students.html',
        students=results,
        search_term=term
    )


@app.route('/admin/students/add', methods=['GET', 'POST'])
def add_student():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = (
            request.form['student_id'],    
            request.form['s_name'],
            request.form['dept_id'],
            request.form['tot_credits'],
            request.form['gpa'],
            request.form['email'],
            request.form['address_houseNumber'],
            request.form['address_street'],
            request.form['address_city'],
            request.form['address_state'],
            request.form['address_zip']
        )

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO student (
                    student_id, s_name, dept_id, tot_credits, gpa, email,
                    address_houseNumber, address_street, address_city,
                    address_state, address_zip
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, data)
            connection.commit()
            flash("Student added successfully!")
            return redirect(url_for('manage_students'))
        finally:
            cursor.close()
            connection.close()

    return render_template('add_student.html')


@app.route('/admin/students/update/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch student
        cursor.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        if not student:
            flash("Student not found.")
            return redirect(url_for('manage_students'))

        if request.method == 'POST':
            data = (
                request.form['s_name'],
                request.form['dept_id'],
                request.form['tot_credits'],
                request.form['gpa'],
                request.form['email'],
                request.form['address_houseNumber'],
                request.form['address_street'],
                request.form['address_city'],
                request.form['address_state'],
                request.form['address_zip'],
                student_id
            )

            cursor.execute("""
                UPDATE student
                SET s_name=%s, dept_id=%s, tot_credits=%s, gpa=%s,
                    email=%s, address_houseNumber=%s, address_street=%s,
                    address_city=%s, address_state=%s, address_zip=%s
                WHERE student_id=%s
            """, data)
            connection.commit()
            flash("Student updated successfully!")
            return redirect(url_for('manage_students'))

    finally:
        cursor.close()
        connection.close()

    return render_template('update_student.html', student=student)


@app.route('/admin/students/delete/<student_id>')
def delete_student(student_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
        connection.commit()

        flash("Student deleted successfully!")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('manage_students'))

@app.route('/admin/professors')
def manage_professors():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    search = request.args.get('search')

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    if search:
        query = "SELECT * FROM professor WHERE p_name LIKE %s"
        cursor.execute(query, (f"%{search}%",))
    else:
        cursor.execute("SELECT * FROM professor")

    professors = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('manage_professors.html',
        professors=professors,
        search_term=search)


@app.route('/admin/professors/add', methods=['GET', 'POST'])
def add_professor():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        professor_id = request.form['professor_id']
        p_name = request.form['p_name']
        dept_id = request.form['dept_id']
        salary = request.form['salary']
        email = request.form['email']
        hn = request.form['address_houseNumber']
        street = request.form['address_street']
        city = request.form['address_city']
        state = request.form['address_state']
        zipc = request.form['address_zip']

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = """
            INSERT INTO professor 
            (professor_id, p_name, dept_id, salary, email,
             address_houseNumber, address_street, address_city, address_state, address_zip)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (professor_id, p_name, dept_id, salary, email,
                               hn, street, city, state, zipc))
        connection.commit()

        cursor.close()
        connection.close()

        flash("Professor added successfully!")
        return redirect(url_for('manage_professors'))

    return render_template('add_professor.html')


@app.route('/admin/professors/update/<professor_id>', methods=['GET', 'POST'])
def update_professor(professor_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM professor WHERE professor_id = %s", (professor_id,))
    professor = cursor.fetchone()

    if request.method == 'POST':
        p_name = request.form['p_name']
        dept_id = request.form['dept_id']
        salary = request.form['salary']
        email = request.form['email']
        hn = request.form['address_houseNumber']
        street = request.form['address_street']
        city = request.form['address_city']
        state = request.form['address_state']
        zipc = request.form['address_zip']

        update_query = """
            UPDATE professor SET
                p_name=%s, dept_id=%s, salary=%s, email=%s,
                address_houseNumber=%s, address_street=%s, address_city=%s,
                address_state=%s, address_zip=%s
            WHERE professor_id=%s
        """

        cursor.execute(update_query, (p_name, dept_id, salary, email,
                                      hn, street, city, state, zipc, professor_id))
        connection.commit()

        cursor.close()
        connection.close()

        flash("Professor updated successfully!")
        return redirect(url_for('manage_professors'))

    cursor.close()
    connection.close()

    return render_template('update_professor.html', professor=professor)


@app.route('/admin/professors/delete/<professor_id>')
def delete_professor(professor_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("DELETE FROM professor WHERE professor_id = %s", (professor_id,))
        connection.commit()

        flash("Professor deleted successfully!")

    except mysql.connector.IntegrityError:
        flash("Cannot delete professor: They are referenced elsewhere.")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('manage_professors'))


@app.route('/admin/professors/search', methods=['GET', 'POST'])
def search_professors():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('search_professor.html')

    term = request.form.get('term', '').strip()
    if not term:
        flash("Please enter a search term.")
        return redirect(url_for('search_professors'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        pattern = f"%{term}%"
        cursor.execute("""
            SELECT professor_id, p_name, dept_id, salary
            FROM professor
            WHERE p_name LIKE %s
            ORDER BY p_name
        """, (pattern,))
        results = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'manage_professors.html',
        professors=results,
        search_term=term
    )


@app.route('/admin/courses')
def manage_courses():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM course ORDER BY course_id")
    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('manage_courses.html', courses=courses)


@app.route('/admin/courses/search', methods=['GET', 'POST'])
def search_courses():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('search_course.html')

    dept = request.form.get('term', '').strip()

    if dept == "":
        flash("Please enter a department ID.")
        return redirect(url_for('search_courses'))

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM course
        WHERE department_id LIKE %s
        ORDER BY course_id
    """, (f"%{dept}%",))

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'manage_courses.html',
        courses=results,
        search_term=dept
    )


@app.route('/admin/courses/add', methods=['GET', 'POST'])
def add_course():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        course_id = request.form['course_id']
        c_name = request.form['c_name']
        credits = request.form['credits']
        department_id = request.form['department_id']

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Validate department_id
        cursor.execute(
            "SELECT department_id FROM department WHERE department_id = %s",
            (department_id,)
        )
        exists = cursor.fetchone()
        if not exists:
            flash("Invalid Department ID.")
            cursor.close()
            connection.close()
            return redirect(url_for('add_course'))

        cursor.execute("""
            INSERT INTO course (course_id, c_name, credits, department_id)
            VALUES (%s,%s,%s,%s)
        """, (course_id, c_name, credits, department_id))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Course added successfully!")
        return redirect(url_for('manage_courses'))

    return render_template('add_course.html')


@app.route('/admin/courses/update/<course_id>', methods=['GET', 'POST'])
def update_course(course_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM course WHERE course_id = %s", (course_id,))
    course = cursor.fetchone()

    if not course:
        cursor.close()
        connection.close()
        flash("Course not found.")
        return redirect(url_for('manage_courses'))

    if request.method == 'POST':
        c_name = request.form['c_name']
        credits = request.form['credits']
        department_id = request.form['department_id']

        # validate department_id
        cursor.execute(
            "SELECT department_id FROM department WHERE department_id = %s",
            (department_id,)
        )
        exists = cursor.fetchone()

        if not exists:
            cursor.close()
            connection.close()
            flash("Invalid Department ID.")
            return redirect(url_for('update_course', course_id=course_id))

        cursor.execute("""
            UPDATE course
            SET c_name=%s, credits=%s, department_id=%s
            WHERE course_id=%s
        """, (c_name, credits, department_id, course_id))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Course updated successfully!")
        return redirect(url_for('manage_courses'))

    cursor.close()
    connection.close()

    return render_template('update_course.html', course=course)


@app.route('/admin/courses/delete/<course_id>')
def delete_course(course_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("DELETE FROM course WHERE course_id = %s", (course_id,))
        connection.commit()

        flash("Course deleted successfully!")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('manage_courses'))


@app.route('/admin/sections')
def manage_sections():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM section ORDER BY section_number")
        sections = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template('manage_sections.html', sections=sections)


@app.route('/admin/sections/search', methods=['GET', 'POST'])
def search_sections():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('search_section.html')

    course = request.form.get('course_id', '').strip()
    semester = request.form.get('semester', '').strip()

    if not course and not semester:
        flash("Please enter a course ID or select a semester.")
        return redirect(url_for('search_sections'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        if course and semester:
            cursor.execute("""
                SELECT * FROM section
                WHERE course_id LIKE %s AND semester = %s
                ORDER BY section_number
            """, (f"%{course}%", semester))
        elif course:
            cursor.execute("""
                SELECT * FROM section
                WHERE course_id LIKE %s
                ORDER BY section_number
            """, (f"%{course}%",))
        else:
            cursor.execute("""
                SELECT * FROM section
                WHERE semester = %s
                ORDER BY section_number
            """, (semester,))

        results = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template('manage_sections.html', sections=results, search_term=f"{course} {semester}".strip())


@app.route('/admin/sections/add', methods=['GET', 'POST'])
def add_section():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        section_number = request.form['section_number'].strip()
        course_id = request.form['course_id'].strip()
        semester = request.form['semester'].strip()
        year = request.form['year'].strip()
        b_name = request.form['b_name'].strip()
        room_number = request.form['room_number'].strip()
        capacity = request.form.get('capacity') or None

        valid_semesters = ['Fall', 'Spring', 'Summer', 'Winter']
        if semester not in valid_semesters:
            flash("Invalid semester. Choose Fall, Spring, Summer, or Winter.")
            return redirect(url_for('add_section'))

        if not year.isdigit() or not (1701 < int(year) < 2100):
            flash("Invalid year. Must be between 1702 and 2099.")
            return redirect(url_for('add_section'))

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            cursor.execute("SELECT course_id FROM course WHERE course_id = %s", (course_id,))
            if not cursor.fetchone():
                flash("Invalid course_id.")
                return redirect(url_for('add_section'))

            cursor.execute("SELECT * FROM classroom WHERE b_name = %s AND room_number = %s", (b_name, room_number))
            if not cursor.fetchone():
                flash("Invalid classroom (building + room number).")
                return redirect(url_for('add_section'))

            cursor.execute("SELECT section_number FROM section WHERE section_number = %s", (section_number,))
            if cursor.fetchone():
                flash("Section number already exists. Please choose a unique section number.")
                return redirect(url_for('add_section'))

            cursor.execute("""
                INSERT INTO section
                    (section_number, course_id, semester, year, b_name, room_number, capacity)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (section_number, course_id, semester, year, b_name, room_number, capacity))

            connection.commit()
            flash("Section added successfully!")
            return redirect(url_for('manage_sections'))

        except mysql.connector.Error as err:
            flash(str(err))
            return redirect(url_for('add_section'))

        finally:
            cursor.close()
            connection.close()

    return render_template('add_section.html')



@app.route('/admin/sections/update/<course_id>/<section_number>', methods=['GET', 'POST'])
def update_section(course_id, section_number):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM section
            WHERE course_id = %s AND section_number = %s
        """, (course_id, section_number))
        section = cursor.fetchone()

        if not section:
            flash("Section not found.")
            return redirect(url_for('manage_sections'))

        if request.method == 'POST':
            new_course_id = request.form['course_id'].strip()
            professor_id = request.form['professor_id'].strip()
            semester = request.form['semester'].strip()
            b_name = request.form['b_name'].strip()
            room_number = request.form['room_number'].strip()
            capacity = request.form.get('capacity') or None

            valid_semesters = ['Fall', 'Spring', 'Summer', 'Winter']
            if semester not in valid_semesters:
                flash("Invalid semester.")
                return redirect(url_for('update_section', course_id=course_id, section_number=section_number))

            cursor.execute("SELECT course_id FROM course WHERE course_id = %s", (new_course_id,))
            if not cursor.fetchone():
                flash("Invalid course_id.")
                return redirect(url_for('update_section', course_id=course_id, section_number=section_number))

            cursor.execute("SELECT professor_id FROM professor WHERE professor_id = %s", (professor_id,))
            if not cursor.fetchone():
                flash("Invalid professor_id.")
                return redirect(url_for('update_section', course_id=course_id, section_number=section_number))

            cursor.execute("""
                SELECT *
                FROM classroom
                WHERE b_name = %s AND room_number = %s
            """, (b_name, room_number))
            if not cursor.fetchone():
                flash("Invalid classroom.")
                return redirect(url_for('update_section', course_id=course_id, section_number=section_number))

            cursor.execute("""
                UPDATE section
                SET course_id=%s, professor_id=%s, semester=%s, b_name=%s, room_number=%s, capacity=%s
                WHERE course_id=%s AND section_number=%s
            """, (new_course_id, professor_id, semester, b_name, room_number, capacity, course_id, section_number))
            connection.commit()

            flash("Section updated successfully!")
            return redirect(url_for('manage_sections'))

    finally:
        cursor.close()
        connection.close()

    return render_template('update_section.html', section=section)


@app.route('/admin/sections/delete/<course_id>/<section_number>')
def delete_section(course_id, section_number):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM section
            WHERE course_id = %s AND section_number = %s
        """, (course_id, section_number))
        connection.commit()
        flash("Section deleted successfully!")
    except mysql.connector.IntegrityError:
        flash("Cannot delete section: referenced elsewhere.")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('manage_sections'))


@app.route('/admin/profile/update', methods=['GET', 'POST'])
def admin_profile_update():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT user_id, username, password FROM users WHERE user_id = %s", (session['user_id'],))
        user = cursor.fetchone()

        if request.method == 'POST':
            print("POST RECEIVED")
            old_password = request.form['old_password']
            new_username = request.form['username'].strip()
            new_password = request.form['password'].strip()

            if not new_username:
                flash("Username cannot be empty.")
                return redirect(url_for('admin_profile_update'))

            if not bcrypt.check_password_hash(user['password'], old_password):
                flash("Old password is incorrect.")
                return redirect(url_for('admin_profile_update'))

            if not new_password:
                flash("New password cannot be empty.")
                return redirect(url_for('admin_profile_update'))

            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

            cursor.execute("""
                UPDATE users
                SET username=%s, password=%s
                WHERE user_id=%s
            """, (new_username, hashed_password, session['user_id']))

            connection.commit()

            flash("Profile updated successfully!")
            return redirect(url_for('admin_dashboard'))

    finally:
        cursor.close()
        connection.close()

    return render_template('admin_modify_info.html', user=user)


@app.route('/admin/assignments')
def manage_assignments():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    dept = request.args.get('dept', '').strip()

    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor(dictionary=True)

        if dept:
            cur.execute("""
                SELECT s.section_number, s.course_id, s.semester, s.year, s.b_name,
                       s.room_number, s.capacity, c.department_id, c.c_name
                FROM section s
                JOIN course c ON s.course_id = c.course_id
                WHERE s.professor_id IS NULL AND c.department_id = %s
                ORDER BY s.course_id, s.section_number
            """, (dept,))
        else:
            cur.execute("""
                SELECT s.section_number, s.course_id, s.semester, s.year, s.b_name,
                       s.room_number, s.capacity, c.department_id, c.c_name
                FROM section s
                LEFT JOIN course c ON s.course_id = c.course_id
                WHERE s.professor_id IS NULL
                ORDER BY s.course_id, s.section_number
            """)
        sections = cur.fetchall()

        cur.execute("SELECT department_id, d_name FROM department ORDER BY d_name")
        departments = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    return render_template(
        'manage_assignments.html',
        sections=sections,
        departments=departments,
        selected_dept=dept
    )


@app.route('/admin/assignments/assign/<course_id>/<section_number>', methods=['GET', 'POST'])
def assign_section(course_id, section_number):
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT s.*, c.department_id, c.c_name
            FROM section s
            LEFT JOIN course c ON s.course_id = c.course_id
            WHERE s.course_id = %s AND s.section_number = %s
        """, (course_id, section_number))
        section = cur.fetchone()

        if not section:
            flash("Section not found.")
            return redirect(url_for('manage_assignments'))

        dept_id = section.get('department_id')

        professors = []
        if dept_id:
            cur.execute("""
                SELECT professor_id, p_name
                FROM professor
                WHERE dept_id = %s
                ORDER BY p_name
            """, (dept_id,))
            professors = cur.fetchall()

        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'remove':

                cur.execute("""
                    UPDATE section
                    SET professor_id = NULL
                    WHERE course_id = %s AND section_number = %s
                """, (course_id, section_number))
                cur.execute("""
                    DELETE FROM teaches
                    WHERE course_ID = %s AND section_number = %s
                """, (course_id, section_number))
                conn.commit()
                flash("Professor unassigned from section.")
                return redirect(url_for('manage_assignments'))

            prof_id = request.form.get('professor_id', '').strip()
            if not prof_id:
                flash("Please choose a professor.")
                return redirect(url_for('assign_section', course_id=course_id, section_number=section_number))

            cur.execute("SELECT dept_id FROM professor WHERE professor_id = %s", (prof_id,))
            prof_row = cur.fetchone()
            if not prof_row:
                flash("Selected professor does not exist.")
                return redirect(url_for('assign_section', course_id=course_id, section_number=section_number))

            if dept_id and prof_row['dept_id'] != dept_id:
                flash("Selected professor is not in the same department as the course.")
                return redirect(url_for('assign_section', course_id=course_id, section_number=section_number))

            cur.execute("""
                UPDATE section
                SET professor_id = %s
                WHERE course_id = %s AND section_number = %s
            """, (prof_id, course_id, section_number))

            cur.execute("""
                DELETE FROM teaches
                WHERE course_ID = %s AND section_number = %s
            """, (course_id, section_number))

            cur.execute("""
                INSERT INTO teaches (professor_id, section_number, course_ID)
                VALUES (%s, %s, %s)
            """, (prof_id, section_number, course_id))

            conn.commit()
            flash("Professor assigned/updated successfully.")
            return redirect(url_for('manage_assignments'))

    finally:
        cur.close()
        conn.close()

    return render_template('assign_section.html', section=section, professors=professors)

@app.route('/admin/assignments/assigned')
def assigned_sections():
    if session.get('role') != 'admin':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT s.section_number, s.course_id, s.semester, s.year, s.b_name,
                   s.room_number, s.capacity, s.professor_id,
                   p.p_name AS prof_name, c.c_name, c.department_id
            FROM section s
            LEFT JOIN professor p ON s.professor_id = p.professor_id
            LEFT JOIN course c ON s.course_id = c.course_id
            WHERE s.professor_id IS NOT NULL
            ORDER BY s.course_id, s.section_number
        """)
        rows = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    return render_template('assigned_sections.html', sections=rows)


@app.route('/instructor/avg_grades')
def avg_grades():
    if session.get('role') != 'instructor':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                d.department_id,
                d.d_name,
                AVG(
                    CASE t.letter
                        WHEN 'A' THEN 4
                        WHEN 'B' THEN 3
                        WHEN 'C' THEN 2
                        WHEN 'D' THEN 1
                        WHEN 'F' THEN 0
                    END
                ) AS avg_grade
            FROM department d
            JOIN student s ON s.dept_id = d.department_id
            JOIN takes t ON t.student_id = s.student_id
            GROUP BY d.department_id, d.d_name
            ORDER BY d.d_name
        """)
        rows = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template("avg_grades.html", rows=rows)


@app.route('/instructor/class_avg', methods=['GET', 'POST'])
def class_avg():

    if session.get('role') not in ['admin', 'instructor']:
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT course_id, c_name FROM course ORDER BY c_name")
    courses = cursor.fetchall()

    result = None
    selected = None

    if request.method == "POST":
        course_id = request.form["course_id"]
        start_sem = request.form["start_sem"]
        start_year = request.form["start_year"]
        end_sem = request.form["end_sem"]
        end_year = request.form["end_year"]

        selected = {
            "course_id": course_id,
            "start_sem": start_sem,
            "start_year": start_year,
            "end_sem": end_sem,
            "end_year": end_year
        }

        query = """
        SELECT 
            AVG(
                CASE 
                    WHEN t.letter = 'A' THEN 4
                    WHEN t.letter = 'B' THEN 3
                    WHEN t.letter = 'C' THEN 2
                    WHEN t.letter = 'D' THEN 1
                    WHEN t.letter = 'F' THEN 0
                END
            ) AS avg_grade
        FROM takes t
        JOIN section s ON t.section_number = s.section_number
        WHERE s.course_id = %s
          AND (
                (s.year > %s AND s.year < %s)
                OR (s.year = %s AND 
                    CASE s.semester 
                        WHEN 'Spring' THEN 1
                        WHEN 'Summer' THEN 2
                        WHEN 'Fall' THEN 3
                        WHEN 'Winter' THEN 4
                    END
                    >= 
                    CASE %s 
                        WHEN 'Spring' THEN 1
                        WHEN 'Summer' THEN 2
                        WHEN 'Fall' THEN 3
                        WHEN 'Winter' THEN 4
                    END
                )
                OR (s.year = %s AND 
                    CASE s.semester 
                        WHEN 'Spring' THEN 1
                        WHEN 'Summer' THEN 2
                        WHEN 'Fall' THEN 3
                        WHEN 'Winter' THEN 4
                    END
                    <= 
                    CASE %s 
                        WHEN 'Spring' THEN 1
                        WHEN 'Summer' THEN 2
                        WHEN 'Fall' THEN 3
                        WHEN 'Winter' THEN 4
                    END
                )
              )
        """

        cursor.execute(query, (
            course_id,
            start_year, end_year,
            start_year, start_sem,
            end_year, end_sem
        ))

        row = cursor.fetchone()
        result = row["avg_grade"]

    cursor.close()
    connection.close()

    return render_template(
        "class_avg.html",
        courses=courses,
        result=result,
        selected=selected
    )


@app.route('/instructor/class_comparison', methods=['GET', 'POST'])
def class_comparison():

    if session.get('role') not in ['admin', 'instructor']:
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    best = None
    worst = None
    classes = []
    selected = None

    if request.method == "POST":
        sem = request.form["semester"]
        year = request.form["year"]
        selected = {"semester": sem, "year": year}

        grade_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}

        query = """
            SELECT c.course_id, c.c_name, t.letter
            FROM course c
            JOIN section s ON c.course_id = s.course_id
            JOIN takes t ON t.section_number = s.section_number
            WHERE s.semester = %s AND s.year = %s
        """

        cursor.execute(query, (sem, year))
        rows = cursor.fetchall()

        grade_data = {}

        for r in rows:
            val = grade_map.get(r['letter'])
            if val is None:
                continue

            cid = r['course_id']
            if cid not in grade_data:
                grade_data[cid] = {
                    "name": r['c_name'],
                    "grades": []
                }

            grade_data[cid]["grades"].append(val)

        for course_id, info in grade_data.items():
            avg = sum(info["grades"]) / len(info["grades"])
            classes.append({
                "course_id": course_id,
                "name": info["name"],
                "avg": avg
            })

        if classes:
            best = max(classes, key=lambda x: x['avg'])
            worst = min(classes, key=lambda x: x['avg'])

    cursor.close()
    connection.close()

    return render_template(
        "class_comparison.html",
        best=best,
        worst=worst,
        selected=selected
    )


@app.route('/instructor/student_counts')
def student_counts():
    if session.get('role') not in ['admin', 'instructor']:
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.department_id, d.d_name,
               COUNT(s.student_id) AS current_students
        FROM department d
        LEFT JOIN student s ON s.dept_id = d.department_id
        GROUP BY d.department_id, d.d_name
        ORDER BY d.d_name
    """)
    current_rows = cursor.fetchall()

    cursor.execute("""
        SELECT d.department_id, d.d_name,
               COUNT(DISTINCT t.student_id) AS past_students
        FROM department d
        LEFT JOIN takes t ON TRUE
        LEFT JOIN student s ON s.student_id = t.student_id
        WHERE s.student_id IS NULL
        GROUP BY d.department_id, d.d_name
        ORDER BY d.d_name
    """)
    past_rows = cursor.fetchall()

    cursor.close()
    connection.close()

    result = []
    past_map = {row['department_id']: row['past_students'] for row in past_rows}

    for row in current_rows:
        dept_id = row['department_id']
        current = row['current_students']
        past = past_map.get(dept_id, 0)
        total = current + past

        result.append({
            "department_id": dept_id,
            "d_name": row['d_name'],
            "current": current,
            "past": past,
            "total": total
        })

    return render_template("student_counts.html", rows=result)


# -------------------------------
# Instructor: view semesters
# -------------------------------
@app.route('/instructor/sections')
def instructor_sections():
    if 'user_id' not in session or session.get('role') != 'instructor':
        flash("Please log in as instructor.")
        return redirect(url_for('login'))

    professor_id = session['user_id']

    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT DISTINCT s.semester, s.year
            FROM section s
            JOIN teaches t
              ON s.section_number = t.section_number
             AND s.course_id = t.course_id
            WHERE t.professor_id = %s
            ORDER BY s.year DESC, FIELD(s.semester, 'Winter','Fall','Summer','Spring')
        """, (professor_id,))
        semesters = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    return render_template('instructor_sections.html', semesters=semesters)


# -------------------------------
# Instructor: view sections inside semester
# -------------------------------
@app.route('/instructor/sections/<semester>/<int:year>')
def instructor_sections_by_semester(semester, year):
    if 'user_id' not in session or session.get('role') != 'instructor':
        flash("Please log in as instructor.")
        return redirect(url_for('login'))

    professor_id = session['user_id']

    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT s.section_number, s.course_id, c.c_name,
                   s.semester, s.year, s.days, s.time, s.b_name, s.room_number, s.capacity
            FROM section s
            JOIN teaches t
              ON s.section_number = t.section_number
             AND s.course_id = t.course_id
            JOIN course c ON s.course_id = c.course_id
            WHERE t.professor_id = %s
              AND s.semester = %s
              AND s.year = %s
            ORDER BY s.course_id, s.section_number
        """, (professor_id, semester, year))
        sections = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    return render_template(
        'instructor_sections_by_semester.html',
        sections=sections,
        semester=semester,
        year=year
    )


# -------------------------------
# Instructor: Roster (NOW ALSO handles grade changes + removals)
# -------------------------------
@app.route('/instructor/sections/<course_id>/<section_number>/roster')
def section_roster(course_id, section_number):
    if 'user_id' not in session or session.get('role') != 'instructor':
        flash("Please log in as instructor.")
        return redirect(url_for('login'))

    professor_id = session['user_id']

    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor(dictionary=True)

        # Verify instructor teaches this class
        cur.execute("""
            SELECT 1 FROM teaches
            WHERE professor_id = %s AND course_id = %s AND section_number = %s
        """, (professor_id, course_id, section_number))

        if not cur.fetchone():
            flash("You do not teach this section.")
            return redirect(url_for('instructor_sections'))

        # Section info
        cur.execute("""
            SELECT s.section_number, s.course_id, c.c_name, s.semester, s.year
            FROM section s
            JOIN course c ON s.course_id = c.course_id
            WHERE s.course_id = %s AND s.section_number = %s
        """, (course_id, section_number))
        section = cur.fetchone()

        # Students + grades
        cur.execute("""
            SELECT t.student_id, st.s_name, st.email, t.letter
            FROM takes t
            JOIN student st ON t.student_id = st.student_id
            WHERE t.course_id = %s AND t.section_number = %s
            ORDER BY st.s_name
        """, (course_id, section_number))
        students = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    return render_template(
        'section_roster.html',
        section=section,
        students=students
    )


# -------------------------------
# Instructor: Update/Assign Grade
# -------------------------------
@app.route('/instructor/sections/<course_id>/<section_number>/update_grade', methods=['POST'])
def update_grade(course_id, section_number):
    if 'user_id' not in session or session.get('role') != 'instructor':
        flash("Unauthorized.")
        return redirect(url_for('login'))

    student_id = request.form['student_id']
    grade = request.form['grade']

    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()

        cur.execute("""
            UPDATE takes
            SET letter = %s
            WHERE student_id = %s AND course_id = %s AND section_number = %s
        """, (grade, student_id, course_id, section_number))
        conn.commit()

        flash("Grade updated.")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for('section_roster', course_id=course_id, section_number=section_number))


# -------------------------------
# Instructor: Remove student from class
# -------------------------------
@app.route('/instructor/sections/<course_id>/<section_number>/remove_student', methods=['POST'])
def remove_student(course_id, section_number):
    if 'user_id' not in session or session.get('role') != 'instructor':
        flash("Unauthorized.")
        return redirect(url_for('login'))

    student_id = request.form['student_id']

    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM takes
            WHERE student_id = %s AND course_id = %s AND section_number = %s
        """, (student_id, course_id, section_number))
        conn.commit()

        flash("Student removed from section.")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for('section_roster', course_id=course_id, section_number=section_number))


@app.route('/instructor/advising')
def advising_dashboard():
    if not session.get('user_id') or session.get('role') != 'instructor':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    professor_id = session['user_id']

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Get professor's department
        cursor.execute("SELECT dept_id FROM professor WHERE professor_id = %s", (professor_id,))
        prof_dept = cursor.fetchone()['dept_id']

        # Students this professor already advises
        cursor.execute("""
            SELECT student_id, s_name, email, dept_id
            FROM student
            WHERE advisor = %s
        """, (professor_id,))
        advisees = cursor.fetchall()

        # Students from same department not advised by this professor
        cursor.execute("""
            SELECT student_id, s_name, email, dept_id
            FROM student
            WHERE dept_id = %s AND (advisor IS NULL OR advisor != %s)
        """, (prof_dept, professor_id))
        eligible_students = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "advising_dashboard.html",
        advisees=advisees,
        eligible_students=eligible_students
    )


@app.route('/instructor/advising/add', methods=['POST'])
def add_advisee():
    if not session.get('user_id') or session.get('role') != 'instructor':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    professor_id = session['user_id']
    student_id = request.form['student_id']

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Safe to update since foreign key ensures student exists
        cursor.execute("UPDATE student SET advisor = %s WHERE student_id = %s", (professor_id, student_id))
        connection.commit()

    finally:
        cursor.close()
        connection.close()

    flash("Student added as advisee.")
    return redirect(url_for('advising_dashboard'))


@app.route('/instructor/advising/remove', methods=['POST'])
def remove_advisee():
    if not session.get('user_id') or session.get('role') != 'instructor':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    professor_id = session['user_id']
    student_id = request.form['student_id']

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Extra safety: only remove if current professor is advisor
        cursor.execute("SELECT advisor FROM student WHERE student_id = %s", (student_id,))
        current_advisor = cursor.fetchone()[0]

        if current_advisor != professor_id:
            flash("You can only remove your own advisees.")
            return redirect(url_for('advising_dashboard'))

        cursor.execute("UPDATE student SET advisor = NULL WHERE student_id = %s", (student_id,))
        connection.commit()

    finally:
        cursor.close()
        connection.close()

    flash("Student removed from advisee list.")
    return redirect(url_for('advising_dashboard'))


@app.route('/instructor/prerequisites', methods=['GET', 'POST'])
def manage_prerequisites():
    if not session.get('user_id') or session.get('role') != 'instructor':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    professor_id = session['user_id']

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Get all courses this professor teaches
        cursor.execute("""
            SELECT s.course_id, c.c_name
            FROM section s
            JOIN course c ON s.course_id = c.course_id
            WHERE s.professor_id = %s
            GROUP BY s.course_id
        """, (professor_id,))
        courses = cursor.fetchall()

        # If a course is selected via query param, get its prerequisites
        selected_course_id = request.args.get('course_id')
        prerequisites = []
        available_courses = []

        if selected_course_id:
            # Get current prerequisites
            cursor.execute("""
                SELECT c.course_id, c.c_name
                FROM course_prerequisite cp
                JOIN course c ON cp.prereq_id = c.course_id
                WHERE cp.course_id = %s
            """, (selected_course_id,))
            prerequisites = cursor.fetchall()

            # Get all other courses in same department as possible prerequisites
            cursor.execute("""
                SELECT course_id, c_name
                FROM course
                WHERE course_id != %s
            """, (selected_course_id,))
            available_courses = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "manage_prerequisites.html",
        courses=courses,
        selected_course_id=selected_course_id,
        prerequisites=prerequisites,
        available_courses=available_courses
    )


@app.route('/instructor/prerequisites/add', methods=['POST'])
def add_prerequisite():
    course_id = request.form['course_id']
    prereq_id = request.form['prereq_id']

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT IGNORE INTO course_prerequisite (course_id, prereq_id)
        VALUES (%s, %s)
    """, (course_id, prereq_id))
    connection.commit()
    cursor.close()
    connection.close()

    flash("Prerequisite added.")
    return redirect(url_for('manage_prerequisites', course_id=course_id))


@app.route('/instructor/prerequisites/remove', methods=['POST'])
def remove_prerequisite():
    course_id = request.form['course_id']
    prereq_id = request.form['prereq_id']

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM course_prerequisite
        WHERE course_id = %s AND prereq_id = %s
    """, (course_id, prereq_id))
    connection.commit()
    cursor.close()
    connection.close()

    flash("Prerequisite removed.")
    return redirect(url_for('manage_prerequisites', course_id=course_id))


if __name__ == '__main__':
    app.run(debug=True)
