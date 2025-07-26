from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chiave-super-segreta"

DB_URL = "postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db"

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM candidates;")
    total_candidates = cur.fetchone()['total']
    cur.close()
    conn.close()
    return render_template("index.html", total_candidates=total_candidates)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]
        
        if len(password) < 8:
            error = "Password must be at least 8 characters long."
        elif not any(c.isupper() for c in password):
            error = "Password must contain at least one uppercase letter."
        elif not any(c.isdigit() for c in password):
            error = "Password must contain at least one number."
        elif not any(c in "!@#$%^&*()_+-=[]{};':,.<>?/" for c in password):
            error = "Password must contain at least one special character."

        if not error:
            hashed_password = generate_password_hash(password)
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO candidates (email, password) VALUES (%s, %s) RETURNING id;", (email, hashed_password))
                user_id = cur.fetchone()['id']
                conn.commit()
                session['user_id'] = user_id
                session['email'] = email
                return redirect(url_for("complete_profile"))
            except psycopg2.Error:
                conn.rollback()
                error = "Email already registered."
            finally:
                cur.close()
                conn.close()
    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM candidates WHERE email = %s;", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            if user['name']:
                return redirect(url_for("candidate_profile", user_id=user['id']))
            else:
                return redirect(url_for("complete_profile"))
        else:
            error = "Invalid email or password."
    return render_template("login.html", error=error)

@app.route("/complete-profile", methods=["GET", "POST"])
def complete_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE candidates SET name = %s WHERE id = %s;", (name, session['user_id']))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("candidate_profile", user_id=session['user_id']))

    return render_template("complete-profile.html")

@app.route("/candidate/<int:user_id>")
def candidate_profile(user_id):
    if "user_id" not in session or session["user_id"] != user_id:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidates WHERE id = %s;", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("candidate.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
