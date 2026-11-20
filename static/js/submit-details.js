(function () {
    'use strict';

    const toggle = document.getElementById('toggleDetailsBtn');
    const details = document.getElementById('extraDetails');
    const icon = document.getElementById('toggleIcon');

    if (!toggle || !details || !icon) return;

    function syncToggleState() {
        const expanded = !details.hidden;
        toggle.setAttribute('aria-expanded', String(expanded));
        toggle.classList.toggle('active', expanded);
        details.classList.toggle('d-none', !expanded);
        icon.className = expanded
            ? 'bi bi-chevron-up text-primary'
            : 'bi bi-chevron-expand text-primary';
    }

    syncToggleState();

    toggle.addEventListener('click', function () {
        details.hidden = !details.hidden;
        syncToggleState();
    });
})();
