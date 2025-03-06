# Pract Chatbot


```
chatbot-erp/
│
├── api/
│   ├── __init__.py
│   ├── main.py          # Ponto de entrada da API
│   ├── models.py        # Definições de modelos Pydantic
│   ├── utils.py         # Funções utilitárias (processamento de texto, imagens, etc.)
│   ├── intents.py       # Lógica para carregar e gerenciar intenções
│   └── responses.py     # Lógica para gerar respostas
│
├── data/
│   ├── intents.json     # Arquivo JSON com as intenções
│   └── images/          # Pasta com as imagens dos produtos
│
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação do projeto
```

# Modelo Entidade-Relacionamento (MER)

## Entidades

### **Intents**
- **id** (PK)
- **nome** (varchar) — Exemplo: "saudacao", "reconhecimento_erro", "erro_regime_tributario", etc.
- **descricao** (varchar) — Descrição opcional do tipo de intenção.

### **Patterns**
- **id** (PK)
- **intent_id** (FK) — Relacionado com a tabela **Intents**.
- **pattern** (varchar) — Frase que o usuário pode digitar.

### **Responses**
- **id** (PK)
- **intent_id** (FK) — Relacionado com a tabela **Intents**.
- **response** (varchar) — Resposta que o bot vai fornecer.

### **Images**
- **id** (PK)
- **intent_id** (FK) — Relacionado com a tabela **Intents**.
- **image_url** (varchar) — URL da imagem relacionada à resposta.

### **Historico_Interacao**
- **id** (PK)
- **usuario_id** (FK) — Relacionado ao usuário (opcional, caso queira rastrear interações específicas de usuários).
- **intent_id** (FK) — Relacionado com a tabela **Intents**.
- **data_interacao** (timestamp) — Data e hora da interação.



## Explicação do Diagrama de Relacionamento de Entidades (DER)

### **Intents (Intenção):**
- Representa o tipo de intenção do usuário (exemplo: saudação, erro, etc.).
- Cada intenção pode ter um ou mais **Patterns** (padrões de frases que o usuário pode digitar).
- Cada intenção pode ter uma ou mais **Responses** (respostas fornecidas pelo chatbot).
- Algumas intenções podem ter imagens associadas, armazenadas na tabela **Images**.

### **Patterns (Padrões de Frases):**
- Cada padrão é uma frase que o chatbot reconhecerá, podendo desencadear uma resposta.
- Está vinculado a uma única **Intent**.

### **Responses (Respostas):**
- São as respostas fornecidas pelo chatbot quando uma intenção é reconhecida.
- Estão relacionadas a uma **Intent** específica.

### **Images (Imagens):**
- Algumas respostas podem conter imagens (por exemplo, para erros ou explicações visuais).
- As imagens estão associadas a uma **Intent**.

### **Historico_Interacao:**
- Armazena as interações entre o usuário e o bot.
- Pode ser útil para treinamento do chatbot ou rastreamento de interações anteriores.

