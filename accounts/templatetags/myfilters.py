from django import template
from ckeditor.fields import CKEditorWidget

register = template.Library()

@register.filter(name='is_ckeditor_field')
def is_ckeditor_field(value):
    return isinstance(value, CKEditorWidget)