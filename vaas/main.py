from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from faster_whisper import WhisperModel
import edge_tts
import uuid
import os

app = FastAPI()

# Load lightweight whisper model
model = WhisperModel("tiny", compute_type="int8")

# Voice options (controlled)
VOICES = {
    "female_us": "en-US-AriaNeural",
    "male_us": "en-US-GuyNeural",
    "female_india": "en-IN-NeerjaNeural",
    "male_india": "en-IN-PrabhatNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_au": "en-AU-NatashaNeural",
    "hindi": "hi-IN-MadhurNeural"
}


# Health check
@app.get("/")
def home():
    return {"message": "VaaS is running 🚀"}


# List voices
@app.get("/voices")
def get_voices():
    return {"voices": list(VOICES.keys())}


# Speech → Text
@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    try:
        filename = f"temp_{uuid.uuid4()}.wav"

        # Save file
        with open(filename, "wb") as f:
            f.write(await file.read())

        # Transcribe
        segments, _ = model.transcribe(filename)
        text = " ".join([seg.text for seg in segments])

        os.remove(filename)

        return {"text": text.strip()}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Text → Speech
@app.post("/tts")
async def tts(text: str = Form(...), voice: str = Form("female_us")):
    try:
        if voice not in VOICES:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid voice. Use /voices"}
            )

        filename = f"tts_{uuid.uuid4()}.mp3"

        communicate = edge_tts.Communicate(text, VOICES[voice])
        await communicate.save(filename)

        return FileResponse(filename, media_type="audio/mpeg")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
