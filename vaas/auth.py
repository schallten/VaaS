import os
import uuid
import asyncio
from datetime import date
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from fastapi import Header, HTTPException, Depends
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client.vaas_db

users_col = db.users
keys_col = db.api_keys
usage_col = db.usage_logs

# Password Hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# API Key Validation (Middleware-ready)
async def validate_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-KEY header missing")
    
    # Check key in MongoDB
    key_record = await keys_col.find_one({"key": x_api_key})
    if not key_record:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Check Usage (50/day limit)
    today = str(date.today())
    usage_entry = await usage_col.find_one({
        "api_key_id": key_record["_id"],
        "usage_date": today
    })

    if usage_entry and usage_entry["count"] >= 50:
        raise HTTPException(status_code=429, detail="Daily usage limit (50) reached")

    # Update usage
    if usage_entry:
        await usage_col.update_one(
            {"_id": usage_entry["_id"]},
            {"$inc": {"count": 1}}
        )
    else:
        await usage_col.insert_one({
            "api_key_id": key_record["_id"],
            "usage_date": today,
            "count": 1
        })

    return key_record["user_id"]
