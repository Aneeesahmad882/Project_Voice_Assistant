# AI Voice Assistant

This project is a simple AI voice assistant backend using FastAPI.

## Features

- Accepts text input to simulate voice input.
- Basic NLP processing for intent recognition.
- Stores interactions in MongoDB.
- Dockerized for easy deployment.

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd voice-assistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Run with Docker**:
   ```bash
   docker compose up --build
   ```
