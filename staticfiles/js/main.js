// Custom JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// Keep navbar solid and mark scroll state for shadow emphasis
document.addEventListener('DOMContentLoaded', function () {
    var nav = document.querySelector('.navbar.sticky-top, .navbar.navbar-theme');
    if (!nav) return;
    function onScroll() {
        if (window.scrollY > 8) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    }
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
});
