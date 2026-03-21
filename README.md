# 🎙️ VaaS — Voice as a Service

A lightweight voice processing API built with **FastAPI**, **Faster-Whisper**, and **Edge-TTS**.

---

## 🚀 API Documentation

### 1. Health Check
Checks if the server is running.

*   **Endpoint:** `GET /`
*   **Response:** `{"message":"VaaS is running 🚀"}`
*   **Example:**
    ```bash
    curl http://localhost:8000/
    ```

### 2. Get Available Voices
Returns a list of supported voice IDs.

*   **Endpoint:** `GET /voices`
*   **Response:** `{"voices": ["female_us", "male_us", "hindi", ... ]}`
*   **Example:**
    ```bash
    curl http://localhost:8000/voices
    ```

### 3. Text-to-Speech (TTS)
Converts text into an MP3 audio file.

*   **Endpoint:** `POST /tts`
*   **Parameters (Form Data):**
    *   `text` (string): The text you want to convert.
    *   `voice` (string, optional): One of the voice IDs from `/voices` (default: `female_us`).
*   **Response:** `audio/mpeg` (downloadable MP3 file).
*   **Example:**
    ```bash
    curl -X POST "http://localhost:8000/tts" \
      -F "text=Hello, this is a test of VaaS." \
      -F "voice=male_india" \
      --output test_voice.mp3
    ```

### 4. Speech-to-Text (STT)
Transcribes audio into text.

*   **Endpoint:** `POST /stt`
*   **Parameters (Form Data):**
    *   `file` (file): Any audio file supported by Whisper (WAV, MP3, etc.).
*   **Response:** `{"text": "Extracted text goes here"}`
*   **Example:**
    ```bash
    curl -X POST "http://localhost:8000/stt" \
      -F "file=@test_voice.mp3"
    ```

---

## 🛠️ Local Setup (Quick Recap)

If you need to restart the server:

1.  **Navigate to the folder:**
    ```bash
    cd vaas
    ```
2.  **Activate environment:**
    ```bash
    source .venv/bin/activate
    ```
3.  **Run with Uvicorn:**
    ```bash
    uvicorn main:app --reload
    ```
