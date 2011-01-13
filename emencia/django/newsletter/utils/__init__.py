"""Utils for emencia.django.newsletter"""
from django.template import Context, Template


def render_string(template_string, context={}):
    """Shortcut for render a template string with a context"""
    t = Template(template_string)
    c = Context(context)
    return t.render(c)
