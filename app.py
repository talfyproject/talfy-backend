from flask import Flask, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configura il database PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelli per User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    job_title = db.Column(db.String(100), nullable=True)

# Endpoint per la registrazione
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.form
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        job_title = data.get('job_title') if role == 'candidate' else None

        if not email or not password or not role:
            return "Missing required fields", 400

        existing = User.query.filter_by(email=email).first()
        if existing:
            return "Email already registered", 409

        new_user = User(email=email, password=password, role=role, job_title=job_title)
        db.session.add(new_user)
        db.session.commit()

        # Redirect alla pagina giusta dopo la registrazione
        if role == 'candidate':
            return redirect('/complete-profile-candidate.html')
        else:
            return redirect('/complete-profile-company.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

# Endpoint base (opzionale)
@app.route('/')
def home():
    return 'Talfy backend running'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
