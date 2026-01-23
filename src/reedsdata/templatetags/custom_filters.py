from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, '')


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary"""
    return dictionary.get(key, '')


@register.filter
def is_evaluation_field(parameter_name):
    """Check if a parameter is an evaluation field"""
    evaluation_fields = [
        'playing_ease',
        'intonation',
        'tone_color',
        'response',
        'counts_rehearsal',
        'counts_concert',
        'global_quality_first_impression',
        'global_quality_second_impression',
        'global_quality_third_impression',
        'note'
    ]
    return parameter_name in evaluation_fields
