const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// قاعدة بيانات SQLite
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) console.error(err.message);
    else console.log('Connected to SQLite database.');
});

// إنشاء الجداول إذا لم تكن موجودة
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        name TEXT,
        points INTEGER DEFAULT 0,
        referral_code TEXT UNIQUE,
        wallet_address TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task_name TEXT,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )`);
});

// تسجيل مستخدم جديد أو استرجاعه
app.post('/api/user', (req, res) => {
    const { telegram_id, name } = req.body;
    db.get("SELECT * FROM users WHERE telegram_id = ?", [telegram_id], (err, row) => {
        if (err) return res.status(500).send(err.message);
        if (row) res.json(row);
        else {
            const referral_code = 'SYRX-' + Math.random().toString(36).substring(2,8).toUpperCase();
            db.run("INSERT INTO users (telegram_id, name, referral_code) VALUES (?, ?, ?)", [telegram_id, name, referral_code], function(err){
                if(err) return res.status(500).send(err.message);
                db.get("SELECT * FROM users WHERE id = ?", [this.lastID], (err2, newUser)=>{
                    res.json(newUser);
                });
            });
        }
    });
});

// تحديث النقاط أو المحفظة
app.post('/api/update', (req,res)=>{
    const { telegram_id, points, wallet_address } = req.body;
    db.run("UPDATE users SET points = ?, wallet_address = ? WHERE telegram_id = ?", [points, wallet_address, telegram_id], function(err){
        if(err) return res.status(500).send(err.message);
        res.json({success:true});
    });
});

// تسجيل اكتمال مهمة
app.post('/api/complete-task', (req,res)=>{
    const { telegram_id, task_name, reward } = req.body;
    db.get("SELECT id, points FROM users WHERE telegram_id = ?", [telegram_id], (err,row)=>{
        if(err) return res.status(500).send(err.message);
        if(!row) return res.status(404).send("User not found");
        db.run("INSERT INTO tasks (user_id, task_name, completed) VALUES (?, ?, 1)", [row.id, task_name], (err2)=>{
            if(err2) return res.status(500).send(err2.message);
            const newPoints = row.points + reward;
            db.run("UPDATE users SET points = ? WHERE id = ?", [newPoints, row.id], (err3)=>{
                if(err3) return res.status(500).send(err3.message);
                res.json({success:true, points:newPoints});
            });
        });
    });
});

app.listen(port, ()=>console.log(`Server running on port ${port}`));
