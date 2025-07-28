// Import dependencies
import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import pkg from "pg";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

dotenv.config();
const { Pool } = pkg;

const app = express();
const PORT = process.env.PORT || 5000;

// Middlewares
app.use(cors());
app.use(express.json());
app.use(express.static("public")); // Cartella per i tuoi file statici Talfy

// Database connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

// Test DB connection
pool.connect()
  .then(() => console.log("✅ Connected to PostgreSQL"))
  .catch((err) => console.error("❌ Database connection error:", err));

// JWT Secret
const JWT_SECRET = process.env.JWT_SECRET || "supersecretkey";

// ✅ ROUTES

// --- 1. Registration ---
app.post("/api/register", async (req, res) => {
  const { email, password, user_type } = req.body;

  if (!email || !password || !user_type) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  try {
    // Check if email already exists
    const existingUser = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (existingUser.rows.length > 0) {
      return res.status(400).json({ error: "Email already registered" });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Insert user
    const result = await pool.query(
      "INSERT INTO users (email, password, user_type) VALUES ($1, $2, $3) RETURNING id",
      [email, hashedPassword, user_type]
    );

    res.json({ message: "Registration successful", userId: result.rows[0].id });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error during registration" });
  }
});

// --- 2. Login ---
app.post("/api/login", async (req, res) => {
  const { email, password } = req.body;

  try {
    const userResult = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (userResult.rows.length === 0) {
      return res.status(400).json({ error: "Invalid email or password" });
    }

    const user = userResult.rows[0];
    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
      return res.status(400).json({ error: "Invalid email or password" });
    }

    // Generate JWT
    const token = jwt.sign({ id: user.id, email: user.email, user_type: user.user_type }, JWT_SECRET, { expiresIn: "2h" });

    res.json({ message: "Login successful", token, userId: user.id, userType: user.user_type });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error during login" });
  }
});

// --- 3. Update Profile ---
app.post("/api/update-profile", async (req, res) => {
  const { userId, profileData } = req.body;

  if (!userId || !profileData) {
    return res.status(400).json({ error: "Missing required data" });
  }

  try {
    await pool.query(
      "UPDATE users SET profile = $1 WHERE id = $2",
      [profileData, userId]
    );

    res.json({ message: "Profile updated successfully" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error updating profile" });
  }
});

// --- 4. Get Counters ---
app.get("/api/counters", async (req, res) => {
  try {
    const candid
