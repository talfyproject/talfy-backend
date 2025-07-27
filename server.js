// server.js - Backend Talfy con Node.js + Express + PostgreSQL
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { Pool } from 'pg';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

// Inizializza Express
const app = express();
app.use(cors());
app.use(express.json());

// Percorso assoluto per servire i file statici
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use(express.static(path.join(__dirname, 'public')));

// Connessione PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

// Test connessione DB
pool.connect()
  .then(() => console.log('✅ Connesso al database PostgreSQL'))
  .catch(err => console.error('❌ Errore connessione DB:', err));

// ✅ API: Registrazione utente
app.post('/api/auth/register', async (req, res) => {
  const { email, password, accountType, company } = req.body;

  try {
    const userExists = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (userExists.rows.length > 0) {
      return res.status(400).json({ message: 'Email già registrata' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const result = await pool.query(
      'INSERT INTO users (email, password, account_type, company_name) VALUES ($1, $2, $3, $4) RETURNING id',
      [email, hashedPassword, accountType, company || null]
    );

    const userId = result.rows[0].id;
    res.json({ status: "success", id: userId });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Errore interno server' });
  }
});

// ✅ API: Login utente
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (result.rows.length === 0) return res.status(400).json({ message: 'Utente non trovato' });

    const user = result.rows[0];
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) return res.status(400).json({ message: 'Password errata' });

    const token = jwt.sign({ id: user.id, accountType: user.account_type }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.json({ status: "success", token, userId: user.id, accountType: user.account_type });
  } catch (error) {
    res.status(500).json({ message: 'Errore interno server' });
  }
});

// ✅ API: Contatori
app.get('/api/stats', async (req, res) => {
  try {
    const candidatesCount = await pool.query("SELECT COUNT(*) FROM users WHERE account_type = 'candidate'");
    const companiesCount = await pool.query("SELECT COUNT(*) FROM users WHERE account_type = 'company'");
    res.json({ candidates: candidatesCount.rows[0].count, companies: companiesCount.rows[0].count });
  } catch (error) {
    res.status(500).json({ message: 'Errore recupero statistiche' });
  }
});

// Avvio server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server avviato su http://localhost:${PORT}`));
