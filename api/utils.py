import spacy
import base64
from pathlib import Path
from fuzzywuzzy import fuzz
import json

try:
    nlp = spacy.load("pt_core_news_sm")
except:
    import os

    os.system("python -m spacy download pt_core_news_sm")
    nlp = spacy.load("pt_core_news_sm")

IMAGES_PATH = Path("data/images")


def load_intents():
    global INTENTS
    try:
        with open('data/intents.json', 'r', encoding='utf-8') as file:
            INTENTS = json.load(file)
        print("Intents carregados com sucesso!")
        print("Intents disponíveis:", list(INTENTS.keys()))
        return True
    except FileNotFoundError:
        raise Exception("Arquivo intents.json não encontrado!")
    except json.JSONDecodeError:
        raise Exception("Erro ao decodificar o arquivo JSON!")
    except Exception as e:
        raise Exception(f"Erro ao carregar intents: {str(e)}")


def get_image_base64(image_name):
    try:
        image_path = IMAGES_PATH / image_name.strip()

        if not image_path.exists():
            return None

        if not image_path.is_file():
            return None

        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return encoded
    except Exception as e:
        return None


def preprocess_text(text: str) -> str:
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_stop])

def find_best_match(question: str, intents: dict) -> tuple:
    preprocessed_question = preprocess_text(question)
    best_score = 0
    best_intent = None

    for intent, data in intents.items():
        for pattern in data["patterns"]:
            preprocessed_pattern = preprocess_text(pattern)
            score = max(
                fuzz.ratio(preprocessed_question, preprocessed_pattern),
                fuzz.partial_ratio(preprocessed_question, preprocessed_pattern),
                fuzz.token_sort_ratio(preprocessed_question, preprocessed_pattern)
            )

            if score > best_score and score > 50:
                best_score = score
                best_intent = intent

    return best_intent, best_score
