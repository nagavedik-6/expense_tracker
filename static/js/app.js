/* 
  FinSmart — Smart Expense Tracker App JS
  Interactive elements, theme switching persistence, sidebar toggles, and helper functions.
*/

document.addEventListener('DOMContentLoaded', function() {
    
    // Sidebar toggle for mobile devices
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarCollapse && sidebar) {
        sidebarCollapse.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside of it on mobile
        document.addEventListener('click', function(e) {
            if (sidebar.classList.contains('show') && !sidebar.contains(e.target) && e.target !== sidebarCollapse) {
                sidebar.classList.remove('show');
            }
        });
    }
    
    // Light / Dark Theme Toggle
    const themeToggler = document.getElementById('themeToggler');
    const body = document.body;
    const html = document.documentElement;
    
    if (themeToggler) {
        themeToggler.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            // Apply theme locally for instant feedback
            html.setAttribute('data-theme', newTheme);
            if (newTheme === 'dark') {
                body.classList.add('dark-mode');
                themeToggler.innerHTML = '<i class="bi bi-sun-fill"></i>';
            } else {
                body.classList.remove('dark-mode');
                themeToggler.innerHTML = '<i class="bi bi-moon-fill"></i>';
            }
            
            // Persist preference to Django session/database via API
            updateThemePreference(newTheme);
        });
    }

    function updateThemePreference(themeName) {
        // CSRF Token fetcher
        const csrfToken = getCookie('csrftoken');
        
        fetch('/accounts/profile/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `theme=${themeName}&phone=${encodeURIComponent(document.querySelector('[name="phone"]')?.value || '')}&currency=${encodeURIComponent(document.querySelector('[name="currency"]')?.value || 'INR')}`
        })
        .then(response => response.json().catch(() => ({})))
        .then(data => {
            console.log('Theme setting updated successfully');
        })
        .catch(err => {
            console.warn('Silent fallback for theme persistence');
        });
    }

    // Helper: Get Cookie (for CSRF token)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Auto-dismiss Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
