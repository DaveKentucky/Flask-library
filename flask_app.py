from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from flask import Flask, session
from flask_session import Session
import sqlite3

# Tworzenie aplikacji
app = Flask("Flask - Lab")

# Tworzenie obsługi sesji
sess = Session()

# Ścieżka do pliku bazy danych w sqlite
db = 'database.db'

@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    # Połączenie sie z bazą danych
    conn = sqlite3.connect(db)
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    conn.execute('CREATE TABLE users (username TEXT, password TEXT, admin INTEGER)')
    conn.execute('CREATE TABLE books (author TEXT, title TEXT)')
    cur = conn.cursor();
    cur.execute("INSERT INTO users (username, password, admin) VALUES (?, ?, ?)", ('admin', 'admin', 1))
    conn.commit()
    # Zakończenie połączenia z bazą danych
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/', methods=['GET'])
def index():
    connection = sqlite3.connect(db)
    cur = connection.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    connection.close()

    if 'user' in session:
        admin = verify_admin(session['user'])
        return render_template('index.html', books=books, logged_in=True, admin=admin)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        if login and password:
            connection = sqlite3.connect(db)
            cur = connection.cursor()
            cur.execute(f'SELECT * FROM users WHERE username=\'{login}\' AND password=\'{password}\'')
            user = cur.fetchone()
            if not user:
                return render_template('login.html')
            else:
                session['user'] = login
                return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user')

    return redirect(url_for('index'))


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user' in session:
        if request.method == 'POST':
            author = request.form['author']
            title = request.form['title']

            if author and title:
                connection = sqlite3.connect(db)
                cur = connection.cursor()
                cur.execute("INSERT INTO books (author, title) VALUES (?, ?)", (author, title))
                connection.commit()
                connection.close()
                return redirect(url_for('index'))
            else:
                return render_template('add_book.html')

        elif request.method == 'GET':
            return render_template('add_book.html')
    else:
        return redirect(url_for('index'))

@app.route('/users', methods=['GET'])
def users():
    if verify_admin(session['user']):
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        connection.close()

        return render_template('users.html', users=users)
        
@app.route('/user/<username>', methods=['GET'])
def user(username):
    if verify_admin(session['user']):
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        cur.execute(f"SELECT * FROM users WHERE username=\'{str(username)}\'")
        user = cur.fetchone()
        connection.close()

        return render_template('user.html', user=user)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user' in session:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            is_admin = True if request.form.get('is-admin') else False
            print(f'u: {username}, passwd: {password}, is admin: {is_admin}')
    
            if username and password and is_admin is not None:
                connection = sqlite3.connect(db)
                cur = connection.cursor()
                cur.execute("INSERT INTO users (username, password, admin) VALUES (?, ?, ?)", (username, password, (1 if is_admin else 0)))
                connection.commit()
                connection.close()
                return redirect(url_for('users'))
            else:
                return render_template('add_user.html')
        elif request.method == 'GET':
            return render_template('add_user.html')
    else:
        return redirect(url_for('index'))

def verify_admin(username):
    connection = sqlite3.connect(db)
    cur = connection.cursor()
    cur.execute(f'SELECT username FROM users WHERE admin=\'1\'')
    admins = cur.fetchall()
    connection.close()

    if username in admins[0]:
        return True
    else:
        return False

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.debug = True
app.run()