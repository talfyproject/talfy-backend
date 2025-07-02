from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Configurazione del database
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Rotta per la registrazione (candidati o aziende)
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    user_type = data.get("user_type")
    email = data.get("email")
    password = data.get("password")

    if not all([user_type, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if user_type == "candidate":
            cur.execute("""
                INSERT INTO candidates (email, password)
                VALUES (%s, %s)
                RETURNING id
            """, (email, password))
        elif user_type == "company":
            cur.execute("""
                INSERT INTO companies (email, password)
                VALUES (%s, %s)
                RETURNING id
            """, (email, password))
        else:
            return jsonify({"error": "Invalid user_type"}), 400

        user_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"success": True, "id": user_id})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Rotta per ottenere il numero totale di candidati e aziende
@app.route('/api/count', methods=['GET'])
def get_counts():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM candidates")
        candidate_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM companies")
        company_count = cur.fetchone()[0]

        return jsonify({
            "candidates": candidate_count,
            "companies": company_count
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
