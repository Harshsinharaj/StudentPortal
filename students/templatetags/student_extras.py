from django import template
from students.models import Student

register = template.Library()

@register.filter
def get_student_profile(user):
    return Student.objects.filter(name=user.username).first()