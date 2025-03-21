import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
 
chat = client.chats.create(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(system_instruction="Você é um professor de matemática. O aluno vai usar você para tirar dúvidas sobre problemas. Não forneça as respostas prontas. Ao invés disso, de instruções dos fundamentos relacionados à resolução do problema, e forneça um passo a passo para a resolução.")
    )

def consultar_gemini(mensagens):
    try:
        contents = []
       
        for msg in mensagens:
            if msg["role"] == "user":
                if "image" in msg and msg["image"]:
                    # Se tiver imagem, adicionamos tanto a imagem quanto o texto (se houver)
                    parts = []
                    
                    # Adiciona a imagem como parte da mensagem
                    parts.append({
                        "inline_data": {
                            "mime_type": msg["image"]["mime_type"],
                            "data": msg["image"]["data"]
                        }
                    })
                    
                    # Adiciona o texto se existir
                    if msg["content"]:
                        parts.append({"text": msg["content"]})
                    
                    contents.append({"role": "user", "parts": parts})
                else:
                    # Mensagem de texto normal
                    contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            else:
                # Mensagem do modelo
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
         
        # Iniciamos o chat com a instrução do sistema
        if len(contents) > 1:  # Se temos mais que apenas a mensagem atual
            for i in range(0, len(contents) - 1, 2):  # Enviamos pares user-model
                if i + 1 < len(contents):  # Garantimos que temos o par completo
                    # Simulamos a conversa anterior
                    user_message = contents[i]
                    
                    # Enviamos a mesma estrutura de mensagem do usuário
                    if len(user_message["parts"]) > 1 or "inline_data" in user_message["parts"][0]:
                        # Se tem imagem, processamos de forma especial
                        response = chat.send_message(user_message["parts"])
                    else:
                        # Mensagem de texto simples
                        response = chat.send_message(user_message["parts"][0]["text"])
        
        # Enviamos a mensagem mais recente
        latest_message = contents[-1]
        
        if len(latest_message["parts"]) > 1 or "inline_data" in latest_message["parts"][0]:
            # Se tem imagem, enviamos as partes completas
            response = chat.send_message(latest_message["parts"])
        else:
            # Mensagem de texto simples
            response = chat.send_message(latest_message["parts"][0]["text"])
            
        return response.text
    except Exception as e:
        return f"Erro ao consultar API Gemini: {str(e)}"

def processar_imagem_base64(imagem_base64, mime_type):
    """
    Processa uma imagem no formato base64
    
    Args:
        imagem_base64 (str): String base64 da imagem
        mime_type (str): Tipo MIME da imagem
        
    Returns:
        dict: Dicionário com os dados da imagem processada
    """
    # Remover o prefixo "data:image/jpeg;base64," se existir
    if "," in imagem_base64:
        imagem_base64 = imagem_base64.split(",", 1)[1]
    
    return {
        "mime_type": mime_type,
        "data": imagem_base64
    }