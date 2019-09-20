from django import template
from distribution.util import create_couple_block

register = template.Library()

@register.filter(name='couple_to_li')
def couple_to_li(couple):
    return create_couple_block(couple)