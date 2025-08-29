-- حذف الجداول إذا كانت موجودة (اختياري، لإعادة الإنشاء)
DROP TABLE IF EXISTS referrals;
DROP TABLE IF EXISTS users;

-- جدول المستخدمين
CREATE TABLE users (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    points INTEGER DEFAULT 0,
    referrals INTEGER DEFAULT 0
);

-- جدول الإحالات
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_id VARCHAR(255) NOT NULL,
    referred_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(referrer_id, referred_id),
    FOREIGN KEY (referrer_id) REFERENCES users(user_id),
    FOREIGN KEY (referred_id) REFERENCES users(user_id)
);
