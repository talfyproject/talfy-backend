from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chiave-super-segreta"  # CAMBIALA in produzione

# URL DB PostgreSQL
DB_URL = "postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db"

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

# Homepage con contatore candidati
@app.route("/")
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM candidates;")
        total_candidates = cur.fetchone()['total']
        cur.close()
        conn.close()
    except Exception as e:
        print("Errore DB homepage:", e)
        total_candidates = 0
    return render_template("index.html", total_candidates=total_candidates)

# Registrazione
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        # Controllo password
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
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO candidates (email, password) VALUES (%s, %s) RETURNING id;",
                            (email, hashed_password))
                result = cur.fetchone()
                if result:
                    user_id = result['id']
                    conn.commit()
                    session['user_id'] = user_id
                    session['email'] = email
                    print(f"✅ Registrazione OK - ID: {user_id}")
                    return redirect(url_for("complete_profile"))
                else:
                    conn.rollback()
                    error = "Database error: no ID returned."
            except psycopg2.Error as e:
                print("Errore registrazione:", e)
                conn.rollback()
                error = "Email already registered or DB error."
            finally:
                cur.close()
                conn.close()
    return render_template("register.html", error=error)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
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
        except Exception as e:
            print("Errore login:", e)
            error = "Unexpected error. Try again."
    return render_template("login.html", error=error)

# Completamento profilo
@app.route("/complete-profile", methods=["GET", "POST"])
def complete_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE candidates SET name = %s WHERE id = %s;", (name, session['user_id']))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("candidate_profile", user_id=session['user_id']))
        except Exception as e:
            print("Errore salvataggio nome:", e)
            return "Error saving profile."

    return render_template("complete-profile.html")

# Pagina candidato
@app.route("/candidate/<int:user_id>")
def candidate_profile(user_id):
    if "user_id" not in session or session["user_id"] != user_id:
        return redirect(url_for("login"))

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM candidates WHERE id = %s;", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if not user:
            return "User not found."
    except Exception as e:
        print("Errore caricamento candidato:", e)
        return "Database error."
    return render_template("candidate.html", user=user)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
