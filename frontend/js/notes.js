const escapeHtml = (value) => String(value || '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));

document.addEventListener('DOMContentLoaded', loadNotes);

async function loadNotes() {
    const grid = document.getElementById('grelha-meus-apontamentos');
    if (!grid) return;

    try {
        const response = await fetch(`${API_BASE_URL}/notes/me`, { credentials: 'include' });
        if (!response.ok) throw new Error('Sessão expirada ou apontamentos indisponíveis.');

        const notes = await response.json();
        if (!notes.length) {
            grid.innerHTML = '<div class="mensagem-vazia"><p>Ainda não partilhaste apontamentos.</p><a href="upload.html">Partilhar o primeiro →</a></div>';
            return;
        }

        grid.innerHTML = notes.map(note =>`
            <article class="card-estudo">
                <div class="capa">
                    <img src="${escapeHtml(note.thumbnail_url || 'https://via.placeholder.com/300x180?text=PDF')}" alt="Pré-visualização do apontamento">
                </div>
                <div class="info">
                    <h3>${escapeHtml(note.title)}</h3>
                    <span class="tag">${escapeHtml(note.subject)}</span>
                    <p class="autor">👤 ${escapeHtml(note.author)}</p>
                    <div class="acoes" style="display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
                        <a href="${escapeHtml(note.file_url)}" target="_blank" rel="noopener" class="btn-ver" style="padding: 6px 12px;">Ver ficheiro</a>
                        <button onclick="openInclusiveReader('${escapeHtml(note.id)}', '${escapeHtml(note.title).replace(/'/g, "\\'")}')" class="btn-ver" style="background-color: #FCC067; color: white; border:none; cursor:pointer; padding: 6px 12px;">🧠 Leitor inclusivo</button>
                        <button onclick="deleteNote('${escapeHtml(note.id)}')" class="btn-ver" style="background: #ffcdd2; color: #b71c1c; border:none; cursor:pointer; padding: 6px 12px;">🗑️ Apagar</button>
                    </div>
                </div>
            </article>`).join('');
    } catch (error) {
        console.error("Erro a carregar apontamentos", error);
        grid.innerHTML = `<p class="loading-state error-state">Erro: ${escapeHtml(error.message)}</p>`;
    }
}

async function deleteNote(id) {
    if (!confirm('Tens a certeza que queres apagar este apontamento?')) return;
    try{
    const response = await fetch(`${API_BASE_URL}/notes/${id}`, { method: 'DELETE', credentials: 'include' });
    if (response.ok) {
        if (typeof showAlerts === 'function') showAlerts('Apontamento apagado!', 'sucesso');
        loadNotes();
    }else{ 
        if (typeof showAlerts === 'function') showAlerts('Não foi possível apagar o apontamento.', 'erro');
    }
}catch(error){
    console.error(error);
        if (typeof showAlerts === 'function') showAlerts('Erro de comunicação com o servidor.', 'erro');
}     
}

function closeModal() {
    const modal = document.getElementById('modal-inclusivo');
    modal.hidden = true;
    modal.style.display = 'none';
    document.getElementById('modal-texto').innerHTML = '';
}

async function openInclusiveReader(id, title) {
    const modal = document.getElementById('modal-inclusivo');
    const content = document.getElementById('modal-texto');

    modal.hidden = false;
    modal.style.display = 'flex';

    document.getElementById('modal-titulo').textContent = title;

    content.innerHTML = `
        <div class="loading-ia" style="text-align: center; padding: 40px;">
            <h3 style="color:#FCC067;">🧠 A processar com Inteligência Artificial...</h3>
            <p>A ler, resumir e a desenhar o teu PDF Inclusivo.<br>Isto pode demorar cerca de 1 minuto.</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE_URL}/notes/${id}/adapt`, {
            method: 'GET',
            credentials: 'include' 
        });
        if (!response.ok) throw new Error('Não foi possível adaptar este documento.');

        const blob = await response.blob();
        const pdfUrl = URL.createObjectURL(blob);

        content.innerHTML = `
            <iframe src="${pdfUrl}"></iframe>
        `;
    } catch (error) {
        console.error(error);
        content.innerHTML = `<p style="color:red; text-align:center;">Erro: ${escapeHtml(error.message)}</p>`;
    }
}
