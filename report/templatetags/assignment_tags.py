from django import template

register = template.Library()

@register.simple_tag
def get_assignment(plan, line, date, shift):
    return plan.get_assignment(line=line, date=date, shift=shift)