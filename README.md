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

## 🧬 Database & Auth (Supabase)

To enable API keys and the 50 calls/day limit, you'll need a **Supabase** project:

1.  **Run SQL**: Open your Supabase SQL Editor and run the content of `[supabase_setup.sql](file:///home/poser/Documents/github_work/VaaS/supabase_setup.sql)`.
2.  **Environment Setup**: Fill in your `[vaas/.env](file:///home/poser/Documents/github_work/VaaS/vaas/.env)` with your Supabase URL and **Service Role Key** (for server-side usage tracking).
3.  **Website Setup**: Open `[web/index.html](file:///home/poser/Documents/github_work/VaaS/web/index.html)` and replace the `SUPABASE_URL` and `SUPABASE_ANON_KEY` variables with your project credentials.

---

## 🌐 Dashboard & User Signup

We've added a premium website in `web/index.html`. Users can:
- **Sign up/Login** (using Supabase Auth).
- **Generate API Keys**.
- **Monitor Usage** (see their current count out of 50).

To serve the website:
```bash
# Example using python's built-in server
python -m http.server 3000 --directory web
```
Then visit `http://localhost:3000`.

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
