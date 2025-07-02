from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    is_company = data.get('is_company', False)

    if not email or not password:
        return jsonify({'success': False, 'message': 'Missing email or password'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM myschema.users WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Email already registered'}), 409

        cur.execute(
            "INSERT INTO myschema.users (email, password, is_company) VALUES (%s, %s, %s) RETURNING id",
            (email, password, is_company)
        )
        user_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({'success': True, 'id': user_id})

    except Exception as e:
        print("Server error:", e)
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

    finally:
        cur.close()
        conn.close()

@app.route('/api/counts', methods=['GET'])
def get_counts():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM myschema.users WHERE is_company = FALSE")
        candidates = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM myschema.users WHERE is_company = TRUE")
        companies = cur.fetchone()[0]
        return jsonify({'candidates': candidates, 'companies': companies})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
