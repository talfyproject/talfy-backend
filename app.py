from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Connessione al database PostgreSQL su Render
conn = psycopg2.connect(
    dbname="talfy_db",
    user="talfy_db_user",
    password="1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq",
    host="dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com",
    port="5432"
)

# 🔹 Endpoint per visualizzare il form candidato
@app.route("/complete-profile")
def complete_profile_page():
    return render_template("complete-profile-candidate.html")

# 🔹 Endpoint per registrare un nuovo utente
@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json()

    email = data.get("email")
    raw_password = data.get("password")
    is_company = data.get("is_company", False)

    hashed_password = generate_password_hash(raw_password)

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO myschema.users (email, password, is_company)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (email, hashed_password, is_company))
            user_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({"message": "User registered successfully", "user_id": user_id}), 200
    except Exception as e:
        print("Registration error:", e)
        return jsonify({"error": "Registration failed"}), 400

# 🔹 Endpoint per salvare il profilo candidato
@app.route("/api/candidate-profile", methods=["POST"])
def save_candidate_profile():
    data = request.get_json()

    user_id = int(data.get("user_id"))

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO myschema.candidates
            (user_id, full_name, job_title, experience_years, salary_range, industry, english_level, tools, education_level, education_area)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            data.get("full_name"),
            data.get("job_title"),
            data.get("experience_years"),
            data.get("salary_range"),
            data.get("industry"),
            data.get("english_level"),
            data.get("tools"),
            data.get("education_level"),
            data.get("education_area")
        ))
        conn.commit()

    return jsonify({"message": "Candidate profile saved successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
