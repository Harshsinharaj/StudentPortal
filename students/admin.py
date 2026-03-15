from django.contrib import admin
from .models import (Student, Announcement, Attendance, Assignment, AssignmentSubmission,
                     EmailNotification, PerformanceMetric, Certificate, SMSAlert)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'marks', 'age', 'profile_pic_preview')
    list_filter = ('course', 'marks')
    search_fields = ('name', 'course')
    readonly_fields = ('profile_pic_preview',)
    
    def profile_pic_preview(self, obj):
        if obj.profile_pic:
            return f'<img src="{obj.profile_pic.url}" width="50" height="50" style="border-radius: 50%; object-fit: cover;"/>'
        return 'No picture'
    
    profile_pic_preview.short_description = 'Picture Preview'
    profile_pic_preview.allow_tags = True

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'announcement_type', 'is_active', 'created_at')
    list_filter = ('announcement_type', 'is_active', 'created_at')
    search_fields = ('title', 'message')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'created_at')
    list_filter = ('status', 'date', 'student__course')
    search_fields = ('student__name',)
    date_hierarchy = 'date'
    list_editable = ('status',)

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'total_marks', 'created_by')
    list_filter = ('course', 'due_date', 'created_at')
    search_fields = ('title', 'course')
    readonly_fields = ('created_at',)

class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'marks_obtained', 'submitted_at', 'is_late')
    list_filter = ('assignment', 'is_late', 'submitted_at')
    search_fields = ('student__name', 'assignment__title')
    readonly_fields = ('submitted_at',)
    list_editable = ('marks_obtained',)

class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'message')
    readonly_fields = ('created_at', 'sent_at')

class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('student', 'attendance_percentage', 'average_assignment_marks', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('student__name',)
    readonly_fields = ('updated_at',)

class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'certificate_type', 'issue_date')
    list_filter = ('certificate_type', 'issue_date', 'course')
    search_fields = ('student__name', 'course')
    readonly_fields = ('generated_at', 'issue_date')

class SMSAlertAdmin(admin.ModelAdmin):
    list_display = ('student', 'alert_type', 'status', 'created_at')
    list_filter = ('alert_type', 'status', 'created_at')
    search_fields = ('student__name', 'phone_number')
    readonly_fields = ('created_at', 'sent_at')

admin.site.register(Student, StudentAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentSubmission, AssignmentSubmissionAdmin)
admin.site.register(EmailNotification, EmailNotificationAdmin)
admin.site.register(PerformanceMetric, PerformanceMetricAdmin)
admin.site.register(Certificate, CertificateAdmin)
admin.site.register(SMSAlert, SMSAlertAdmin)
