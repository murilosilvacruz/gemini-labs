document.addEventListener('DOMContentLoaded', function() {
    const promptInput = document.getElementById('prompt-input');
    const submitBtn = document.getElementById('submit-btn');
    const clearBtn = document.getElementById('clear-btn');
    const chatContainer = document.getElementById('chat-container');
    const loadingElement = document.getElementById('loading');
    const uploadImageBtn = document.getElementById('upload-image-btn');
    const takePhotoBtn = document.getElementById('take-photo-btn');
    const imageInput = document.getElementById('image-input');
    const cameraInput = document.getElementById('camera-input');
    const imagePreview = document.getElementById('image-upload-preview');
    const previewImg = document.getElementById('preview-img');
    const removeImageBtn = document.getElementById('remove-image-btn');
    
    let selectedImage = null;
    let selectedImageType = null;

    // Função para adicionar mensagem ao chat
    function adicionarMensagem(conteudo, remetente, imagem = null) {
        const mensagemDiv = document.createElement('div');
        mensagemDiv.className = `mensagem ${remetente}`;
        
        // Se tiver imagem, adiciona o preview
        if (imagem) {
            const imagePreviewDiv = document.createElement('div');
            imagePreviewDiv.className = 'image-preview';
            
            const img = document.createElement('img');
            img.src = imagem;
            img.alt = 'Imagem enviada';
            
            imagePreviewDiv.appendChild(img);
            mensagemDiv.appendChild(imagePreviewDiv);
        }
        
        const conteudoDiv = document.createElement('div');
        conteudoDiv.className = 'conteudo';
        conteudoDiv.textContent = conteudo;
        
        mensagemDiv.appendChild(conteudoDiv);
        chatContainer.appendChild(mensagemDiv);
        
        // Rolar para o final do chat
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Função para processar o upload de imagem
    function processarImagem(file) {
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const imageData = e.target.result;
            
            // Exibir preview da imagem
            previewImg.src = imageData;
            imagePreview.style.display = 'block';
            
            // Armazenar imagem para envio
            selectedImage = imageData;
            selectedImageType = file.type;
        };
        reader.readAsDataURL(file);
    }

    // Função para consultar a API
    async function consultarAPI() {
        const prompt = promptInput.value.trim();
        
        if (!prompt && !selectedImage) {
            alert('Por favor, digite uma consulta ou selecione uma imagem.');
            return;
        }
        
        // Adicionar mensagem do usuário ao chat
        adicionarMensagem(prompt, 'usuario', selectedImage);
        
        // Limpar o campo de entrada
        promptInput.value = '';
        
        // Mostrar indicador de carregamento
        loadingElement.style.display = 'block';
        
        try {
            const payload = { prompt: prompt };
            
            // Adicionar imagem ao payload se existir
            if (selectedImage) {
                payload.imagem = selectedImage;
                payload.mimeType = selectedImageType;
            }
            
            const response = await fetch('/consultar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Adicionar resposta do assistente ao chat
                adicionarMensagem(data.resposta, 'assistente');
                
                // Limpar imagem selecionada após envio
                limparImagemSelecionada();
            } else {
                adicionarMensagem(`Erro: ${data.error || 'Ocorreu um erro na consulta.'}`, 'assistente');
            }
        } catch (error) {
            adicionarMensagem(`Erro: ${error.message}`, 'assistente');
        } finally {
            // Esconder indicador de carregamento
            loadingElement.style.display = 'none';
        }
    }
    
    // Função para limpar a imagem selecionada
    function limparImagemSelecionada() {
        selectedImage = null;
        selectedImageType = null;
        previewImg.src = '';
        imagePreview.style.display = 'none';
    }
    
    // Função para limpar a conversa
    async function limparConversa() {
        try {
            const response = await fetch('/limpar-conversa', {
                method: 'POST',
            });
            
            if (response.ok) {
                // Limpar o chat no frontend
                chatContainer.innerHTML = '';
                // Limpar imagem selecionada
                limparImagemSelecionada();
            } else {
                alert('Erro ao limpar a conversa. Tente novamente.');
            }
        } catch (error) {
            alert(`Erro: ${error.message}`);
        }
    }
    
    // Event listeners para upload de imagem
    uploadImageBtn.addEventListener('click', function() {
        imageInput.click();
    });
    
    imageInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            processarImagem(this.files[0]);
        }
    });
    
    // Event listeners para foto da câmera
    takePhotoBtn.addEventListener('click', function() {
        cameraInput.click();
    });
    
    cameraInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            processarImagem(this.files[0]);
        }
    });
    
    // Event listener para remover imagem selecionada
    removeImageBtn.addEventListener('click', limparImagemSelecionada);
    
    // Adicionar event listener ao botão de envio
    submitBtn.addEventListener('click', consultarAPI);
    
    // Adicionar event listener ao botão de limpar
    clearBtn.addEventListener('click', limparConversa);
    
    // Permitir envio da consulta ao pressionar Enter no textarea
    promptInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Evitar quebra de linha
            consultarAPI();
        }
    });
    
    // Rolar para o final do chat quando a página carregar
    chatContainer.scrollTop = chatContainer.scrollHeight;
});