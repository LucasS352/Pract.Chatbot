import base64
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

IMAGES_PATH = Path(os.getenv("IMAGES_PATH"))


def get_image_base64(image_name):
    image_path = IMAGES_PATH / image_name.strip()
    try:
        if not image_path.exists():
            return None
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Erro ao processar imagem {image_name}: {str(e)}")
        return None


def generate_response(intent, confidence, intents):
    if not intent:
        return None
    response_data = {
        "status": "success",
        "confidence": confidence,
        "response": intents[intent]["responses"][0]
    }

    if "images" in intents[intent]:
        images_data = []
        for image_name in intents[intent]["images"]:
            image_data = get_image_base64(image_name)
            if image_data:
                images_data.append(image_data)
        if images_data:
            response_data["images"] = images_data

    return response_data
