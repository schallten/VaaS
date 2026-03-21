from fastapi import FastAPI, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import edge_tts
import uuid
import os
from datetime import date
from auth import validate_api_key, get_db, hash_password, verify_password

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load lightweight whisper model
model = WhisperModel("tiny", compute_type="int8")

# Global voices for hackathons
VOICES = {
    # English
    "en_us_ava": "en-US-AvaNeural",
    "en_us_andrew": "en-US-AndrewNeural",
    "en_gb_libby": "en-GB-LibbyNeural",
    "en_in_neerja": "en-IN-NeerjaNeural",
    "hi_in_madhur": "hi-IN-MadhurNeural",
    # Spanish
    "es_es_alvaro": "es-ES-AlvaroNeural",
    "es_mx_dalia": "es-MX-DaliaNeural",
    # German
    "de_de_katja": "de-DE-KatjaNeural",
    # Japanese
    "ja_jp_nanami": "ja-JP-NanamiNeural",
    # Korean
    "ko_kr_sunhi": "ko-KR-SunHiNeural",
    # Chinese
    "zh_cn_xiaoxiao": "zh-CN-XiaoxiaoNeural",
    # Arabic
    "ar_sa_hamed": "ar-SA-HamedNeural"
}

# Cleanup helper
def cleanup_temp_file(path: str):
    if os.path.exists(path):
        os.remove(path)

# Health check
@app.get("/")
def home():
    return {"message": "VaaS for Hackathons is live 🚀"}

# Auth endpoints
@app.post("/auth/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    try:
        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(password)
        cursor.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)", 
                       (user_id, username, hashed_pwd))
        conn.commit()
        return {"id": user_id, "username": username}
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return JSONResponse(status_code=400, content={"error": "Username already exists"})
        return JSONResponse(status_code=500, content={"error": "Internal Error"})

@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user and verify_password(password, user["password_hash"]):
        return {"id": user["id"], "username": user["username"]}
    return JSONResponse(status_code=401, content={"error": "Invalid username or password"})

@app.get("/auth/me")
async def get_dashboard_info(user_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_keys WHERE user_id = ?", (user_id,))
    key_record = cursor.fetchone()
    count = 0
    if key_record:
        today = str(date.today())
        cursor.execute("SELECT count FROM usage_logs WHERE api_key_id = ? AND usage_date = ?", (key_record["id"], today))
        usage_record = cursor.fetchone()
        if usage_record:
            count = usage_record["count"]
    return {"api_key": key_record["key"] if key_record else None, "usage": count}

@app.post("/auth/generate-key")
async def generate_key(user_id: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    new_key = "vaas_" + uuid.uuid4().hex
    cursor.execute("SELECT id FROM api_keys WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("UPDATE api_keys SET key = ? WHERE user_id = ?", (new_key, user_id))
    else:
        cursor.execute("INSERT INTO api_keys (id, user_id, key) VALUES (?, ?, ?)", (str(uuid.uuid4()), user_id, new_key))
    conn.commit()
    return {"api_key": new_key}

# Speech → Text
@app.post("/stt")
async def stt(background_tasks: BackgroundTasks, file: UploadFile = File(...), user_id: str = Depends(validate_api_key)):
    try:
        filename = f"temp_{uuid.uuid4()}.wav"
        with open(filename, "wb") as f:
            f.write(await file.read())
        segments, _ = model.transcribe(filename)
        text = " ".join([seg.text for seg in segments])
        background_tasks.add_task(cleanup_temp_file, filename)
        return {"text": text.strip()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Text → Speech
@app.post("/tts")
async def tts(background_tasks: BackgroundTasks, text: str = Form(...), voice: str = Form("en_us_ava"), user_id: str = Depends(validate_api_key)):
    try:
        if voice not in VOICES:
            return JSONResponse(status_code=400, content={"error": f"Invalid voice"})
        filename = f"tts_{uuid.uuid4()}.mp3"
        communicate = edge_tts.Communicate(text, VOICES[voice])
        await communicate.save(filename)
        return FileResponse(filename, media_type="audio/mpeg", background=background_tasks.add_task(cleanup_temp_file, filename))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
