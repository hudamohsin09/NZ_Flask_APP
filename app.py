import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'xyz'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 4306
app.config['MYSQL_USER'] = 'root@'
app.config['MYSQL_PASSWORD'] = 'YES'
app.config['MYSQL_DB'] = 'flask_users'

mysql = MySQL(app)



# Function to hash the password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])


def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM `user-system` WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['login'] = True
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return render_template('user.html', message=message)
        else:
            message = 'Please enter correct email / password!'
    
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.pop('login', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/registration', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM `user-system` WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not email or not password:
            message = 'Please fill out the form!'
        else:
            # Hash the password before storing it in the database
            hashed_password = hash_password(password)
            cursor.execute('INSERT INTO `user-system` (`email`, `password`) VALUES (%s, %s)', (email, hashed_password))
            mysql.connection.commit()
            message = 'You have successfully registered!'
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    
    return render_template('registration.html', message=message)

if __name__ == "__main__":
    app.run(debug=True)  

