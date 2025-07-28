// server.js
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// ✅ Mock Database in memoria
let candidates = [];
let companies = [];

// ✅ Rotta di test
app.get('/', (req, res) => {
  res.json({ message: 'Talfy Backend Mock is running!' });
});

// ✅ Registrazione utente
app.post('/api/register', (req, res) => {
  const { email, password, userType } = req.body;

  if (!email || !password || !userType) {
    return res.status(400).json({ message: 'Missing fields' });
  }

  const newUser = {
    id: Date.now(),
    email,
    password,
    userType,
    profileCompleted: false
  };

  if (userType === 'candidate') {
    candidates.push(newUser);
  } else if (userType === 'company') {
    companies.push(newUser);
  }

  res.json({ message: 'User registered successfully', user: newUser });
});

// ✅ Login
app.post('/api/login', (req, res) => {
  const { email, password } = req.body;

  const user = [...candidates, ...companies].find(u => u.email === email && u.password === password);

  if (!user) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }

  res.json({ message: 'Login successful', user });
});

// ✅ Completa profilo (mock)
app.post('/api/complete-profile', (req, res) => {
  const { userId, profileData } = req.body;

  let user = candidates.find(c => c.id === userId) || companies.find(c => c.id === userId);
  if (!user) {
    return res.status(404).json({ message: 'User not found' });
  }

  user.profileCompleted = true;
  user.profileData = profileData;

  res.json({ message: 'Profile completed', user });
});

// ✅ Contatori
app.get('/api/counters', (req, res) => {
  res.json({
    candidates: candidates.length,
    companies: companies.length
  });
});

// Avvio server
app.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}`);
});
