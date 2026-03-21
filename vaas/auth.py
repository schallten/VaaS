import sqlite3
import os
import uuid
from datetime import date
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext

# Database Setup
DB_PATH = "vaas.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB on start
conn = get_db()
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS api_keys 
                  (id TEXT PRIMARY KEY, user_id TEXT, key TEXT UNIQUE, 
                   FOREIGN KEY(user_id) REFERENCES users(id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS usage_logs 
                  (id TEXT PRIMARY KEY, api_key_id TEXT, usage_date TEXT, count INTEGER,
                   UNIQUE(api_key_id, usage_date),
                   FOREIGN KEY(api_key_id) REFERENCES api_keys(id))''')
conn.commit()

# Password Hashing
# Switching to pbkdf2_sha256 because bcrypt causes version conflicts with recent passlib
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# API Key Validation Dependency
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key missing")

    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Check if key exists
    cursor.execute("SELECT * FROM api_keys WHERE key = ?", (api_key,))
    key_record = cursor.fetchone()
    if not key_record:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    api_key_id = key_record["id"]
    today = str(date.today())

    # 2. Daily Usage limit (50)
    cursor.execute("SELECT count FROM usage_logs WHERE api_key_id = ? AND usage_date = ?", (api_key_id, today))
    usage_record = cursor.fetchone()
    
    current_count = 0
    if usage_record:
        current_count = usage_record["count"]

    if current_count >= 50:
        raise HTTPException(status_code=429, detail="Daily usage limit (50) exceeded")

    # 3. Increment Count
    if usage_record:
        cursor.execute("UPDATE usage_logs SET count = count + 1 WHERE api_key_id = ? AND usage_date = ?", (api_key_id, today))
    else:
        cursor.execute("INSERT INTO usage_logs (id, api_key_id, usage_date, count) VALUES (?, ?, ?, ?)", 
                       (str(uuid.uuid4()), api_key_id, today, 1))
    
    conn.commit()
    return key_record["user_id"]
