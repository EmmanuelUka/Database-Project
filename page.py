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


@app.route('/student/profile')
def student_profile():
    if not session.get('user_id') or session.get('role') != 'student':
        flash('Unauthorized access. Please log in as student.')
        return redirect(url_for('login'))
    
    student_id = session['user_id']
    
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student WHERE user_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template("student_profile.html", student=student)




@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)