
from flask import Flask, render_template, request, jsonify, session
from gemini_api import consultar_gemini, processar_imagem_base64
import uuid
import os


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_secreta_de_desenvolvimento")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitar uploads a 16MB

@app.route('/')
def index():
    """Rota para a página principal"""
    # Gerar um ID de sessão se não existir
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['mensagens'] = []
    
    return render_template('index.html', historico=session.get('mensagens', []))

if __name__ == "__main__":
    # Obtém a porta da variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))  # Padrão para 5000 se não for especificado
    # Configura para escutar em 0.0.0.0 e na porta especificada
    app.run(host="0.0.0.0", port=port)

@app.route('/consultar', methods=['POST'])
def consultar():
    """Rota para processar consultas à API do Gemini"""
    data = request.json
    prompt = data.get('prompt', '')
    imagem_base64 = data.get('imagem', '')
    mime_type = data.get('mimeType', 'image/jpeg')
    
    if not prompt and not imagem_base64:
        return jsonify({'error': 'Prompt ou imagem não fornecido'}), 400
    
    # Garantir que temos a lista de mensagens
    if 'mensagens' not in session:
        session['mensagens'] = []
    
    # Criar a mensagem do usuário
    nova_mensagem = {
        "role": "user",
        "content": prompt
    }
    
    # Se tiver imagem, processar e adicionar à mensagem
    if imagem_base64:
        nova_mensagem["image"] = processar_imagem_base64(imagem_base64, mime_type)
    
    # Adicionar a nova mensagem do usuário ao histórico
    session['mensagens'].append(nova_mensagem)
    
    # Chamar a função de consulta à API do Gemini com o histórico completo
    resposta = consultar_gemini(session['mensagens'])
    
    # Adicionar a resposta ao histórico
    session['mensagens'].append({
        "role": "assistant",
        "content": resposta
    })
    
    # Salvar a sessão
    session.modified = True
    
    return jsonify({
        'resposta': resposta,
        'historico': session['mensagens']
    })

@app.route('/limpar-conversa', methods=['POST'])
def limpar_conversa():
    """Rota para limpar o histórico da conversa"""
    session['mensagens'] = []
    session.modified = True
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)

