from django import template
from students.models import Student

register = template.Library()

@register.filter
def get_student_profile(user):
    """Get student profile for a user by matching username with student name"""
    try:
        student = Student.objects.get(name=user.username)
        return student
    except Student.DoesNotExist:
        # Try by first name
        try:
            student = Student.objects.get(name=user.first_name)
            return student
        except:
            return None
