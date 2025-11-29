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
        user = None
        
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
            s.address_houseNumber, s.address_street, s.address_city, s.address_state, s.address_zip, s.advisor
            FROM student s
            LEFT JOIN department d ON s.dept_id = d.department_id
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

if __name__ == '__main__':
    app.run(debug=True)