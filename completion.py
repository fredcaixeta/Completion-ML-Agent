import os
import requests
import json
from dotenv import load_dotenv
import json
import re

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Função para criar uma conclusão usando a API da OpenAI
def OpenAICompletion(system_message, questions):
    # Lista para armazenar as mensagens formatadas
    formatted_questions = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    # Verifica e formata as perguntas
    for question in questions:
        if not isinstance(question, dict) or ('assistant' not in question and 'user' not in question):
            return {"error": "Each question must be a dict containing the keys 'assistant' or 'user'"}
        
        if 'assistant' in question:
            formatted_questions.append({
                "role": "assistant",
                "content": question['assistant']
            })
        
        if 'user' in question:
            formatted_questions.append({
                "role": "user",
                "content": question['user']
            })

    # Configuração da API
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"  # Use a chave da API do ambiente
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": formatted_questions
    }

    # Envio da requisição para a API
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    # Verifica se a resposta é válida
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        return {"error": response.status_code, "message": response.text}

def start_Completion(question):
    print("start completion")
    
    system_message = f"Você é um assistente que entregará a um modelo de Machine Learning os parâmetros para prever o ruído de um aerofólio diante do pedido do usuário. Parâmetros vindos do usuário - Frequency (ex: 300), Suction Thickness (ex: 0.02), Chord Length (ex: 1.5), Angle of Attack (ex: 53), Free Stream Velocity (ex: 50). Retorne apenas o json com os parâmetros a serem entregues ao modelo."
    questions = question
    questions = [
        {"user": questions}
    ]

    response = OpenAICompletion(system_message, questions)
    return response

def trigger_model():
    pass

# Exemplo de uso
if __name__ == "__main__":
    
    
    with open('response_rag.json', 'r') as file:
        response = json.load(file)
    
    print(response)
    pdf = response["arquivo"]
    question = response["pergunta"]
    
    print("pdf")
    print(pdf)
    print("question")
    print(question)
    
    rag.start_rag(pdf_doc=pdf, user_question=question)
    
    
