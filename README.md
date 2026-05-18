# Routing LLM

A smart routing server for Large Language Models with voice integration capabilities. This project automatically routes requests to the most appropriate model based on complexity, supports vision models, and includes full voice-to-voice conversation features.

## Features

- **Intelligent Routing**: Automatically routes requests to fast, smart, or vision models based on content complexity and requirements
- **Multiple Models**:
  - **Fast Model**: Gemma 2 2B (Q6_K_L) - For simple queries
  - **Smart Model**: Gemma 4 E4B (Q5_K_M) - For complex reasoning with vision capabilities
  - **Vision Model**: Qwen3 VL 8B (Q4_K_M) - Specialized for vision tasks
- **Voice Integration**:
  - Speech-to-Text using OpenAI Whisper
  - Text-to-Speech using Google TTS (natural voices) or pyttsx3
  - Full voice-to-voice conversation pipeline
- **Web UI**: Open-WebUI interface for easy interaction
- **OpenAI API Compatible**: Compatible with OpenAI API format

## Architecture

The system consists of:

- **Router** (FastAPI): Main routing logic and voice processing
- **Model Servers**: Individual llama-server instances for each model
- **Web UI**: Open-WebUI container for user interface

## Prerequisites

- Python 3.8+
- llama.cpp with CUDA support (compiled and available at `../llama.cpp/build-cuda/bin/`)
- Docker and Docker Compose (for Web UI)
- Model files in GGUF format

## Installation

1. **Clone and setup llama.cpp**:

   ```bash
   # Assuming llama.cpp is at the same level as this project
   cd ../llama.cpp
   mkdir build-cuda
   cd build-cuda
   cmake .. -DLLAMA_CUDA=ON
   make -j$(nproc)
   ```

2. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Download models**:
   Place the following GGUF model files in the `models/` directory:
   - `gemma-2-2b-it-Q6_K_L.gguf`
   - `gemma-4-E4B-it-Q5_K_M.gguf`
   - `gemma-4-E4B-it-Q5_K_M-mmproj-F16.gguf` (vision projection)
   - `Qwen3-VL-8B-Instruct-Q4_K_M.gguf`
   - `Qwen3-VL-8B-Instruct-Q4_K_M-mmproj-F16.gguf` (vision projection)

## Usage

### Start the System

Run the complete system (router + web UI):

```bash
./start.sh
```

This will:

- Start the FastAPI router on port 8060
- Start the Open-WebUI on port 3000
- Automatically start model servers as needed

### Manual Control

**Start individual components:**

- Router only: `uvicorn router:app --host 127.0.0.1 --port 8060`
- Web UI only: `./web-ui.sh`
- Individual models:
  - Fast model: `./run-fast.sh`
  - Smart model: `./run-smart.sh`
  - Vision model: `./run-vision.sh`

### API Endpoints

#### Chat Completions

```bash
curl -X POST "http://127.0.0.1:8060/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "model": "gemma2-fast"
  }'
```

#### Voice Features

**Transcribe Audio:**

```bash
curl -X POST "http://127.0.0.1:8060/v1/audio/transcribe" \
  -F "file=@audio.wav"
```

**Text to Speech:**

```bash
curl -X POST "http://127.0.0.1:8060/v1/audio/speak" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!"}' \
  --output speech.mp3
```

**Voice Chat (full pipeline):**

```bash
curl -X POST "http://127.0.0.1:8060/v1/chat/audio" \
  -F "audio_file=@question.wav" \
  -F "model=gemma2-fast"
```

## Routing Logic

The router automatically selects the appropriate model:

- **Fast Model** (Gemma 2 2B): Simple queries, short responses
- **Smart Model** (Gemma 4): Complex reasoning, analysis, comparison tasks, or when prompt > 200 characters
- **Vision Model** (Qwen3 VL): When images are present in the request or explicitly requested

## Testing

Use the provided test script for voice features:

```bash
# Transcribe audio
python test_audio.py transcribe audio.wav

# Generate speech
python test_audio.py speak "Hello world"

# Voice chat
python test_audio.py voice audio.wav gemma2-fast
```

## Configuration

### Model Parameters

Each model server can be configured by editing the respective shell scripts:

- `run-fast.sh`: Fast model configuration
- `run-smart.sh`: Smart model configuration
- `run-vision.sh`: Vision model configuration

Key parameters:

- `-ngl`: GPU layers
- `-c`: Context size
- `-b`: Batch size
- `-t`: Threads

### Voice Settings

Voice parameters are configured in `router.py`:

- **Speech-to-Text**: Whisper model: `base` (change to `small`, `medium`, `large` for better accuracy)
- **Text-to-Speech**: 
  - Primary: Google Text-to-Speech (gTTS) - natural voices
  - Fallback: pyttsx3 (robotic but offline)
  - Language: `es` (Spanish) - change to `en` for English
  - Toggle: Set `USE_GTTS = False` to use pyttsx3 fallback

**Alternative TTS Options:**
- **ElevenLabs API**: Premium natural voices (requires API key)
- **OpenAI TTS API**: High-quality voices (requires API key)  
- **Coqui TTS**: Open-source high-quality (requires additional setup)

## Web Interface

Access the web UI at `http://localhost:3000` after starting the system. The interface connects to the router's OpenAI-compatible API.

## Troubleshooting

### Common Issues

1. **Model servers fail to start**: Ensure llama.cpp is properly compiled with CUDA support
2. **CUDA out of memory**: Reduce `-ngl` parameter in model scripts
3. **Voice transcription fails**: Check audio file format (WAV/MP3 supported)
4. **Web UI not accessible**: Ensure Docker is running and ports are available

### Logs

Check terminal output for router and model server logs. Model servers run in background and their output is suppressed.

## Dependencies

- fastapi: Web framework
- uvicorn: ASGI server
- requests: HTTP client
- python-multipart: File upload handling
- openai-whisper: Speech recognition
- gtts: Google Text-to-Speech (natural voices)
- pyttsx3: Text-to-speech fallback
- llama.cpp: Model inference engine
- Open-WebUI: Web interface

## License

This project is open source. Check individual component licenses for details.
