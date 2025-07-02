from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Connessione al database PostgreSQL Render
conn = psycopg2.connect(
    dbname="talfy_db",
    user="talfy_db_user",
    password="1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq",
    host="dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com",
    port="5432"
)

# 🔹 Endpoint per visualizzare la pagina del form
@app.route("/complete-profile")
def complete_profile_page():
    return render_template("complete-profile-candidate.html")

# 🔹 Endpoint che riceve e salva il profilo candidato
@app.route("/api/candidate-profile", methods=["POST"])
def save_candidate_profile():
    data = request.get_json()

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO myschema.candidates
            (user_id, full_name, job_title, experience_years, salary_range, industry, english_level, tools, education_level, education_area)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            1,  # user_id fittizio per ora (da collegare a login/registrazione)
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
