/**
 * NotesService - Service Layer Pattern
 * Responsável exclusiva pela comunicação HTTP com a API.
 */
const notesService = {
    async getall(){
        const response = await fetch(`${API_BASE_URL}/notes/me`, { credentials: 'include'});
        if (!response.ok) throw new Error('Não foi possível carregar os teus apontamentos.');
        return response.json();
    },

    async adapt(noteId, signal){
        const response = await fetch(`${API_BASE_URL}/notes/${noteId}/adapt`, {
             method: 'GET', 
             credentials: 'include',
             signal
        });
        if (!response.ok) throw new Error('Não foi possível gerar a versão inclusiva.');
        return response.blob();
    },

    getAudioUrl(noteId){
        return `${API_BASE_URL}/notes/${noteId}/audio`;
    },

    async toggleLike(noteId){
        const response = await fetch(`${API_BASE_URL}/notes/${noteId}/like`, {
            method: 'POST',
            credentials: 'include'
        });
        if (!response.ok) throw new Error('Erro ao registar o gosto.');
        return response.json();
    },

    async delete(noteId){
        const response = await fetch(`${API_BASE_URL}/notes/${noteId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        if (!response.ok) throw new Error('Falha ao remover o apontamento.');
        return response.ok;
    },

    getAudioUrl(noteId){
        return `${API_BASE_URL}/notes/${noteId}/audio`;
    }
}