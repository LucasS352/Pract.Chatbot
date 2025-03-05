from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from fuzzywuzzy import fuzz
import spacy
import json
import base64
from pathlib import Path

# Carregar modelo spaCy
try:
    nlp = spacy.load("pt_core_news_sm")
except:
    import os
    os.system("python -m spacy download pt_core_news_sm")
    nlp = spacy.load("pt_core_news_sm")

app = FastAPI(title="Chatbot ERP Master")

# Variável global para armazenar as intenções
INTENTS = {}

# Configurar caminho das imagens - AJUSTADO PARA O CAMINHO CORRETO
IMAGES_PATH = Path("images/produtos")

# Verificar e listar imagens disponíveis
print("\nVerificando arquivos na pasta de imagens:")
available_images = list(IMAGES_PATH.glob('*'))
for img in available_images:
    print(f"- Encontrado: {img}")
print(f"Total de imagens encontradas: {len(available_images)}\n")

def load_intents():
    """Função para carregar/recarregar as intenções do arquivo JSON"""
    global INTENTS
    try:
        with open('intents.json', 'r', encoding='utf-8') as file:
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

# Carregar intenções inicialmente
load_intents()

class Message(BaseModel):
    question: str

def get_image_base64(image_name):
    """Função para carregar e codificar imagem em base64"""
    try:
        image_path = IMAGES_PATH / image_name.strip()
        print(f"\nTentando carregar imagem: {image_path}")
        
        if not image_path.exists():
            print(f"ERRO: Arquivo não encontrado em {image_path}")
            return None
            
        if not image_path.is_file():
            print(f"ERRO: {image_path} não é um arquivo válido")
            return None
            
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            print(f"✓ Imagem {image_name} carregada e codificada com sucesso")
            return encoded
            
    except Exception as e:
        print(f"ERRO ao processar {image_name}: {str(e)}")
        return None

def preprocess_text(text: str) -> str:
    """Pré-processa o texto removendo stopwords e aplicando lematização"""
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_stop])

def find_best_match(question: str, intents: Dict) -> tuple:
    """Encontra a melhor correspondência para a pergunta usando NLP"""
    preprocessed_question = preprocess_text(question)
    best_score = 0
    best_intent = None

    print(f"\nAnalisando pergunta: '{question}'")
    print(f"Texto processado: '{preprocessed_question}'")

    for intent, data in intents.items():
        for pattern in data["patterns"]:
            preprocessed_pattern = preprocess_text(pattern)
            ratio = fuzz.ratio(preprocessed_question, preprocessed_pattern)
            partial_ratio = fuzz.partial_ratio(preprocessed_question, preprocessed_pattern)
            token_sort_ratio = fuzz.token_sort_ratio(preprocessed_question, preprocessed_pattern)
            
            score = max(ratio, partial_ratio, token_sort_ratio)
            
            if score > best_score and score > 50:
                best_score = score
                best_intent = intent
                print(f"Match encontrado: '{pattern}' (score: {score})")

    return best_intent, best_score

@app.post("/chat")
async def chat(message: Message):
    try:
        intent, confidence = find_best_match(message.question, INTENTS)
        
        if intent:
            print(f"\nIntent identificado: {intent}")
            print(f"Confiança: {confidence}%")
            
            response_data = {
                "status": "success",
                "confidence": confidence,
                "response": INTENTS[intent]["responses"][0]
            }
            
            # Verificar se o intent tem imagens associadas
            if "images" in INTENTS[intent]:
                images_data = []
                print(f"\nProcessando imagens para o intent '{intent}':")
                
                for image_name in INTENTS[intent]['images']:
                    print(f"\nProcessando: {image_name}")
                    image_data = get_image_base64(image_name)
                    
                    if image_data:
                        images_data.append(image_data)
                        print(f"✓ {image_name} adicionada ao response")
                    else:
                        print(f"✗ Falha ao processar {image_name}")
                
                if images_data:
                    response_data["images"] = images_data
                    print(f"\nTotal de imagens incluídas na resposta: {len(images_data)}")
                else:
                    print("\nNenhuma imagem foi incluída na resposta")
            
            return response_data
        else:
            print("\nNenhum intent correspondente encontrado")
            return {
                "status": "not_found",
                "response": "Desculpe, não entendi sua pergunta. Pode reformular de outra forma?"
            }
    except Exception as e:
        print(f"\nERRO no processamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/intents")
async def list_intents():
    """Lista todos os intents disponíveis"""
    return {
        "status": "success",
        "intents": list(INTENTS.keys())
    }

@app.post("/reload")
async def reload_intents():
    """Recarrega as intenções do arquivo JSON"""
    try:
        load_intents()
        return {
            "status": "success",
            "message": "Intenções recarregadas com sucesso!",
            "intents_count": len(INTENTS)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n=== Iniciando Servidor do Chatbot ERP Master ===")
    print("Verificando configurações...")
    print(f"- Diretório de imagens: {IMAGES_PATH}")
    print(f"- Arquivo de intents: intents.json")
    print("\nIniciando servidor...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
