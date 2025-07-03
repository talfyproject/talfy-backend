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

# Modello User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    job_title = db.Column(db.String(100), nullable=True)

# Modello CandidateProfile
class CandidateProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(20), nullable=False)
    salary_range = db.Column(db.String(30), nullable=False)
    sector = db.Column(db.String(100), nullable=False)
    tools = db.Column(db.Text, nullable=False)
    english_level = db.Column(db.String(20), nullable=False)
    education = db.Column(db.String(50), nullable=False)
    area_of_study = db.Column(db.String(100), nullable=False)

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

# Endpoint per il salvataggio del profilo candidato
@app.route('/submit-candidate-profile', methods=['POST'])
def submit_candidate_profile():
    try:
        data = request.form

        # Per ora associamo al primo utente candidato (in futuro user session/token)
        user = User.query.filter_by(role='candidate').order_by(User.id.desc()).first()
        if not user:
            return "No candidate user found", 404

        profile = CandidateProfile(
            user_id=user.id,
            fullname=data.get('fullname'),
            experience=data.get('experience'),
            salary_range=data.get('salary_range'),
            sector=data.get('sector'),
            tools=data.get('tools'),
            english_level=data.get('english_level'),
            education=data.get('education'),
            area_of_study=data.get('area_of_study')
        )
        db.session.add(profile)
        db.session.commit()

        return redirect('/thank-you.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

# Endpoint base
@app.route('/')
def home():
    return 'Talfy backend running'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
