# 🎙️ VaaS — Voice as a Service

![Status](https://img.shields.io/badge/Status-Live-success)
![Limit](https://img.shields.io/badge/Limit-100%20uses%2Fday-blue)
![License](https://img.shields.io/badge/License-MIT-purple)

VaaS is a lightweight, open-source voice processing API built for hackathons and quick prototypes. Get high-quality Speech-to-Text and Text-to-Speech without the headache of cloud billing or complex setups.

## 🚀 [Try the Live Dashboard](https://vaas-production-c42f.up.railway.app)

---

### 🕹️ Features
- **⚡ 0 Sec Setup**: Plug and play with a simple REST API.
- **🌍 Multilingual**: Support for 10+ languages (Spanish, German, Japanese, etc.).
- **🎙️ Whisper Precise**: STT powered by Faster-Whisper.
- **🔊 Natural Voices**: TTS powered by premium Microsoft Edge-TTS.
- **🛡️ Privacy Focused**: All processing is handled on your own Python server.

### 🛠️ API Usage
VaaS is designed to be dead simple for teams. Once you have a key from the dashboard:

#### 🔊 Text-to-Speech (TTS)
```bash
curl -X POST "https://vaas-production-c42f.up.railway.app/tts" \
  -H "X-API-KEY: your_key_here" \
  -F "text=Hello World" \
  -F "voice=en_us_ava" \
  --output voice.mp3
```

#### 🎙️ Speech-to-Text (STT)
```bash
curl -X POST "https://vaas-production-c42f.up.railway.app/stt" \
  -H "X-API-KEY: your_key_here" \
  -F "file=@voice.mp3"
```

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
Built with ❤️ for the developer community. Open source under MIT.
