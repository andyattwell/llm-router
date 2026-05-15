# Integración de Voz - Routing LLM

## Resumen

Se han agregado tres nuevos endpoints para integrar capacidades de voz (Speech-to-Text y Text-to-Speech) al router LLM:

### Endpoints Disponibles

#### 1. **POST `/v1/audio/transcribe`** - Convertir audio a texto

Transcribe un archivo de audio (WAV, MP3, etc.) a texto usando Whisper (OpenAI).

**Request:**

```bash
curl -X POST "http://127.0.0.1:8060/v1/audio/transcribe" \
  -F "file=@audio.wav"
```

**Response:**

```json
{
  "text": "Hola, ¿cómo estás?",
  "language": "es"
}
```

---

#### 2. **POST `/v1/audio/speak`** - Convertir texto a audio

Convierte texto a audio usando síntesis de voz (pyttsx3).

**Request:**

```bash
curl -X POST "http://127.0.0.1:8060/v1/audio/speak" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, soy un asistente de voz"}' \
  --output output.mp3
```

**Response:** Archivo MP3 de audio

---

#### 3. **POST `/v1/chat/audio`** - Chat por voz (flujo completo)

Flujo end-to-end: Audio → Transcripción → LLM → Respuesta → Audio

**Request:**

```bash
curl -X POST "http://127.0.0.1:8060/v1/chat/audio" \
  -F "audio_file=@pregunta.wav" \
  -F "model=gemma2-fast"
```

**Response:**

```json
{
  "user_input": "¿Cuál es la capital de Francia?",
  "assistant_response": "La capital de Francia es París.",
  "audio": "ffd8ffe000...", // Hex del audio MP3
  "model_used": "gemma2-fast"
}
```

---

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Librerías principales:**

- `openai-whisper` - Speech-to-Text (reconocimiento de voz)
- `pyttsx3` - Text-to-Speech (síntesis de voz)
- `python-multipart` - Manejo de file uploads

### 2. Primeras librerías a descargar

En la primera ejecución, Whisper descargará el modelo base (~140 MB):

```
Loading Whisper model...
# Descargando ~//.cache/whisper/base.pt
```

---

## Uso

### Opción A: Script de Prueba

```bash
# Transcribir audio
python test_audio.py transcribe audio.wav

# Generar voz desde texto
python test_audio.py speak "Hola, ¿cómo estás?"

# Chat por voz completo
python test_audio.py voice audio.wav gemma2-fast
```

### Opción B: Curl directo

```bash
# Transcribir
curl -X POST "http://127.0.0.1:8060/v1/audio/transcribe" \
  -F "file=@audio.wav"

# Hablar
curl -X POST "http://127.0.0.1:8060/v1/audio/speak" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola mundo"}' \
  --output respuesta.mp3
```

### Opción C: Cliente Python

```python
import requests

# Transcribir
with open("audio.wav", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://127.0.0.1:8060/v1/audio/transcribe",
        files=files
    )
    print(response.json())

# Text-to-Speech
response = requests.post(
    "http://127.0.0.1:8060/v1/audio/speak",
    json={"text": "Hola"}
)
with open("salida.mp3", "wb") as f:
    f.write(response.content)
```

---

## Configuración

### Cambiar modelo de Whisper

En `router.py`, modifica el tamaño del modelo:

```python
def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        # Opciones: tiny, base, small, medium, large
        whisper_model = whisper.load_model("small")  # En vez de "base"
    return whisper_model
```

**Tamaños disponibles:**

- `tiny` - Más rápido, menos preciso (~39 MB)
- `base` - Balance (defecto, ~140 MB)
- `small` - Más preciso (~465 MB)
- `medium` - Muy preciso (~1.5 GB)
- `large` - Máxima precisión (~2.9 GB)

### Cambiar velocidad de voz

En `router.py`:

```python
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # 50-300 (defecto: 200)
tts_engine.setProperty('volume', 1.0)  # 0.0-1.0
```

### Cambiar idioma de transcripción

En los endpoints, la transcripción por defecto es en español (`language="es"`).

Para cambiar a otro idioma, modifica `router.py`:

```python
result = model.transcribe(tmp_path, language="es")  # Cambiar a "en", "fr", etc.
```

---

## Flujo de Integración con Open WebUI

Si deseas agregar interfaz de voz a Open WebUI:

1. **Crear un plugin** que envíe audio a `/v1/chat/audio`
2. **Usar Web Audio API** para captura de micrófono:

```javascript
const mediaRecorder = new MediaRecorder(stream);
mediaRecorder.ondataavailable = (event) => {
  const audioBlob = event.data;
  const formData = new FormData();
  formData.append("audio_file", audioBlob, "audio.wav");
  formData.append("model", "gemma2-fast");

  fetch("http://127.0.0.1:8060/v1/chat/audio", {
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      console.log(data.assistant_response);
    });
};
```

---

## Casos de Uso

✅ **Chat por voz** - Hablar y recibir respuestas en audio
✅ **Transcripción de memos** - Convertir grabaciones a texto
✅ **Asistente de voz** - Comandos hablados para el LLM
✅ **Accesibilidad** - Interfaz auditiva para usuarios
✅ **Análisis de audio** - Procesar grabaciones con Whisper

---

## Limitaciones y Notas

- **TTS (pyttsx3)**: Calidad de voz natural es limitada. Para mejor calidad, considera:
  - `gTTS` (Google Text-to-Speech) - Requiere conexión
  - `elevenlabs` - Voz muy natural (requiere API key)
  - `azure-cognitiveservices-speech` - Enterprise

- **STT (Whisper)**: Offline y open-source. Alternativas:
  - `google-cloud-speech` - Más preciso (requiere API key)
  - `azure-cognitiveservices-speech` - Enterprise

- **Rendimiento**:
  - Primera carga de Whisper: ~5-10 segundos
  - Transcripción por archivo: 30-60 segundos (depende de duración y modelo)
  - TTS: ~2-5 segundos por frase

---

## Próximos Pasos

1. **Instalar dependencias:** `pip install -r requirements.txt`
2. **Iniciar router:** `python -m uvicorn router:app --port 8060`
3. **Probar:** `python test_audio.py transcribe sample.wav`
4. **Integrar en Open WebUI** con plugin JavaScript

¿Preguntas? Revisa los logs de error en la terminal para diagnosticar problemas.
