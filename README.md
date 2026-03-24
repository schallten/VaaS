# 🎙️ VaaS — Voice as a Service

![Status](https://img.shields.io/badge/Status-Live-success)
![Limit](https://img.shields.io/badge/Limit-100%20uses%2Fday-blue)
![License](https://img.shields.io/badge/License-Apache_2.0-orange)

VaaS is a lightweight, open-source voice processing API built for hackathons and quick prototypes. Get high-quality Speech-to-Text and Text-to-Speech without the headache of cloud billing or complex setups.

## 🚀 [Try the Live Dashboard](https://vaas-production-c42f.up.railway.app)

---

### 🕹️ Features
- **⚡ 0 Sec Setup**: Plug and play with a simple REST API.
- **🌍 Multilingual**: Support for 10+ languages (Spanish, German, Japanese, etc.).
- **🎙️ Whisper Precise**: STT powered by Faster-Whisper.
- **🔊 Natural Voices**: TTS powered by premium Microsoft Edge-TTS.
- **🛡️ Privacy Focused**: All processing is handled on your own Python server.

---

### 🤖 AI Agent Integration (Fast-Track)
*Paste this into your AI coding assistant (like Antigravity or ChatGPT) to immediately teach it the VaaS API:*

```text
The VaaS API is a Voice processing service.
Base URL: https://vaas-production-c42f.up.railway.app
Authentication: Include your key in the 'X-API-KEY' header.

1. Text-To-Speech (TTS):
   - Endpoint: POST /tts
   - Content-Type: multipart/form-data
   - Params: 'text' (string), 'voice' (string, e.g. 'en_us_ava'), 'language' (string, e.g. 'en', 'es').
   - Note: If 'language' is provided without 'voice', a default voice for that language is used.
   - Return: MP3 Audio file.

2. Speech-To-Text (STT):
   - Endpoint: POST /stt
   - Content-Type: multipart/form-data
   - Params: 'file' (audio file/blob), 'language' (string, e.g. 'en', 'hi').
   - Note: 'language' is optional but improves accuracy. Whisper auto-detects by default.
   - Return: JSON { "text": "transcription" }.
```

---

### 🛠️ API Documentation (Detailed)

#### 1. POST `/tts` (Text-to-Speech)
Generates an MP3 file from text.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `string` | Yes | The text to convert to speech. |
| `voice` | `string` | No | ID of the voice to use (e.g. `en_us_ava`). |
| `language` | `string` | No | Language code (e.g. `en`, `es`, `hi`) to use a default voice. |

**Header:** `X-API-KEY: your_api_key`

**Example:**
```bash
curl -X POST "https://vaas-production-c42f.up.railway.app/tts" \
  -H "X-API-KEY: your_key" \
  -F "text=Hello World" \
  -F "language=en" \
  --output voice.mp3
```

#### 2. POST `/stt` (Speech-to-Text)
Transcribes an audio file into text.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file` | `file` | Yes | The audio file (WAV, MP3, WEBM). |
| `language` | `string` | No | Explicit language code for transcription (e.g. `en`, `es`). |

**Header:** `X-API-KEY: your_api_key`

**Example:**
```bash
curl -X POST "https://vaas-production-c42f.up.railway.app/stt" \
  -H "X-API-KEY: your_key" \
  -F "file=@voice.mp3" \
  -F "language=en"
```

---

### 📦 Local Setup
If you want to run VaaS yourself:
```bash
# Clone the repo
git clone https://github.com/schallten/vaas
cd vaas

# Setup environment
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Run!
uvicorn vaas.main:app --reload
```

---
Built with ❤️ for the developer community. Open source under Apache License 2.0.
