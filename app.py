from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'candidate' or 'company'

class CandidateProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    current_job = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    salary_range = db.Column(db.String(50))
    sector = db.Column(db.String(100))
    tools = db.Column(db.String(255))
    avatar = db.Column(db.String(255))

# ROUTES
@app.route("/")
def home():
    return "✅ Talfy Backend Running!"

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user_type = data.get("user_type")

        if not all([email, password, user_type]):
            return jsonify({"error": "Missing fields"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 409

        new_user = User(email=email, password=password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Registration successful", "user_id": new_user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/counts", methods=["GET"])
def get_counts():
    try:
        candidate_count = User.query.filter_by(user_type="candidate").count()
        company_count = User.query.filter_by(user_type="company").count()
        return jsonify({
            "candidates": candidate_count,
            "companies": company_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save-candidate-profile", methods=["POST"])
def save_candidate_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        display_name = data.get("display_name")
        current_job = data.get("current_job")
        experience_years = data.get("experience_years")
        salary_range = data.get("salary_range")
        sector = data.get("sector")
        tools = data.get("tools")
        avatar = data.get("avatar")

        if not user_id or not display_name:
            return jsonify({"error": "Missing user_id or display_name"}), 400

        existing_profile = CandidateProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            return jsonify({"error": "Profile already exists"}), 409

        profile = CandidateProfile(
            user_id=user_id,
            display_name=display_name,
            current_job=current_job,
            experience_years=experience_years,
            salary_range=salary_range,
            sector=sector,
            tools=tools,
            avatar=avatar
        )
        db.session.add(profile)
        db.session.commit()

        return jsonify({"message": "Profile saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/candidates", methods=["GET"])
def get_candidates():
    try:
        candidates = CandidateProfile.query.all()
        result = []
        for c in candidates:
            result.append({
                "id": c.id,
                "display_name": c.display_name,
                "current_job": c.current_job,
                "experience_years": c.experience_years,
                "salary_range": c.salary_range,
                "sector": c.sector,
                "tools": c.tools,
                "avatar": c.avatar
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Error loading candidates: {str(e)}"}), 500

@app.route("/init-db")
def init_db():
    try:
        db.create_all()
        return "✅ Database initialized successfully", 200
    except Exception as e:
        return f"❌ Error initializing DB: {e}", 500

# MAIN
if __name__ == "__main__":
    app.run(debug=True)
