from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector


app = Flask(__name__)
app.secret_key = "Cleveland_Browns"

db_config = {
    'user': 'euka', 
    'password': '@Dubem0610',
    'host': 'dbdev.cs.kent.edu',
    'database': 'euka'
}

"""@app.route('/')
def home():
    return render_template('index.html')"""
    
@app.route('/')
def home():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT student_name, student_id, gpa FROM student;")
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', students=students)
    except Exception as e:
        return f"Database connection failed: {e}"

if __name__ == '__main__':
    app.run(debug=True)
    

    
 