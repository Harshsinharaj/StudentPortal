from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('home/', views.home, name='home'),
    path('students/', views.students_page, name='students'),
    path('add/', views.add_student, name='add'),
    path('delete/<int:id>/', views.delete_student, name='delete'),
    path('edit/<int:id>/', views.edit_student, name='edit'),
    path('search/', views.search_page, name='search'),
    path('analytics/', views.analytics_page, name='analytics'),
    path('courses/', views.courses_page, name='courses'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('import-csv/', views.import_csv, name='import_csv'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    
    # Feature 1: Attendance
    path('attendance/', views.attendance_page, name='attendance'),
    path('attendance-report/<int:student_id>/', views.attendance_report, name='attendance_report'),
    path('edit-attendance/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),
    path('delete-attendance/<int:attendance_id>/', views.delete_attendance, name='delete_attendance'),
    path('bulk-attendance/', views.bulk_attendance_update, name='bulk_attendance'),
    path('attendance-statistics/', views.attendance_statistics, name='attendance_statistics'),
    path('export-attendance/', views.export_attendance_csv, name='export_attendance'),
    
    # Feature 2: Assignments
    path('assignments/', views.assignments_page, name='assignments'),
    path('create-assignment/', views.create_assignment, name='create_assignment'),
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('submit-assignment/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    
    # Feature 3: Email Notifications
    path('email-notifications/', views.email_notifications, name='email_notifications'),
    
    # Feature 4: Performance Charts
    path('performance-charts/', views.performance_charts, name='performance_charts'),
    path('student-performance/<int:student_id>/', views.student_performance, name='student_performance'),
    
    # Feature 5: Certificates
    path('certificates/', views.certificates, name='certificates'),
    path('certificate/<int:certificate_id>/', views.view_certificate, name='view_certificate'),
    
    # Feature 6: SMS Alerts
    path('sms-alerts/', views.sms_alerts, name='sms_alerts'),
]