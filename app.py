from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://www.talfy.eu"]}})

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELS
class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'candidate' or 'company'

class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profile'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    current_job = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    salary_range = db.Column(db.String(50))
    sector = db.Column(db.String(100))
    tools = db.Column(db.String(255))
    avatar = db.Column(db.String(255))

class CompanyProfile(db.Model):
    __tablename__ = 'company_profile'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(100))
    num_employees = db.Column(db.Integer)
    headquarters = db.Column(db.String(100))
    logo = db.Column(db.String(255))

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
        # Conta solo i candidati che hanno completato il profilo
        candidate_count = db.session.query(CandidateProfile).count()

        # Conta solo le aziende che hanno completato il profilo
        company_count = db.session.query(CompanyProfile).count()

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

        return jsonify({"message": "Candidate profile saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save-company-profile", methods=["POST"])
def save_company_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        company_name = data.get("company_name")
        sector = data.get("sector")
        num_employees = data.get("num_employees")
        headquarters = data.get("headquarters")
        logo = data.get("logo")

        if not user_id or not company_name:
            return jsonify({"error": "Missing user_id or company_name"}), 400

        existing_profile = CompanyProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            return jsonify({"error": "Company profile already exists"}), 409

        profile = CompanyProfile(
            user_id=user_id,
            company_name=company_name,
            sector=sector,
            num_employees=num_employees,
            headquarters=headquarters,
            logo=logo
        )
        db.session.add(profile)
        db.session.commit()

        return jsonify({"message": "Company profile saved"}), 201
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

@app.route("/api/companies", methods=["GET"])
def get_companies():
    try:
        companies = CompanyProfile.query.all()
        result = []
        for c in companies:
            result.append({
                "id": c.id,
                "company_name": c.company_name,
                "sector": c.sector,
                "num_employees": c.num_employees,
                "headquarters": c.headquarters,
                "logo": c.logo
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Error loading companies: {str(e)}"}), 500

@app.route("/init-db")
def init_db():
    try:
        db.create_all()
        return "✅ Database initialized successfully", 200
    except Exception as e:
        return f"❌ Error initializing DB: {e}", 500
@app.route("/admin-data")
def admin_data():
    try:
        users = User.query.all()
        candidates = CandidateProfile.query.all()
        companies = CompanyProfile.query.all()

        users_data = []
        for u in users:
            users_data.append({
                "id": u.id,
                "email": u.email,
                "type": u.user_type
            })

        candidate_data = []
        for c in candidates:
            candidate_data.append({
                "id": c.id,
                "user_id": c.user_id,
                "name": c.display_name,
                "job": c.current_job,
                "years": c.experience_years
            })

        company_data = []
        for c in companies:
            company_data.append({
                "id": c.id,
                "user_id": c.user_id,
                "name": c.company_name,
                "sector": c.sector,
                "hq": c.headquarters
            })

        return jsonify({
            "users": users_data,
            "candidates": candidate_data,
            "companies": company_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# MAIN
if __name__ == "__main__":
    app.run(debug=True)
