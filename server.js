import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import pkg from "pg";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import multer from "multer";
import path from "path";
import fs from "fs";

dotenv.config();
const { Pool } = pkg;

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors({ origin: "*", methods: ["GET", "POST"], allowedHeaders: ["Content-Type", "Authorization"] }));
app.use(express.json());
app.use(express.urlencoded({ extended: true })); // ✅ per gestire form/text
app.use(express.static("public"));

// ✅ Upload folder
const uploadDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}
app.use("/uploads", express.static(uploadDir));

// ✅ Multer config
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, Date.now() + "-" + file.originalname)
});
const upload = multer({ storage });

// ✅ PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

pool.connect()
  .then(() => console.log("✅ Connected to PostgreSQL"))
  .catch((err) => console.error("❌ DB connection error:", err));

const JWT_SECRET = process.env.JWT_SECRET || "supersecretkey";

// ✅ JWT Middleware
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ success: false, error: "Unauthorized" });
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ success: false, error: "Invalid token" });
  }
};

// ✅ ROUTES

// Test route
app.get("/", (req, res) => res.json({ message: "✅ Talfy Backend is running" }));

// REGISTER
app.post("/api/register", async (req, res) => {
  const { email, password, user_type } = req.body;
  if (!email || !password || !user_type) {
    return res.status(400).json({ success: false, error: "Missing required fields" });
  }

  try {
    const existingUser = await pool.query("SELECT id FROM users WHERE email = $1", [email]);
    if (existingUser.rows.length > 0) {
      return res.status(400).json({ success: false, error: "Email already registered" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const result = await pool.query(
      "INSERT INTO users (email, password, user_type) VALUES ($1, $2, $3) RETURNING id",
      [email, hashedPassword, user_type]
    );

    res.json({ success: true, userId: result.rows[0].id, userType: user_type });
  } catch (err) {
    console.error("❌ Registration error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// LOGIN
app.post("/api/login", async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ success: false, error: "Email and password required" });
  }

  try {
    const userResult = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (userResult.rows.length === 0) return res.status(400).json({ success: false, error: "Invalid credentials" });

    const user = userResult.rows[0];
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) return res.status(400).json({ success: false, error: "Invalid credentials" });

    const token = jwt.sign({ id: user.id, email: user.email, user_type: user.user_type }, JWT_SECRET, { expiresIn: "2h" });

    res.json({ success: true, token, userId: user.id, userType: user.user_type });
  } catch (err) {
    console.error("❌ Login error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

/* ========= BLOCCO DUPLICATO (COMMENTATO, lasciato intatto) =========

import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import pkg from "pg";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import multer from "multer";
import path from "path";
import fs from "fs";

dotenv.config();
const { Pool } = pkg;

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors({ origin: "*", methods: ["GET", "POST"], allowedHeaders: ["Content-Type", "Authorization"] }));
app.use(express.json());
app.use(express.static("public"));

// ✅ Upload folder
const uploadDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}
app.use("/uploads", express.static(uploadDir));

// ✅ Multer config
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, Date.now() + "-" + file.originalname)
});
const upload = multer({ storage });

// ✅ PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

pool.connect()
  .then(() => console.log("✅ Connected to PostgreSQL"))
  .catch((err) => console.error("❌ DB connection error:", err));

const JWT_SECRET = process.env.JWT_SECRET || "supersecretkey";

// ✅ JWT Middleware
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ success: false, error: "Unauthorized" });
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ success: false, error: "Invalid token" });
  }
};

// ✅ ROUTES

// Test route
app.get("/", (req, res) => res.json({ message: "✅ Talfy Backend is running" }));

// REGISTER
app.post("/api/register", async (req, res) => {
  const { email, password, user_type } = req.body;
  if (!email || !password || !user_type) {
    return res.status(400).json({ success: false, error: "Missing required fields" });
  }

  try {
    const existingUser = await pool.query("SELECT id FROM users WHERE email = $1", [email]);
    if (existingUser.rows.length > 0) {
      return res.status(400).json({ success: false, error: "Email already registered" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const result = await pool.query(
      "INSERT INTO users (email, password, user_type) VALUES ($1, $2, $3) RETURNING id",
      [email, hashedPassword, user_type]
    );

    res.json({ success: true, userId: result.rows[0].id, userType: user_type });
  } catch (err) {
    console.error("❌ Registration error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// LOGIN
app.post("/api/login", async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ success: false, error: "Email and password required" });
  }

  try {
    const userResult = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (userResult.rows.length === 0) return res.status(400).json({ success: false, error: "Invalid credentials" });

    const user = userResult.rows[0];
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) return res.status(400).json({ success: false, error: "Invalid credentials" });

    const token = jwt.sign({ id: user.id, email: user.email, user_type: user.user_type }, JWT_SECRET, { expiresIn: "2h" });

    res.json({ success: true, token, userId: user.id, userType: user.user_type });
  } catch (err) {
    console.error("❌ Login error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
*/
 
// ✅ COMPLETE PROFILE (with upload)
app.post("/api/candidate-profile", authMiddleware, upload.fields([
  { name: "photo", maxCount: 1 },
  { name: "cv", maxCount: 1 }
]), async (req, res) => {
  try {
    const userId = req.user.id;

    console.log("Updating userId:", userId);

    // parse arrays safely
    let sectorsArr = [];
    let softwareArr = [];
    try {
      sectorsArr = req.body.sectors ? JSON.parse(req.body.sectors) : [];
    } catch { sectorsArr = []; }
    try {
      softwareArr = req.body.software ? JSON.parse(req.body.software) : [];
    } catch { softwareArr = []; }

    const profileData = {
      firstName: req.body.firstName || null,
      lastName: req.body.lastName || null,
      phone: req.body.phone || null,
      location: req.body.location || null,
      birthDate: (req.body.birthDay && req.body.birthMonth && req.body.birthYear)
        ? `${req.body.birthDay}-${req.body.birthMonth}-${req.body.birthYear}`
        : null,
      jobRole: req.body.jobRole || req.body.otherJobRole || null,
      avatar: req.body.avatar || null,
      experience: req.body.experience || null,
      education: req.body.education || null,
      salaryRange: {
        min: req.body.salaryMin || null,
        max: req.body.salaryMax || null
      },
      languages: {
        native: req.body.nativeLanguage || null,
        second: { lang: req.body.secondLanguage || null, level: req.body.secondLanguageLevel || null },
        third: { lang: req.body.thirdLanguage || null, level: req.body.thirdLanguageLevel || null }
      },
      availability: req.body.availability || null,
      remoteWork: req.body.remoteWork || null,
      relocation: req.body.relocation || null,
      summary: req.body.summary || null,
      sectors: sectorsArr,
      software: softwareArr,
      photo: req.files?.photo?.[0] ? `/uploads/${req.files.photo[0].filename}` : null,
      cv: req.files?.cv?.[0] ? `/uploads/${req.files.cv[0].filename}` : null
    };

    // ✅ UNICO UPDATE CON RETURNING
    const upd = await pool.query(
      "UPDATE users SET profile = $1::jsonb WHERE id = $2 RETURNING id, email, user_type, profile",
      [JSON.stringify(profileData), userId]
    );
    if (upd.rowCount === 0) {
      return res.status(404).json({ success: false, error: "User not found" });
    }
    res.json({ success: true, message: "Profile saved", user: upd.rows[0] });
  } catch (err) {
    console.error("❌ Profile error:", err);
    res.status(500).json({ success: false, error: "Error saving profile" });
  }
});

// ✅ GET USER PROFILE
app.get("/api/user/:id", async (req, res) => {
  try {
    const result = await pool.query("SELECT id, email, user_type, profile FROM users WHERE id = $1", [req.params.id]);
    if (result.rows.length === 0) return res.status(404).json({ success: false, error: "User not found" });
    res.json({ success: true, user: result.rows[0] });
  } catch (err) {
    console.error("❌ Get user error:", err);
    res.status(500).json({ success: false, error: "Error fetching user" });
  }
});

// ✅ COUNTERS
app.get("/api/counters", async (req, res) => {
  try {
    const candidates = await pool.query("SELECT COUNT(*) FROM users WHERE user_type = 'candidate'");
    const companies = await pool.query("SELECT COUNT(*) FROM users WHERE user_type = 'company'");
    res.json({ success: true, candidates: parseInt(candidates.rows[0].count), companies: parseInt(companies.rows[0].count) });
  } catch (err) {
    console.error("❌ Counters error:", err);
    res.status(500).json({ success: false, error: "Error fetching counters" });
  }
});

// ✅ Start Server
app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));

/* ========= COPIE DUPLICATE FINALI (COMMENTATE, lasciate nel file) =========

// ✅ GET USER PROFILE (duplicato)
app.get("/api/user/:id", async (req, res) => {
  try {
    const result = await pool.query("SELECT id, email, user_type, profile FROM users WHERE id = $1", [req.params.id]);
    if (result.rows.length === 0) return res.status(404).json({ success: false, error: "User not found" });
    res.json({ success: true, user: result.rows[0] });
  } catch (err) {
    console.error("❌ Get user error:", err);
    res.status(500).json({ success: false, error: "Error fetching user" });
  }
});

// ✅ COUNTERS (duplicato)
app.get("/api/counters", async (req, res) => {
  try {
    const candidates = await pool.query("SELECT COUNT(*) FROM users WHERE user_type = 'candidate'");
    const companies = await pool.query("SELECT COUNT(*) FROM users WHERE user_type = 'company'");
    res.json({ success: true, candidates: parseInt(candidates.rows[0].count), companies: parseInt(companies.rows[0].count) });
  } catch (err) {
    console.error("❌ Counters error:", err);
    res.status(500).json({ success: false, error: "Error fetching counters" });
  }
});

// ✅ Start Server (duplicato)
app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));
*/










