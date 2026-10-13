class LanguageManager {
    constructor() {
        if (LanguageManager.instance) {
            return LanguageManager.instance;
        }

        let savedLang = localStorage.getItem('preferred_language');

        if (!savedLang || savedLang === 'null' || savedLang === 'undefined') {
            savedLang = 'pt-PT';
            localStorage.setItem('preferred_language', 'pt-PT');
        }

        this.currentLang = savedLang;

        this.dictionary = { 
            "pt-PT": {
                "menu-explorar": "Explorar",
                "menu-como-funciona": "Como funciona",
                "menu-contactos": "Contactos",
                "btn-entrar": "Entrar",
                "btn-criar-conta": "Criar conta",
                "menu-titulo": "Menu",
                "menu-lateral-inicio": "Página inicial",
                "menu-lateral-explorar": "Explorar materiais",
                "menu-lateral-partilhar": "Partilhar apontamentos",
                "menu-lateral-meus": "Os meus apontamentos",
                "menu-slogan": "Aprende. Partilha. Cresce.",
                "btn-conta-gratis": "Criar conta gratuita",
                "upload-comunidade": "Comunidade exe.cuTIva",
                "upload-titulo": "Partilhar apontamento",
                "upload-desc": "Ajuda outros estudantes com os teus materiais de estudo.",
                "label-titulo": "Título",
                "placeholder-titulo": "Ex.: Resumo de Redes — Capítulo 1",
                "label-escola": "Escola superior",
                "opt-escola": "Seleciona a escola...",
                "label-curso": "Curso",
                "opt-curso": "Seleciona primeiro uma escola...",
                "label-ano": "Ano letivo",
                "opt-ano": "Seleciona primeiro um curso...",
                "label-disciplina": "Disciplina",
                "opt-disciplina": "Seleciona primeiro o ano...",
                "label-ficheiro": "Ficheiro",
                "btn-submeter": "Submeter apontamento",
                "footer-slogan": "Estudar melhor começa por partilhar.",
                "btn-sair": "Sair"
            },
            "en": {
                "menu-explorar": "Explore",
                "menu-como-funciona": "How it works",
                "menu-contactos": "Contacts",
                "btn-entrar": "Log In",
                "btn-criar-conta": "Sign Up",
                "menu-titulo": "Menu",
                "menu-lateral-inicio": "Home Page",
                "menu-lateral-explorar": "Explore Materials",
                "menu-lateral-partilhar": "Share Notes",
                "menu-lateral-meus": "My Notes",
                "menu-slogan": "Learn. Share. Grow.",
                "btn-conta-gratis": "Create free account",
                "upload-comunidade": "exe.cuTIva Community",
                "upload-titulo": "Share Notes",
                "upload-desc": "Help other students by sharing your study materials.",
                "label-titulo": "Title",
                "placeholder-titulo": "E.g.: Networking Summary — Chapter 1",
                "label-escola": "University",
                "opt-escola": "Select a university...",
                "label-curso": "Course",
                "opt-curso": "Select a university first...",
                "label-ano": "Academic Year",
                "opt-ano": "Select a course first...",
                "label-disciplina": "Subject",
                "opt-disciplina": "Select a year first...",
                "label-ficheiro": "File",
                "btn-submeter": "Submit Note",
                "footer-slogan": "Better studying starts with sharing.",
                "btn-sair": "Log Out"
            }
        };

        LanguageManager.instance = this;
    }

    setLanguage(lang) {
        if (this.dictionary[lang]) {
            this.currentLang = lang;
            localStorage.setItem('preferred_language', lang);
            this.applyToHTML();
        }
    }

    get(key) {
        return this.dictionary[this.currentLang][key] || key;
    }

    applyToHTML() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const languageStr = this.get(key);

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = languageStr;
            } else {
                element.innerHTML = languageStr;
            }
        });
    }
}

window.AppLanguage = new LanguageManager();
window.AppLanguage.applyToHTML();

console.log("✅ Dicionário carregado! Idioma atual:", window.AppLanguage.currentLang);