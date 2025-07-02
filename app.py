
from flask import Flask, request, redirect
import psycopg2
import bcrypt
import os

app = Flask(__name__)

# Connessione al database PostgreSQL (Render)
DATABASE_URL = "postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    role = request.form.get("role")
    job_title = request.form.get("job_title") if role == "candidate" else None

    if password != confirm_password:
        return "Passwords do not match", 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_db_connection()
    cur = conn.cursor()

    # Verifica se l'email è già registrata
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return "Email already registered", 400

    # Inserimento nuovo utente
    cur.execute(
        "INSERT INTO users (email, password, role, job_title) VALUES (%s, %s, %s, %s)",
        (email, hashed, role, job_title)
    )
    conn.commit()
    cur.close()
    conn.close()

    # Reindirizzamento
    if role == "candidate":
        return redirect("/complete-profile-candidate.html")
    else:
        return redirect("/complete-profile-company.html")

if __name__ == "__main__":
    app.run(debug=True)
