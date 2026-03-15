from django.db import models
from django.utils import timezone
from datetime import date

class Student(models.Model):
    name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    marks = models.IntegerField()
    age = models.IntegerField(default=18)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.name

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    announcement_type = models.CharField(max_length=20, choices=[
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
    ], default='info')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# Attendance Tracking
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
        ('late', 'Late'),
    ], default='present')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.status})"

# Assignment Management
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.CharField(max_length=100)
    due_date = models.DateTimeField()
    total_marks = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, default='Admin')

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return self.title

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='submissions/')
    marks_obtained = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title}"

# Email Notification
class EmailNotification(models.Model):
    subject = models.CharField(max_length=200)
    message = models.TextField()
    recipients = models.ManyToManyField(Student)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
    ], default='draft')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.subject

# Performance Charts
class PerformanceMetric(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='performance_metric')
    total_assignments = models.IntegerField(default=0)
    completed_assignments = models.IntegerField(default=0)
    average_assignment_marks = models.FloatField(default=0)
    attendance_percentage = models.FloatField(default=0)
    total_attendance_days = models.IntegerField(default=0)
    present_days = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Performance - {self.student.name}"

# Certificate
class Certificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    course = models.CharField(max_length=100)
    issue_date = models.DateField(auto_now_add=True)
    certificate_type = models.CharField(max_length=20, choices=[
        ('completion', 'Completion'),
        ('achievement', 'Achievement'),
        ('merit', 'Merit'),
    ], default='completion')
    certificate_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"Certificate - {self.student.name}"

# SMS Alert
class SMSAlert(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sms_alerts')
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=[
        ('attendance', 'Attendance'),
        ('marks', 'Marks'),
        ('assignment', 'Assignment'),
        ('announcement', 'Announcement'),
        ('general', 'General'),
    ], default='general')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ], default='pending')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SMS - {self.student.name} ({self.alert_type})"
