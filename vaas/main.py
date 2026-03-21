from fastapi import FastAPI, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel
import edge_tts
import uuid
import os
from datetime import date
from vaas.auth import validate_api_key, hash_password, verify_password, users_col, keys_col, usage_col

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

# Global voices
VOICES = {
    "en_us_ava": "en-US-AvaNeural",
    "en_us_andrew": "en-US-AndrewNeural",
    "en_in_neerja": "en-IN-NeerjaNeural",
    "hi_in_madhur": "hi-IN-MadhurNeural",
    "es_mx_dalia": "es-MX-DaliaNeural",
    "es_es_alvaro": "es-ES-AlvaroNeural",
    "de_de_katja": "de-DE-KatjaNeural",
    "ja_jp_nanami": "ja-JP-NanamiNeural",
    "ko_kr_sunhi": "ko-KR-SunHiNeural",
    "zh_cn_xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "ar_sa_hamed": "ar-SA-HamedNeural"
}

# Cleanup helper
def cleanup_temp_file(path: str):
    if os.path.exists(path):
        os.remove(path)

# Auth endpoints
@app.post("/auth/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    try:
        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(password)
        existing = await users_col.find_one({"username": username})
        if existing:
            return JSONResponse(status_code=400, content={"error": "Username already exists"})
        await users_col.insert_one({"id": user_id, "username": username, "password_hash": hashed_pwd})
        return {"id": user_id, "username": username}
    except Exception:
        return JSONResponse(status_code=500, content={"error": "Internal Error"})

@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = await users_col.find_one({"username": username})
    if user and verify_password(password, user["password_hash"]):
        return {"id": user["id"], "username": user["username"]}
    return JSONResponse(status_code=401, content={"error": "Invalid login"})

@app.get("/auth/me")
async def get_dashboard_info(user_id: str):
    key_record = await keys_col.find_one({"user_id": user_id})
    count = 0
    if key_record:
        today = str(date.today())
        usage_record = await usage_col.find_one({"api_key_id": key_record["_id"], "usage_date": today})
        if usage_record: count = usage_record["count"]
    return {"api_key": key_record["key"] if key_record else None, "usage": count}

# Health check
@app.get("/health")
def health():
    return {"status": "VaaS is healthy 🚀"}

@app.post("/auth/generate-key")
async def generate_key(user_id: str = Form(...)):
    new_key = "vaas_" + uuid.uuid4().hex
    existing = await keys_col.find_one({"user_id": user_id})
    if existing: await keys_col.update_one({"user_id": user_id}, {"$set": {"key": new_key}})
    else: await keys_col.insert_one({"id": str(uuid.uuid4()), "user_id": user_id, "key": new_key})
    return {"api_key": new_key}

# STT / TTS
@app.post("/stt")
async def stt(background_tasks: BackgroundTasks, file: UploadFile = File(...), user_id: str = Depends(validate_api_key)):
    try:
        filename = f"temp_{uuid.uuid4()}.wav"
        with open(filename, "wb") as f: f.write(await file.read())
        segments, _ = model.transcribe(filename)
        text = " ".join([seg.text for seg in segments])
        background_tasks.add_task(cleanup_temp_file, filename)
        return {"text": text.strip()}
    except Exception as e: return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/tts")
async def tts(background_tasks: BackgroundTasks, text: str = Form(...), voice: str = Form("en_us_ava"), user_id: str = Depends(validate_api_key)):
    try:
        if voice not in VOICES: return JSONResponse(status_code=400, content={"error": "Invalid voice"})
        filename = f"tts_{uuid.uuid4()}.mp3"
        communicate = edge_tts.Communicate(text, VOICES[voice])
        await communicate.save(filename)
        return FileResponse(filename, media_type="audio/mpeg", background=background_tasks.add_task(cleanup_temp_file, filename))
    except Exception as e: return JSONResponse(status_code=500, content={"error": str(e)})

# --- SERVE FRONTEND ---
# Serve the web/ folder at the root
if os.path.exists("web"):
    app.mount("/", StaticFiles(directory="web", html=True), name="web")
