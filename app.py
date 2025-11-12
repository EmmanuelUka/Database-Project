from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector


app = Flask(__name__)
app.secret_key = "Cleveland_Browns"

db_config = {
    'user': 'zevans6', 
    'password': 'k38ndcYQ',
    'host': 'dbdev.cs.kent.edu',
    'database': 'zevans6'
}

if __name__ == '__main__':
    app.run(debug=True)