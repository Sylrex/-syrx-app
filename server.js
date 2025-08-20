const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST,      // ضع بيانات Render
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  port: 5432,
});

async function initDB() {
  const client = await pool.connect();
  try {
    // جدول المستخدمين
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id TEXT UNIQUE,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        photo_url TEXT,
        points INTEGER DEFAULT 0,
        referral_code TEXT UNIQUE,
        referred_by TEXT,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `);

    // جدول المهام المكتملة
    await client.query(`
      CREATE TABLE IF NOT EXISTS user_tasks (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(id),
        task_id TEXT,
        completed BOOLEAN DEFAULT FALSE,
        completed_at TIMESTAMP
      );
    `);

    // جدول Claim كل 6 ساعات
    await client.query(`
      CREATE TABLE IF NOT EXISTS user_claims (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(id),
        last_claim_at TIMESTAMP
      );
    `);

    console.log("✅ Tables created or already exist.");
  } catch (err) {
    console.error("Error creating tables:", err);
  } finally {
    client.release();
  }
}

// استدعاء الدالة عند بدء السيرفر
initDB();

// هنا يمكن إضافة باقي كود السيرفر (Express أو Fastify) للتعامل مع Telegram WebApp
