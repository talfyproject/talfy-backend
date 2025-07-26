const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Database vuoto - partiamo da 0!
let users = [];
let candidates = [];

// Route principale
app.get('/', (req, res) => {
  res.json({ 
    message: 'Talfy Backend API is running!',
    candidatesCount: candidates.length,
    usersCount: users.length
  });
});

// REGISTRAZIONE
app.post('/api/auth/register', (req, res) => {
  const { name, email, password } = req.body;
  
  // Validazione base
  if (!name || !email || !password) {
    return res.status(400).json({ message: 'Nome, email e password sono obbligatori' });
  }
  
  // Controlla se esiste già
  const exists = users.find(u => u.email === email);
  if (exists) {
    return res.status(400).json({ message: 'Email già registrata' });
  }
  
  // Crea nuovo utente
  const newUser = {
    id: users.length + 1,
    name,
    email,
    password,
    registeredAt: new Date().toISOString()
  };
  
  users.push(newUser);
  
  res.json({
    success: true,
    message: 'Registrazione completata con successo!',
    user: { 
      id: newUser.id, 
      name: newUser.name, 
      email: newUser.email 
    },
    nextStep: 'complete-profile'
  });
});

// COMPLETA PROFILO - diventa candidato
app.post('/api/profile/complete', (req, res) => {
  const { userId, name } = req.body;
  
  // Trova l'utente
  const user = users.find(u => u.id === parseInt(userId));
  if (!user) {
    return res.status(404).json({ message: 'Utente non trovato' });
  }
  
  // Crea il candidato
  const newCandidate = {
    id: candidates.length + 1,
    userId: user.id,
    name: name || user.name,
    createdAt: new Date().toISOString()
  };
  
  candidates.push(newCandidate);
  
  res.json({
    success: true,
    message: 'Profilo completato! Sei ora un candidato Talfy',
    candidate: newCandidate,
    nextStep: 'dashboard'
  });
});

// LISTA CANDIDATI
app.get('/api/candidates', (req, res) => {
  res.json({
    candidates: candidates,
    total: candidates.length,
    message: candidates.length === 0 ? 'Nessun candidato ancora registrato' : `${candidates.length} candidati trovati`
  });
});

// CONTATORE
app.get('/api/candidates/stats/count', (req, res) => {
  res.json({
    total: candidates.length,
    status: candidates.length === 0 ? 'Aspettando il primo candidato...' : 'Candidati attivi'
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Talfy Backend running on port ${PORT}`);
  console.log(`📊 Candidati: ${candidates.length}`);
  console.log(`👥 Utenti: ${users.length}`);
});