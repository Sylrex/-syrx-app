const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// PostgreSQL connection
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

// Create users table
pool.query(`
    CREATE TABLE IF NOT EXISTS users (
        userId TEXT PRIMARY KEY,
        points INTEGER DEFAULT 0,
        lastLogin DATE,
        walletAddress TEXT,
        referrals INTEGER DEFAULT 0
    )
`);

// Get user points
app.get('/api/points/:userId', async (req, res) => {
    const { userId } = req.params;
    const result = await pool.query('SELECT points FROM users WHERE userId = $1', [userId]);
    if (result.rows.length === 0) {
        await pool.query('INSERT INTO users (userId, points) VALUES ($1, 0)', [userId]);
        return res.json({ points: 0 });
    }
    res.json({ points: result.rows[0].points });
});

// Daily login
app.get('/api/daily-login/:userId', async (req, res) => {
    const { userId } = req.params;
    const result = await pool.query('SELECT lastLogin FROM users WHERE userId = $1', [userId]);
    const today = new Date().toISOString().split('T')[0];
    if (result.rows.length === 0) {
        await pool.query('INSERT INTO users (userId, points, lastLogin) VALUES ($1, 0, $2)', [userId, today]);
        return res.json({ canLogin: true });
    }
    const lastLogin = result.rows[0].lastLogin;
    res.json({ canLogin: !lastLogin || lastLogin !== today });
});
app.post('/api/daily-login/:userId', async (req, res) => {
    const { userId } = req.params;
    const today = new Date().toISOString().split('T')[0];
    await pool.query('UPDATE users SET points = points + 10, lastLogin = $1 WHERE userId = $2', [today, userId]);
    const result = await pool.query('SELECT points FROM users WHERE userId = $1', [userId]);
    res.json({ success: true, points: result.rows[0].points });
});

// Tasks
app.post('/api/task/:userId/:task', async (req, res) => {
    const { userId, task } = req.params;
    await pool.query('UPDATE users SET points = points + 5 WHERE userId = $1', [userId]);
    const result = await pool.query('SELECT points FROM users WHERE userId = $1', [userId]);
    res.json({ success: true, points: result.rows[0].points });
});

// Wallet connection
app.post('/api/wallet/:userId', async (req, res) => {
    const { userId } = req.params;
    const { walletAddress } = req.body;
    await pool.query('UPDATE users SET walletAddress = $1, points = points + 5 WHERE userId = $2', [walletAddress, userId]);
    res.json({ success: true });
});

// Referrals
app.post('/api/referral/:userId', async (req, res) => {
    const { userId } = req.params;
    await pool.query('UPDATE users SET referrals = referrals + 1, points = points + 10 WHERE userId = $1', [userId]);
    res.json({ success: true });
});

// Leaderboard
app.get('/api/leaderboard', async (req, res) => {
    const result = await pool.query('SELECT userId, points FROM users ORDER BY points DESC LIMIT 100');
    res.json(result.rows);
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
