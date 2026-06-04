from flask import Flask, render_template, request, redirect, session
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "secret123"
bcrypt = Bcrypt(app)

def get_db():
    return sqlite3.connect("database.db")

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

        if user and bcrypt.check_password_hash(user[3], password):
            session['user'] = user[0]
            return redirect('/vote')

        return "Invalid Login"

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        hashed = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        db = get_db()
        db.execute("INSERT INTO users (name,email,password,voted) VALUES (?,?,?,0)",
                   (request.form['name'], request.form['email'], hashed))
        db.commit()

        return redirect('/login')

    return render_template("register.html")

# ---------------- VOTE ----------------
@app.route('/vote')
def vote():
    if not session.get('user'):
        return redirect('/login')

    db = get_db()

    status = db.execute("SELECT status FROM election WHERE id=1").fetchone()[0]
    if status == "stopped":
        return "<h3 style='text-align:center;'>Voting Closed</h3>"

    candidates = db.execute("SELECT * FROM candidates").fetchall()
    return render_template("vote.html", candidates=candidates)

# ---------------- CAST VOTE ----------------
@app.route('/cast_vote/<int:id>')
def cast_vote(id):
    if not session.get('user'):
        return redirect('/login')

    db = get_db()

    user = db.execute("SELECT voted FROM users WHERE id=?", (session['user'],)).fetchone()

    if user[0] == 1:
        return "❌ You already voted!"

    db.execute("UPDATE candidates SET votes=votes+1 WHERE id=?", (id,))
    db.execute("UPDATE users SET voted=1 WHERE id=?", (session['user'],))
    db.commit()

    return redirect('/result')

# ---------------- RESULT ----------------
@app.route('/result')
def result():
    db = get_db()
    candidates = db.execute("SELECT * FROM candidates").fetchall()
    return render_template("result.html", candidates=candidates)

# ---------------- ADMIN LOGIN ----------------
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASS = "1234"

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['email'] == ADMIN_EMAIL and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect('/admin')
        return "Invalid Admin Login"

    return render_template("admin_login.html")

# ---------------- ADMIN PANEL ----------------
@app.route('/admin', methods=['GET','POST'])
def admin():
    if not session.get('admin'):
        return redirect('/admin_login')

    db = get_db()

    if request.method == 'POST':
        db.execute("INSERT INTO candidates (name,votes) VALUES (?,0)",
                   (request.form['name'],))
        db.commit()

    candidates = db.execute("SELECT * FROM candidates").fetchall()
    status = db.execute("SELECT status FROM election WHERE id=1").fetchone()[0]

    return render_template("admin.html", candidates=candidates, status=status)

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    db.execute("DELETE FROM candidates WHERE id=?", (id,))
    db.commit()
    return redirect('/admin')

# ---------------- TOGGLE ----------------
@app.route('/toggle')
def toggle():
    db = get_db()
    status = db.execute("SELECT status FROM election").fetchone()[0]

    new_status = "started" if status == "stopped" else "stopped"
    db.execute("UPDATE election SET status=?", (new_status,))
    db.commit()

    return redirect('/admin')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)