from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, Response, FileResponse
import requests
import socket
import subprocess
import time
import whisper
import pyttsx3
import os
import tempfile
from pathlib import Path

app = FastAPI()

# Initialize Whisper model (small by default, can use 'base', 'medium', 'large')
whisper_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        print("Loading Whisper model...")
        whisper_model = whisper.load_model("base")
    return whisper_model

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Velocidad del habla
tts_engine.setProperty('volume', 1.0)  # Volumen máximo

FAST = "http://127.0.0.1:8081"
SMART = "http://127.0.0.1:8082"
VISION = "http://127.0.0.1:8083"

started_processes = []


def server_alive(url):
    try:
        r = requests.get(f"{url}/health", timeout=1)
        if r.status_code < 500:
            return True
    except Exception:
        pass

    try:
        r = requests.get(f"{url}/v1/models", timeout=1)
        if r.status_code < 500:
            return True
    except Exception:
        pass

    try:
        host = url.split("://", 1)[-1].split(":")[0]
        port = int(url.rsplit(":", 1)[-1])
        with socket.create_connection((host, port), timeout=1):
            return True
    except Exception:
        pass

    return False


def start_server(script):
    proc = subprocess.Popen(
        ["bash", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    started_processes.append(proc)
    return proc


def ensure_server(url, script):
    if server_alive(url):
        return

    print(f"Starting server: {script}")

    proc = start_server(script)

    for i in range(120):
        if proc.poll() is not None:
            raise RuntimeError(f"Server process exited early with code {proc.poll()}")

        if server_alive(url):
            print("Server ready")
            return

        time.sleep(1)

    raise RuntimeError("Server failed to start within 120 seconds")


@app.on_event("startup")
async def startup_event():
    ensure_server(FAST, "./run-fast.sh")


@app.on_event("shutdown")
async def shutdown_event():
    for proc in started_processes:
        if proc.poll() is None:
            proc.terminate()

    deadline = time.time() + 5
    for proc in started_processes:
        if proc.poll() is None:
            try:
                proc.wait(timeout=max(0, deadline - time.time()))
            except subprocess.TimeoutExpired:
                proc.kill()


def is_complex(prompt):
    keywords = [
        "analyze",
        "architecture",
        "debug",
        "compare",
        "optimize",
        "reason"
    ]

    if len(prompt) > 200:
        return True

    if any(k in prompt.lower() for k in keywords):
        return True

    return False

@app.get("/v1/models")
async def models():

  return {
    "object": "list",
    "data": [
      {
        "id": "gemma2-fast",
        "object": "model",
        "owned_by": "local"
      },
      {
        "id": "gemma4-smart",
        "object": "model",
        "owned_by": "local"
      },
      {
        "id": "qwen2vl-vision",
        "object": "model",
        "owned_by": "local"
      }
    ]
  }


@app.get("/v1/models/api/tags")
async def tags():

  return {
    "object": "list",
    "data": [
      {
        "id": "fast",
        "object": "model_tag"
      },
      {
        "id": "smart",
        "object": "model_tag"
      },
      {
        "id": "vision",
        "object": "model_tag"
      }
    ]
  }

@app.post("/v1/chat/completions")
async def route(req: dict):

    messages = req.get("messages", [])

    last = str(messages[-1])

    has_image = "image_url" in last
    model = req.get("model", "")

    print(f"Routing request: model={model}, has_image={has_image}, is_complex={is_complex(last)}")

    if model == "qwen2vl-vision":
        ensure_server(VISION, "./run-vision.sh")
        target = f"{VISION}/v1/chat/completions"

    elif is_complex(last):
        try:
            ensure_server(SMART, "./run-smart.sh")
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc))
        target = f"{SMART}/v1/chat/completions"

    else:
        ensure_server(FAST, "./run-fast.sh")
        target = f"{FAST}/v1/chat/completions"

    try:
        r = requests.post(target, json=req, timeout=30)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}")

    content_type = r.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            return JSONResponse(status_code=r.status_code, content=r.json())
        except ValueError:
            return Response(content=r.text or "", status_code=r.status_code, media_type="text/plain")

    return Response(
        content=r.content or r.text or "",
        status_code=r.status_code,
        media_type=content_type.split(";")[0] if content_type else "text/plain"
    )


@app.post("/v1/audio/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio file to text using Whisper"""
    try:
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Transcribir con Whisper
            model = get_whisper_model()
            result = model.transcribe(tmp_path, language="es")  # Español por defecto
            
            return {
                "text": result["text"],
                "language": result.get("language", "es")
            }
        finally:
            # Limpiar archivo temporal
            os.unlink(tmp_path)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error transcribing audio: {str(e)}")


@app.post("/v1/audio/speak")
async def text_to_speech(req: dict):
    """Convert text to speech"""
    try:
        text = req.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Generar archivo de audio temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Convertir texto a voz
            tts_engine.save_to_file(text, tmp_path)
            tts_engine.runAndWait()
            
            # Retornar archivo de audio
            return FileResponse(
                tmp_path,
                media_type="audio/mpeg",
                filename="speech.mp3"
            )
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating speech: {str(e)}")


@app.post("/v1/chat/audio")
async def chat_with_voice(
    audio_file: UploadFile = File(...),
    model: str = ""
):
    """Complete voice-to-voice conversation: Audio -> Text -> LLM -> Text -> Audio"""
    try:
        # Step 1: Transcribir audio a texto
        print(f"Transcribing audio...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            whisper_model = get_whisper_model()
            transcript = whisper_model.transcribe(tmp_path, language="es")
            user_text = transcript["text"]
            print(f"Transcribed: {user_text}")
        finally:
            os.unlink(tmp_path)
        
        # Step 2: Enviar al LLM
        print(f"Routing to LLM with model: {model}")
        llm_request = {
            "messages": [{"role": "user", "content": user_text}],
            "model": model or "gemma2-fast"
        }
        
        llm_response = await route(llm_request)
        
        # Extraer el texto de la respuesta
        if hasattr(llm_response, "body"):
            import json
            response_json = json.loads(llm_response.body)
        else:
            response_json = llm_response
        
        assistant_text = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"LLM response: {assistant_text}")
        
        # Step 3: Convertir respuesta a audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_audio_path = tmp_file.name
        
        try:
            tts_engine.save_to_file(assistant_text, tmp_audio_path)
            tts_engine.runAndWait()
            
            # Retornar JSON con texto y URL/contenido de audio
            with open(tmp_audio_path, "rb") as f:
                audio_bytes = f.read()
            
            return {
                "user_input": user_text,
                "assistant_response": assistant_text,
                "audio": audio_bytes.hex(),  # Convertir a hex para JSON
                "model_used": model or "gemma2-fast"
            }
        finally:
            if os.path.exists(tmp_audio_path):
                os.unlink(tmp_audio_path)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in voice chat: {str(e)}")