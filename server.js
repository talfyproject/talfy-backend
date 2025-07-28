// server.js
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { Pool } = require('pg');

const app = express();
const PORT = process.env.PORT || 5000;

// ✅ Connessione al database PostgreSQL (Render)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://talfy_db_user:1POTty3Z6HosHBD8TDtzh2hWqcVFdRAq@dpg-d1gdskqli9vc73ahklag-a.frankfurt-postgres.render.com/talfy_db',
  ssl: { rejectUnauthorized: false }
});

// Middleware
app.use(cors());
app.use(bodyParser.json());

// ✅ Test DB
pool.connect()
  .then(() => console.log('✅ Connected to PostgreSQL'))
  .catch(err => console.error('❌ DB Connection Error:', err));

// ✅ Rotta di test
app.get('/', (req, res) => {
  res.json({ message: 'Talfy Backend with PostgreSQL is running!' });
});

// ✅ Registrazione utente
app.post('/api/register', async (req, res) => {
  const { email, password, userType } = req.body;

  if (!email || !password || !userType) {
    return res.status(400).json({ message: 'Missing fields' });
  }

  try {
    const result = await pool.query(
      'INSERT INTO users (email, password, user_type, profile_completed) VALUES ($1, $2, $3, $4) RETURNING id, email, user_type, profile_completed',
      [email, password, userType, false]
    );

    res.json({ message: 'User registered successfully', user: result.rows[0] });
  } catch (error) {
    console.error('Error inserting user:', error);
    res.status(500).json({ message: 'Database error' });
  }
});

// ✅ Login
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const result = await pool.query(
      'SELECT id, email, user_type, profile_completed FROM users WHERE email=$1 AND password=$2',
      [email, password]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    res.json({ message: 'Login successful', user: result.rows[0] });
  } catch (error) {
    console.error('Error during login:', error);
    res.status(500).json({ message: 'Database error' });
  }
});

// ✅ Completa profilo
app.post('/api/complete-profile', async (req, res) => {
  const { userId, profileData } = req.body;

  try {
    await pool.query(
      'UPDATE users SET profile_completed=$1, profile_data=$2 WHERE id=$3',
      [true, JSON.stringify(profileData), userId]
    );

    res.json({ message: 'Profile completed' });
  } catch (error) {
    console.error('Error updating profile:', error);
    res.status(500).json({ message: 'Database error' });
  }
});

// ✅ Contatori
app.get('/api/counters', async (req, res) => {
  try {
    const candidatesResult = await pool.query("SELECT COUNT(*) FROM users WHERE user_type='candidate'");
    const companiesResult = await pool.query("SELECT COUNT(*) FROM users WHERE user_type='company'");

    res.json({
      candidates: parseInt(candidatesResult.rows[0].count),
      companies: parseInt(companiesResult.rows[0].count)
    });
  } catch (error) {
    console.error('Error fetching counters:', error);
    res.status(500).json({ message: 'Database error' });
  }
});

// ✅ Avvio server
app.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}`);
});
