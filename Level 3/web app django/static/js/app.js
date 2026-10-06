/**
 * TaskFlow Application Client Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss toasts after 5 seconds
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.4s ease';
            setTimeout(() => toast.remove(), 400);
        }, 5000);
    });

    // 2. Demo login credential autofill helper
    const demoPills = document.querySelectorAll('.demo-pill');
    demoPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const user = pill.getAttribute('data-user');
            const pass = pill.getAttribute('data-pass');
            const userInput = document.querySelector('input[name="username"]');
            const passInput = document.querySelector('input[name="password"]');

            if (userInput && passInput) {
                userInput.value = user;
                passInput.value = pass;
                userInput.focus();
                
                // Visual feedback pulse
                pill.style.transform = 'scale(0.95)';
                setTimeout(() => pill.style.transform = '', 150);
            }
        });
    });

    // 3. Password visibility toggle
    const toggleButtons = document.querySelectorAll('.toggle-password-btn');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    btn.textContent = '🔒';
                } else {
                    input.type = 'password';
                    btn.textContent = '👁️';
                }
            }
        });
    });

    // 4. Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // 5. Close sidebar on click outside on small screens
    document.addEventListener('click', (e) => {
        if (sidebar && sidebar.classList.contains('open')) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });
});
