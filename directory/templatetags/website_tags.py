from urllib.parse import urlparse

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def website_icon(website, size=32):
    """
    Returns the favicon URL for a website.
    Falls back to a default icon if not found.

    Usage: {{ website|website_icon }} or {{ website|website_icon:48 }}
    """
    if not website or not website.url:
        return default_icon_url(size)

    # Extract domain from URL
    try:

        parsed = urlparse(website.url)
        domain = parsed.netloc or parsed.path.split('/')[0]
    except Exception:
        return default_icon_url(size)

    # Use multiple favicon services for reliability
    # 1. DuckDuckGo's favicon service (most reliable)
    # 2. Google Favicon API (fallback)
    # 3. Direct /favicon.ico attempt

    favicon_url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"

    return mark_safe(
        f"""
        <img src="{favicon_url}"
            alt="{website.title} icon"
            width="{size}"
            height="{size}"
            style="border-radius: 4px; object-fit: contain;"
            onerror="this.onerror=null; this.src='https://icons.duckduckgo.com/ip3/www.google.com.ico';"
            loading="lazy">
    """
    )



@register.simple_tag
def website_icon_url(website, size=32):
    """
    Returns just the favicon URL (not HTML).
    Use this when you want to control the img tag yourself.

    Usage: <img src="{% website_icon_url website 32 %}">
    """
    if not website or not website.url:
        return default_icon_url(size)

    try:

        parsed = urlparse(website.url)
        domain = parsed.netloc or parsed.path.split('/')[0]
    except Exception:
        return default_icon_url(size)

    return f"https://icons.duckduckgo.com/ip3/{domain}.ico"


def default_icon_url(size):
    """Returns a default placeholder icon URL."""
    return f"https://via.placeholder.com/{size}x{size}/64748b/ffffff?text=🌐"