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
    'database': 'project'
}


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!')

            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'instructor':
                return redirect(url_for('instructor_dashboard'))
            elif user['role'] == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                flash('Unknown role.')
                return redirect(url_for('login'))
        else:
            flash('Invalid username or password')

    # If GET request or no valid login, just show the page again
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