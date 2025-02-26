from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.nlp import recognize_intent, generate_response
from app.database import save_interaction, get_recent_interactions
import logging
import os
import speech_recognition as sr
import pyttsx3
import io
import base64
import tempfile

app = FastAPI(title="AI Voice Assistant API")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

class TextInput(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Serve the frontend interface
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process-text/")
async def process_text(input: TextInput):
    """
    Process text input and return a response
    """
    logger.info(f"Received text: {input.text}")
    
    # Recognize intent
    intent = recognize_intent(input.text)
    
    # Generate response
    response = generate_response(intent, input.text)
    
    # Save interaction
    try:
        await save_interaction(input.text, intent, response)
    except Exception as e:
        logger.error(f"Error saving interaction: {e}")
    
    logger.info(f"Processed intent: {intent}")
    return {
        "intent": intent,
        "message": response["text"],
        "data": response["data"]
    }

@app.post("/process-audio/")
async def process_audio(audio_file: UploadFile = File(...)):
    """
    Process audio input, convert to text, and return a response
    """
    logger.info(f"Received audio file: {audio_file.filename}")
    
    # Save the uploaded file temporarily
    file_extension = os.path.splitext(audio_file.filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_audio:
        temp_audio_path = temp_audio.name
        content = await audio_file.read()
        temp_audio.write(content)
    
    # Convert audio to text
    text = ""
    audio_response_base64 = ""
    
    try:
        # Try using whisper for more robust speech recognition
        try:
            import whisper
            
            # Load the model (use "tiny" for faster processing, "base" for better accuracy)
            model = whisper.load_model("tiny")
            
            # Transcribe the audio
            result = model.transcribe(temp_audio_path)
            text = result["text"].strip()
            logger.info(f"Recognized text using Whisper: {text}")
            
        except ImportError:
            # Fallback to traditional speech recognition if whisper is not available
            logger.warning("Whisper not available, falling back to traditional speech recognition")
            
            # Convert to WAV if not already in WAV format
            wav_path = temp_audio_path
            if file_extension != '.wav':
                try:
                    import subprocess
                    wav_path = temp_audio_path + '.wav'
                    # Use ffmpeg to convert to WAV format with specific parameters
                    subprocess.run(
                        ['ffmpeg', '-i', temp_audio_path, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', wav_path],
                        check=True, capture_output=True
                    )
                    logger.info(f"Converted audio file to WAV format: {wav_path}")
                except Exception as e:
                    logger.error(f"Error converting audio format: {e}")
                    return JSONResponse(
                        status_code=400,
                        content={"error": f"Could not convert audio format: {str(e)}"}
                    )
            
            # Use traditional speech recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    logger.warning("Google Speech Recognition could not understand audio")
                    try:
                        # Try with whisper API if available
                        try:
                            text = recognizer.recognize_whisper(audio_data)
                            logger.info("Used Whisper API as fallback")
                        except (sr.UnknownValueError, AttributeError):
                            # Try with sphinx as last resort
                            text = recognizer.recognize_sphinx(audio_data)
                            logger.info("Used Sphinx as fallback")
                    except:
                        logger.error("All speech recognition attempts failed")
                        raise
                
                logger.info(f"Recognized text from audio: {text}")
    except Exception as e:
        logger.error(f"Error recognizing speech: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": f"Could not recognize speech in the audio file: {str(e)}"}
        )
    finally:
        # Clean up the temporary files
        try:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
            if 'wav_path' in locals() and wav_path != temp_audio_path and os.path.exists(wav_path):
                os.unlink(wav_path)
        except Exception as e:
            logger.error(f"Error deleting temporary audio file: {e}")
    
    if not text:
        return JSONResponse(
            status_code=400,
            content={"error": "No speech detected in the audio file"}
        )
    
    # Process the recognized text
    intent = recognize_intent(text)
    response = generate_response(intent, text)
    
    # Save interaction
    try:
        await save_interaction(text, intent, response)
    except Exception as e:
        logger.error(f"Error saving interaction: {e}")
    
    # Generate speech response
    try:
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_response:
            temp_response_path = temp_response.name
        
        engine.save_to_file(response["text"], temp_response_path)
        engine.runAndWait()
        
        with open(temp_response_path, "rb") as audio_file:
            audio_response_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
        
        # Only try to delete if the file exists
        if os.path.exists(temp_response_path):
            os.unlink(temp_response_path)
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
    
    return {
        "text": text,
        "intent": intent,
        "message": response["text"],
        "data": response["data"],
        "audio_response": audio_response_base64
    }

@app.get("/history/")
async def get_history(limit: int = 10):
    """
    Get recent interaction history
    """
    try:
        history = await get_recent_interactions(limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving interaction history")