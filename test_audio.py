#!/usr/bin/env python3
"""
Script de prueba para los endpoints de audio (voz) en el router LLM.
Requiere que el router esté corriendo en http://127.0.0.1:8060

Uso:
    python test_audio.py transcribe <archivo_audio.wav>
    python test_audio.py speak "Tu texto aquí"
    python test_audio.py voice <archivo_audio.wav> [modelo]
"""

import requests
import sys
import json
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8060"

def test_transcribe(audio_file):
    """Prueba endpoint de transcripción (audio -> texto)"""
    print(f"[*] Transcribiendo: {audio_file}")
    
    if not os.path.exists(audio_file):
        print(f"[!] Error: Archivo no encontrado: {audio_file}")
        return
    
    with open(audio_file, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/v1/audio/transcribe", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"[✓] Transcripción exitosa:")
        print(f"    Texto: {result['text']}")
        print(f"    Idioma: {result.get('language', 'unknown')}")
    else:
        print(f"[!] Error ({response.status_code}): {response.text}")


def test_speak(text, output_file="output.mp3"):
    """Prueba endpoint de síntesis de voz (texto -> audio)"""
    print(f"[*] Generando voz para: '{text}'")
    
    response = requests.post(
        f"{BASE_URL}/v1/audio/speak",
        json={"text": text}
    )
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"[✓] Audio generado: {output_file}")
    else:
        print(f"[!] Error ({response.status_code}): {response.text}")


def test_voice_chat(audio_file, model="gemma2-fast"):
    """Prueba flujo completo: Audio -> Texto -> LLM -> Texto -> Audio"""
    print(f"[*] Chat por voz: {audio_file} (modelo: {model})")
    
    if not os.path.exists(audio_file):
        print(f"[!] Error: Archivo no encontrado: {audio_file}")
        return
    
    with open(audio_file, "rb") as f:
        files = {"audio_file": f}
        data = {"model": model}
        response = requests.post(
            f"{BASE_URL}/v1/chat/audio",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"[✓] Conversación exitosa:")
        print(f"    Tu pregunta: {result['user_input']}")
        print(f"    Respuesta: {result['assistant_response']}")
        print(f"    Modelo usado: {result['model_used']}")
        
        # Guardar audio de respuesta
        audio_bytes = bytes.fromhex(result['audio'])
        output_file = "response_audio.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        print(f"    Audio guardado: {output_file}")
    else:
        print(f"[!] Error ({response.status_code}): {response.text}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "transcribe" and len(sys.argv) >= 3:
            test_transcribe(sys.argv[2])
        
        elif command == "speak" and len(sys.argv) >= 3:
            text = " ".join(sys.argv[2:])
            test_speak(text)
        
        elif command == "voice" and len(sys.argv) >= 3:
            audio_file = sys.argv[2]
            model = sys.argv[3] if len(sys.argv) >= 4 else "gemma2-fast"
            test_voice_chat(audio_file, model)
        
        else:
            print(__doc__)
            sys.exit(1)
    
    except requests.exceptions.ConnectionError:
        print(f"[!] Error: No se puede conectar a {BASE_URL}")
        print("    Asegúrate de que el router esté ejecutándose")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {str(e)}")
        sys.exit(1)
