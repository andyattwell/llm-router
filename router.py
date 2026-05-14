from fastapi import FastAPI
import requests

app = FastAPI()

FAST = "http://localhost:8081/v1/chat/completions"
SMART = "http://localhost:8082/v1/chat/completions"
VISION = "http://localhost:8083/v1/chat/completions"


def is_complex(prompt):
    keywords = [
        "analyze", "architecture", "debug",
        "compare", "optimize", "reason"
    ]

    if len(prompt) > 200:
        return True

    if any(k in prompt.lower() for k in keywords):
        return True

    return False


@app.post("/v1/chat/completions")
async def route(req: dict):

    messages = req.get("messages", [])
    content = str(messages[-1])

    has_image = "image_url" in content

    if has_image:
        target = VISION
    else:
        target = SMART if is_complex(content) else FAST

    r = requests.post(target, json=req)
    return r.json()