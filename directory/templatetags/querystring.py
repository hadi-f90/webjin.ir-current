from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    """
    Returns the current query string with updated parameters.
    Usage: ?{% query_string page=2 %} or ?{% query_string category="tech" page=1 %}
    """
    request = context.get('request')
    if not request:
        return ''

    # Get current GET parameters
    params = request.GET.copy()

    # Update with new values
    for key, value in kwargs.items():
        if value is not None and value != '':
            params[key] = value
        elif key in params:
            del params[key]

    return params.urlencode()