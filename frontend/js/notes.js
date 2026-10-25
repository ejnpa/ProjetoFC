/**
 * Utilitário de segurança contra XSS
 */
const escapeHtml = (value) => 
    String(value || '').replace(/[&<>'"]/g, char => ({ 
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' 
    }[char]));

const state  = {
    notes :[],
    activeNote: null,
    adaptedBlobUrl:null
};

document.addEventListener('DOMContentLoaded', loadNotes);

/**
 * Carrega a lista de apontamentos do utilizador
 */
async function loadNotes() {
    const grid = document.getElementById('grelha-meus-apontamentos');
    if (!grid) return;

    try {
        state.notes = await notesService.getall();
        if (!state.notes.length) {
            grid.innerHTML = `
                <div class="mensagem-vazia">
                    <p>Ainda não partilhaste apontamentos.</p>
                    <a href="upload.html">Partilhar o primeiro →</a>
                </div>`;
            return; 
        }

        grid.innerHTML = state.notes.map(note =>{
            const likeCount = note.likes || 0;
            const isLikedClass = note.liked_by_user ? 'is-liked' : '';
            const noteId = String(note.id);
            const titleSafe = escapeHtml(note.title);
            return `
                    <article class="card-estudo">
                <div class="capa" 
                     role="button" 
                     tabindex="0"
                     onclick="openDocumentModal('${noteId}')"
                     onkeydown="if(event.key === 'Enter') openDocumentModal('${noteId}')"
                     title="Clica para abrir ${titleSafe}" 
                     style="cursor: pointer;">
                    <img src="${escapeHtml(note.thumbnail_url || 'https://via.placeholder.com/300x180?text=PDF')}" alt="Pré-visualização de ${titleSafe}">
                </div>
                
                <div class="info">
                    <h3 onclick="openDocumentModal('${noteId}')" style="cursor: pointer;" title="Clica para abrir">${titleSafe}</h3>
                    <span class="tag">${escapeHtml(note.subject)}</span>
                    <p class="autor">👤 ${escapeHtml(note.author)}</p>
                    
                    <div class="acoes" style="display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; align-items: center;">
                        <button type="button" class="btn-like ${isLikedClass}" data-action="like">
                            <svg viewBox="0 0 24 24">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                            </svg>
                            <span class="like-count">${likeCount}</span>
                        </button>

                        <button type="button" onclick="deleteNote('${noteId}')" class="btn-ver" style="background: #ffcdd2; color: #b71c1c; border:none; cursor:pointer; padding: 6px 12px;">
                            🗑️ Apagar
                        </button>
                    </div>
                </div>
            </article>`
        }).join('');

        grid.addEventListener('click', (event) => {
            const trigger = event.target.closest('[data-action]');
            if (!trigger) return;

            const card = trigger.closest('.card-estudo');
            const noteId = card?.dataset.id;
            if (!noteId) return;

            const actions = {
                open: () => modalController.open(noteId),
                like: () => window.toggleLike(trigger, noteId),
                delete: () => notesService.delete(noteId)
            };

            const action = trigger.dataset.action;
            if (actions[action]) actions[action]();
        });

    } catch (error) {
        console.error("Erro a carregar apontamentos", error);
        grid.innerHTML = `<p class="loading-state error-state">Erro: ${escapeHtml(error.message)}</p>`;
    }
}


/**
 * Remove um apontamento
 */
async function deleteNote(id) {
    if (!confirm('Tens a certeza que queres apagar este apontamento?')) return;
    try{
        await notesService.delete(id);
        if (typeof showAlerts === 'function') showAlerts('Apontamento apagado!', 'sucesso');
        loadNotes();
    }catch(error){
        console.error("Erro ao apagar:",error);
        if (typeof showAlerts === 'function') showAlerts('Erro de comunicação com o servidor.', 'erro');
    }     
}

/**
 * Abre o modal e inicializa o visualizador com o ficheiro original
 */
async function openDocumentModal(id){
    const note = state.notes.find(n => String(n.id) === String(id));
    if (!note){
        console.error("Apontamento não localizado:", id);
        return;
    } 

    state.activeNote = note;

    if (state.adaptedBlobUrl){
         URL.revokeObjectURL(state.adaptedBlobUrl);
         state.adaptedBlobUrl = null;
    }

    const modal = document.getElementById('modal-inclusivo');
    const titulo = document.getElementById('modal-titulo');
    const audioContainer = document.getElementById('container-audio-player');
    const playerAudio = document.getElementById('player-audio-tts');
    

    if (titulo)titulo.textContent = note.title;
    if (audioContainer) audioContainer.style.display = 'none';
    if (playerAudio) {
        playerAudio.pause();
        playerAudio.src = '';
    }
    
    if (modal) {
        modal.removeAttribute('hidden');
        modal.style.display = 'flex';
    }
    showOriginalNote();
}

/**
 * Fecha o modal e limpa recursos
 */
function closeModal() {
    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;
    }

    const modal = document.getElementById('modal-inclusivo');
    const iframe = document.getElementById('visualizador-pdf');
    const playerAudio = document.getElementById('player-audio-tts');
    const audioContainer = document.getElementById('container-audio-player');

    if (playerAudio) {
        playerAudio.pause();
        playerAudio.src= '';
    }
    if (iframe) iframe.src = '';
    if (audioContainer) audioContainer.style.display = 'none';
    
    if (state.adaptedBlobUrl) {
        URL.revokeObjectURL(state.adaptedBlobUrl);
        state.adaptedBlobUrl = null;
    }

    state.activeNote = null;
    if (modal) {
        modal.setAttribute('hidden', '');
        modal.style.display = 'none';
    }
    
}


/**
 * Mostra o apontamento original diretamente no visualizador
 */
function showOriginalNote(){
    if (!state.activeNote) return;

    const iframe = document.getElementById('visualizador-pdf');
    const loadingContainer = document.getElementById('modal-loading-state');
    const btnOriginal = document.getElementById('btn-ver-original');
    const btnInclusao = document.getElementById('btn-gerar-inclusao');

    if(btnOriginal)btnOriginal.classList.add('is-active');
    if(btnInclusao)btnInclusao.classList.remove('is-active');
    if(loadingContainer)loadingContainer.style.display = 'none';

    
     if (iframe) {
        iframe.src = state.activeNote.file_url;
        iframe.style.display = 'block';
     }
}   

/**
 * Processa e gera a versão inclusiva
 */
let currentAbortController = null;

async function generateInclusiveVersion(){
    if (!state.activeNote) return;
    
        if (!state.activeNote) return;

        const iframe = document.getElementById('visualizador-pdf');
        const loadingContainer = document.getElementById('modal-loading-state');
        const btnInclusao = document.getElementById('btn-gerar-inclusao');
        const btnOriginal = document.getElementById('btn-ver-original');

        if (btnInclusao) btnInclusao.classList.add('is-active');
        if (btnOriginal) btnOriginal.classList.remove('is-active');

        if (state.adaptedBlobUrl){
            if (iframe) {
                iframe.src = state.adaptedBlobUrl;
                iframe.style.display = 'block';
            }
            if (loadingContainer) loadingContainer.style.display = 'none';
            return;
        }

        if (iframe) iframe.style.display = 'none';
        if (loadingContainer) {
            loadingContainer.innerHTML = `
                <h3 style="color:#FCC067;">🧠 A processar com Inteligência Artificial...</h3>
                <p>A ler, resumir e a estruturar o documento.<br>Isto pode demorar cerca de 1 minuto.</p>
            `;
            loadingContainer.style.display = 'flex';
        }

        if (currentAbortController) currentAbortController.abort();
        currentAbortController = new AbortController();

        try{
            const blob = await notesService.adapt(state.activeNote.id, currentAbortController.signal);
            state.adaptedBlobUrl = URL.createObjectURL(blob);

            if (iframe) {
                iframe.src = state.adaptedBlobUrl;
                iframe.style.display = 'block';
            }
            if (loadingContainer) loadingContainer.style.display = 'none';
        }catch(error){
            if (error.name === 'AbortError') return;
            console.error("Erro ao gerar inclusão:",error);
            if (loadingContainer) {
                loadingContainer.innerHTML = `<p style="color:#d32f2f; font-weight:bold;">Erro: ${escapeHtml(error.message)}</p>`;
            }
        }finally {
            currentAbortController = null;
        }
 }

/**
 * Alterna e controla a reprodução do sintetizador de voz (TTS)
 */
async function toggleTTSAudio(){
    if (!state.activeNote)return;

    const audioContainer = document.getElementById('container-audio-player');
    const playerAudio = document.getElementById('player-audio-tts');
    const btnTTS = document.getElementById('btn-gerar-tts');

    if (!audioContainer || !playerAudio) return;

    if (audioContainer.style.display === 'flex'){
        playerAudio.pause();
        audioContainer.style.display = 'none';
        btnTTS.classList.remove('is-active');
        return;
    }

    const originalText = btnTTS ? btnTTS.innerHTML : '';
    if(btnTTS){
        btnTTS.disabled = true;
        btnTTS.innerHTML = '⏳ A preparar áudio...';
    }
    
    try{
        playerAudio.src = notesService.getAudioUrl(state.activeNote.id);
        audioContainer.style.display = 'flex';
        if (btnTTS) btnTTS.classList.add('is-active');
        playerAudio.play().catch(() => {});
    }catch(error){
        console.error("Erro ao carregar áudio:", error);
        alert("Não foi possível carregar a síntese de voz para este apontamento.");
    } finally{
        if (btnTTS) {
            btnTTS.disabled = false;
            btnTTS.innerHTML = originalText;  
        }
    }
}


        
        

     
