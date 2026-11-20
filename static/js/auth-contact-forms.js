(function () {
    'use strict';

    const genericError = 'ارسال فرم با مشکل روبه‌رو شد. لطفاً دوباره تلاش کنید.';
    const validationError = 'لطفاً اطلاعات واردشده را بررسی کنید.';

    function errorMessages(value) {
        if (Array.isArray(value)) {
            return value.map(String).filter(Boolean);
        }
        return value ? [String(value)] : [];
    }

    function addDescription(control, id) {
        const ids = new Set((control.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean));
        ids.add(id);
        control.setAttribute('aria-describedby', Array.from(ids).join(' '));
    }

    function removeDescription(control, id) {
        const ids = (control.getAttribute('aria-describedby') || '')
            .split(/\s+/)
            .filter((descriptionId) => descriptionId && descriptionId !== id);
        if (ids.length) {
            control.setAttribute('aria-describedby', ids.join(' '));
        } else {
            control.removeAttribute('aria-describedby');
        }
    }

    function controlsIn(group) {
        return Array.from(group.querySelectorAll('input, select, textarea'))
            .filter((control) => control.type !== 'hidden');
    }

    function connectInitialErrors(form) {
        form.querySelectorAll('[data-field-group]').forEach((group) => {
            const controls = controlsIn(group);
            const renderedErrors = Array.from(group.querySelectorAll('.invalid-feedback'))
                .filter((node) => !node.hasAttribute('data-field-feedback') && node.textContent.trim());

            if (renderedErrors.length) {
                controls.forEach((control) => {
                    control.setAttribute('aria-invalid', 'true');
                    renderedErrors.forEach((error) => {
                        if (error.id) addDescription(control, error.id);
                    });
                });
            }
        });
    }

    function findGroup(form, key) {
        return Array.from(form.querySelectorAll('[data-field-group]'))
            .find((group) => group.dataset.fieldGroup === key);
    }

    function clearFieldErrors(form) {
        form.querySelectorAll('[data-field-group]').forEach((group) => {
            const controls = controlsIn(group);
            group.querySelectorAll('.invalid-feedback').forEach((node) => {
                if (node.id) controls.forEach((control) => removeDescription(control, node.id));
                if (node.hasAttribute('data-field-feedback')) {
                    node.textContent = '';
                    node.hidden = true;
                    node.classList.remove('d-block');
                } else {
                    node.remove();
                }
            });
            controls.forEach((control) => {
                control.setAttribute('aria-invalid', 'false');
            });
        });
    }

    function showFieldError(group, messages) {
        const feedback = group.querySelector('[data-field-feedback]');
        if (!feedback || !messages.length) return;

        feedback.textContent = messages.join(' ');
        feedback.hidden = false;
        feedback.classList.add('d-block');
        controlsIn(group).forEach((control) => {
            control.setAttribute('aria-invalid', 'true');
            addDescription(control, feedback.id);
        });
    }

    function showSummary(form, message, details) {
        const summary = form.querySelector('[data-form-summary]');
        if (!summary) return;

        summary.replaceChildren();
        const heading = document.createElement('p');
        heading.className = 'mb-1';
        heading.textContent = message || validationError;
        summary.appendChild(heading);

        if (details.length) {
            const list = document.createElement('ul');
            list.className = 'mb-0';
            details.forEach((detail) => {
                const item = document.createElement('li');
                item.textContent = detail;
                list.appendChild(item);
            });
            summary.appendChild(list);
        }

        summary.classList.remove('d-none');
        summary.focus();
    }

    function renderErrors(form, data) {
        clearFieldErrors(form);

        const errors = data && data.errors && typeof data.errors === 'object'
            ? data.errors
            : {};
        const summaryErrors = [];

        Object.entries(errors).forEach(([key, value]) => {
            const messages = errorMessages(value);
            const group = key !== '__all__' && key !== 'non_field_errors'
                ? findGroup(form, key)
                : null;
            if (group) {
                showFieldError(group, messages);
            } else {
                summaryErrors.push(...messages);
            }
        });

        showSummary(form, (data && data.message) || validationError, summaryErrors);
    }

    function setPending(form, pending, button, originalContent) {
        form.setAttribute('aria-busy', pending ? 'true' : 'false');
        if (!button) return;

        button.disabled = pending;
        if (button.tagName === 'INPUT') {
            button.value = pending ? 'در حال ارسال…' : originalContent;
        } else {
            button.innerHTML = pending
                ? '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>در حال ارسال…'
                : originalContent;
        }
    }

    function csrfToken(form) {
        const field = form.querySelector('input[name="csrfmiddlewaretoken"]');
        if (field && field.value) return field.value;

        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta && meta.content && meta.content !== 'NOTPROVIDED') return meta.content;

        const cookie = document.cookie.split('; ').find((part) => part.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
    }

    function statusMessage(form, message, success) {
        const status = form.querySelector('[data-form-status]');
        if (!status) return;
        status.className = success ? 'alert alert-success' : 'alert alert-danger';
        status.textContent = message;
        status.classList.remove('d-none');
        status.setAttribute('role', success ? 'status' : 'alert');
        status.setAttribute('aria-live', success ? 'polite' : 'assertive');
        status.focus();
    }

    function enhance(form) {
        connectInitialErrors(form);
        const summary = form.querySelector('[data-form-summary]');
        const status = form.querySelector('[data-form-status]');
        if (summary && !summary.textContent.trim()) summary.classList.add('d-none');

        form.addEventListener('submit', async (event) => {
            if (form.dataset.ajaxForm !== '1') return;

            event.preventDefault();
            if (summary) {
                summary.classList.add('d-none');
                summary.replaceChildren();
            }
            if (status) {
                status.classList.add('d-none');
                status.textContent = '';
            }
            clearFieldErrors(form);

            const button = form.querySelector('button[type="submit"], input[type="submit"]');
            const originalContent = button
                ? (button.tagName === 'INPUT' ? button.value : button.innerHTML)
                : '';
            setPending(form, true, button, originalContent);

            const headers = {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            };
            const token = csrfToken(form);
            if (token) headers['X-CSRFToken'] = token;

            try {
                const response = await fetch(form.action || window.location.href, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: headers,
                    credentials: 'same-origin'
                });
                let data = null;
                try {
                    data = await response.json();
                } catch (_parseError) {
                    data = null;
                }

                if (response.ok && data && data.status === 'success') {
                    if (data.redirect || form.dataset.successUrl) {
                        window.location.assign(data.redirect || form.dataset.successUrl);
                        return;
                    }
                    statusMessage(form, data.message || 'درخواست شما با موفقیت انجام شد.', true);
                    setPending(form, false, button, originalContent);
                    return;
                }

                if (data && data.status === 'error') {
                    renderErrors(form, data);
                } else {
                    statusMessage(form, genericError);
                }
                setPending(form, false, button, originalContent);
            } catch (_networkError) {
                statusMessage(form, genericError);
                setPending(form, false, button, originalContent);
            }
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('form[data-ajax-form="1"]').forEach(enhance);
    });
})();
