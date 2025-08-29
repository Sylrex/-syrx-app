-- إنشاء جدول المستخدمين إذا لم يكن موجودًا
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL DEFAULT 'Anonymous',
    points INTEGER DEFAULT 0,
    referrals INTEGER DEFAULT 0
);

-- إنشاء جدول الإحالات إذا لم يكن موجودًا
CREATE TABLE IF NOT EXISTS referrals (
    id SERIAL PRIMARY KEY,
    referrer_id VARCHAR(255) NOT NULL,
    referred_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(referrer_id, referred_id),
    FOREIGN KEY (referrer_id) REFERENCES users(user_id),
    FOREIGN KEY (referred_id) REFERENCES users(user_id)
);
