/**
 * Controle do tema (claro/escuro) e utilidades de UI para a aplicação de Lista de Tarefas
 */

// Loading states
function showLoading(button) {
    const originalText = button.textContent;
    button.dataset.originalText = originalText;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Carregando...';
}

function hideLoading(button) {
    button.disabled = false;
    button.textContent = button.dataset.originalText;
}

// Toast notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast show position-fixed bottom-0 end-0 m-3 bg-${type === 'success' ? 'success' : 'danger'}`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body text-white">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Task filtering
function filterTasks(searchTerm) {
    const tasks = document.querySelectorAll('.task-item');
    tasks.forEach(task => {
        const text = task.textContent.toLowerCase();
        task.style.display = text.includes(searchTerm.toLowerCase()) ? '' : 'none';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const themeIcon = document.querySelector('#theme-toggle i');
    
    // Verifica se há um tema salvo no localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        htmlElement.setAttribute('data-theme', savedTheme);
        updateIcon(savedTheme);
    } else {
        // Verifica se o usuário prefere tema escuro no sistema
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
        if (prefersDarkScheme.matches) {
            htmlElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            updateIcon('dark');
        }
    }
    
    // Função para atualizar o ícone do botão
    function updateIcon(theme) {
        if (theme === 'dark') {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
            document.body.classList.add('dark-mode');
        } else {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
            document.body.classList.remove('dark-mode');
        }
        localStorage.setItem('darkMode', theme === 'dark');
    }
    
    // Evento de clique para alternar tema
    themeToggle.addEventListener('click', function() {
        const currentTheme = htmlElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        // Aplica animação ao alternar
        document.body.classList.add('theme-transition');
        
        // Atualiza o tema
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateIcon(newTheme);
        
        // Remove a classe de animação após a transição
        setTimeout(() => {
            document.body.classList.remove('theme-transition');
        }, 300);
    });
}); 