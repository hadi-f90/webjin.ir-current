# directory/templatetags/website_tags.py

from django import template
from django.utils.safestring import mark_safe
import hashlib

register = template.Library()


@register.filter
def website_icon(website, size=32):
    """
    Returns the website's own favicon.ico
    Falls back to a generated initial-based icon.
    """
    if not website or not website.url:
        return default_icon(size, '🌐')

    try:
        from urllib.parse import urlparse
        parsed = urlparse(website.url)
        domain = parsed.netloc or parsed.path.split('/')[0]

        if domain:
            # Try to get favicon from the website itself
            favicon_url = f"https://{domain}/favicon.ico"

            return mark_safe(f'''
                <img src="{favicon_url}"
                     alt="{website.title}"
                     width="{size}"
                     height="{size}"
                     style="border-radius: 6px; object-fit: contain; background: white;"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                     loading="lazy">
                <div class="website-icon-fallback" style="display: none; width: {size}px; height: {size}px;
                     border-radius: 6px; background: {get_color_from_domain(domain)};
                     color: white; font-size: {size//2}px; font-weight: bold;
                     display: flex; align-items: center; justify-content: center;">
                    {get_initial(website.title)}
                </div>
            ''')
    except Exception:
        pass

    return default_icon(size, get_initial(website.title))


@register.simple_tag
def website_icon_url(website):
    """Returns just the favicon URL."""
    if not website or not website.url:
        return ''

    try:
        from urllib.parse import urlparse
        parsed = urlparse(website.url)
        domain = parsed.netloc or parsed.path.split('/')[0]

        if domain:
            return f"https://{domain}/favicon.ico"
    except Exception:
        pass

    return ''


def get_initial(title):
    """Get first letter/character of title for fallback icon."""
    if not title:
        return '?'
    # Get first Persian/English word
    words = title.split()
    first_word = words[0] if words else title
    return first_word[0].upper()


def get_color_from_domain(domain):
    """Generate a consistent color from domain name."""
    colors = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
    ]
    hash_value = int(hashlib.md5(domain.encode()).hexdigest(), 16)
    return colors[hash_value % len(colors)]


def default_icon(size, content):
    """Default placeholder icon."""
    return mark_safe(f'''
        <div style="width: {size}px; height: {size}px; border-radius: 6px;
             background: #64748b; color: white; font-size: {size//2}px;
             display: flex; align-items: center; justify-content: center;">
            {content}
        </div>
    ''')