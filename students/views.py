from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q, Avg, Count, Max, Min
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import date, timedelta
from .models import (Student, Announcement, Attendance, Assignment, AssignmentSubmission,
                     EmailNotification, PerformanceMetric, Certificate, SMSAlert)

def is_admin(user):
    return user.is_superuser or user.is_staff

# Create your views here.
# def home(request):
#     return HttpResponse("Welcome to Students Portal!")

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'login.html')

def logout_page(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    total_students = Student.objects.count()
    courses = Student.objects.values('course').distinct().count()
    avg_marks = Student.objects.aggregate(Avg('marks'))['marks__avg'] or 0
    pass_count = Student.objects.filter(marks__gte=50).count()
    pass_rate = 0
    if total_students > 0:
        pass_rate = round((pass_count / total_students) * 100)
    
    announcements = Announcement.objects.filter(is_active=True)[:5]
    
    data = {
        'title': 'Python Full Stack Development',
        'instructor': 'Gladden',
        'students_count': total_students,
        'courses_count': courses,
        'avg_score': round(avg_marks, 2),
        'pass_rate': f'{pass_rate}%',
        'announcements': announcements
    }
    return render(request, 'home.html', data)

@login_required(login_url='login')
def students_page(request):
    students = Student.objects.all().order_by('-marks')
    return render(request, 'students.html', {'students': students})


@login_required(login_url='login')
def search_page(request):
    q = request.GET.get('q', '').strip()
    course_filter = request.GET.get('course', '').strip()
    marks_min = request.GET.get('marks_min', '')
    marks_max = request.GET.get('marks_max', '')
    sort_by = request.GET.get('sort_by', '-marks')
    
    results = Student.objects.all()
    
    # Text search
    if q:
        results = results.filter(Q(name__icontains=q) | Q(course__icontains=q))
    
    # Filter by course
    if course_filter:
        results = results.filter(course__icontains=course_filter)
    
    # Filter by marks range
    if marks_min:
        try:
            results = results.filter(marks__gte=int(marks_min))
        except ValueError:
            pass
    
    if marks_max:
        try:
            results = results.filter(marks__lte=int(marks_max))
        except ValueError:
            pass
    
    # Sorting
    results = results.order_by(sort_by)
    
    # Get unique courses for dropdown
    all_courses = Student.objects.values_list('course', flat=True).distinct()

    return render(request, 'search.html', {
        'results': results,
        'q': q,
        'course_filter': course_filter,
        'marks_min': marks_min,
        'marks_max': marks_max,
        'sort_by': sort_by,
        'all_courses': all_courses
    })


@login_required(login_url='login')
def add_student(request):
    if request.method == "POST":
        name = request.POST.get('name')
        course = request.POST.get('course')
        marks = request.POST.get('marks')
        age = request.POST.get('age')
        profile_pic = request.FILES.get('profile_pic')

        if marks:
            try:
                if int(marks) > 100:
                    return render(request, 'add_student.html', {
                        'error': 'Marks cannot be greater than 100'
                    })
            except ValueError:
                return render(request, 'add_student.html', {'error': 'Marks must be a number'})

        Student.objects.create(
            name=name,
            course=course,
            marks=marks or 0,
            age=age or 18,
            profile_pic=profile_pic
        )

        return redirect('students')

    return render(request, 'add_student.html')


@user_passes_test(is_admin, login_url='home')
def delete_student(request, id):
    student = Student.objects.get(id=id)
    student.delete()
    return redirect('students')


@login_required(login_url='login')
def edit_student(request, id):
    student = Student.objects.get(id=id)

    if request.method == "POST":
        student.name = request.POST.get('name')
        student.course = request.POST.get('course')
        student.marks = request.POST.get('marks')
        student.age = request.POST.get('age')
        
        if 'profile_pic' in request.FILES:
            if student.profile_pic:
                student.profile_pic.delete()
            student.profile_pic = request.FILES['profile_pic']

        student.save()

        return redirect('students')

    return render(request, 'edit_student.html', {'student': student})


@login_required(login_url='login')
def analytics_page(request):
    total_students = Student.objects.count()
    avg_marks = Student.objects.aggregate(Avg('marks'))['marks__avg'] or 0
    total_courses = Student.objects.values('course').distinct().count()
    highest_marks = Student.objects.aggregate(Max('marks'))['marks__max'] or 0
    lowest_marks = Student.objects.aggregate(Min('marks'))['marks__min'] or 0
    pass_count = Student.objects.filter(marks__gte=50).count()
    fail_count = Student.objects.filter(marks__lt=50).count()
    
    top_students = Student.objects.order_by('-marks')[:5]
    course_stats = Student.objects.values('course').annotate(count=Count('id'), 
                                                               avg_marks=Avg('marks')).order_by('-count')

    data = {
        'total_students': total_students,
        'avg_marks': round(avg_marks, 2),
        'total_courses': total_courses,
        'highest_marks': highest_marks,
        'lowest_marks': lowest_marks,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'top_students': top_students,
        'course_stats': course_stats,
    }
    
    return render(request, 'analytics.html', data)


@login_required(login_url='login')
def courses_page(request):
    courses = Student.objects.values('course').distinct()
    course_list = []
    for c in courses:
        course_name = c['course']
        enrolled = Student.objects.filter(course=course_name).count()
        avg = Student.objects.filter(course=course_name).aggregate(Avg('marks'))['marks__avg'] or 0
        course_list.append({
            'name': course_name,
            'enrolled': enrolled,
            'avg_marks': round(avg, 2)
        })
    
    return render(request, 'courses.html', {'courses': course_list})

@login_required(login_url='login')
def export_csv(request):
    from .utils import export_students_csv
    students = Student.objects.all().order_by('-marks')
    return export_students_csv(students)

@login_required(login_url='login')
def import_csv(request):
    from .utils import import_students_csv
    
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            return render(request, 'import_csv.html', {'error': 'Please select a CSV file'})
        
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            return render(request, 'import_csv.html', {'error': 'Please upload a valid CSV file'})
        
        created_count, errors = import_students_csv(csv_file)
        
        return render(request, 'import_csv.html', {
            'success': f'Successfully imported {created_count} students',
            'errors': errors
        })
    
    return render(request, 'import_csv.html')

@user_passes_test(is_admin, login_url='home')
def admin_panel(request):
    total_students = Student.objects.count()
    total_users = User.objects.count()
    total_admins = User.objects.filter(is_staff=True).count()
    total_courses = Student.objects.values('course').distinct().count()
    
    data = {
        'total_students': total_students,
        'total_users': total_users,
        'total_admins': total_admins,
        'total_courses': total_courses,
    }
    
    return render(request, 'admin_panel.html', data)

# ============ FEATURE 1: ATTENDANCE TRACKING ============

@login_required(login_url='login')
def attendance_page(request):
    """View attendance records for students"""
    students = Student.objects.all()
    selected_date = request.GET.get('date', date.today())
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        student = Student.objects.get(id=student_id)
        attendance, created = Attendance.objects.update_or_create(
            student=student,
            date=selected_date,
            defaults={'status': status, 'remarks': remarks}
        )
        return redirect('attendance')
    
    attendance_records = Attendance.objects.filter(date=selected_date).select_related('student')
    
    data = {
        'students': students,
        'attendance_records': attendance_records,
        'selected_date': selected_date,
        'status_choices': Attendance._meta.get_field('status').choices,
    }
    
    return render(request, 'attendance.html', data)

@login_required(login_url='login')
def attendance_report(request, student_id):
    """View attendance report for a student"""
    student = Student.objects.get(id=student_id)
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = attendance_records.filter(status='absent').count()
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    data = {
        'student': student,
        'attendance_records': attendance_records,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': round(attendance_percentage, 2),
    }
    
    return render(request, 'attendance_report.html', data)

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def edit_attendance(request, attendance_id):
    """Edit existing attendance record"""
    attendance = Attendance.objects.get(id=attendance_id)
    
    if request.method == 'POST':
        attendance.status = request.POST.get('status')
        attendance.remarks = request.POST.get('remarks', '')
        attendance.save()
        return redirect('attendance')
    
    data = {
        'attendance': attendance,
        'status_choices': Attendance._meta.get_field('status').choices,
    }
    
    return render(request, 'edit_attendance.html', data)

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def delete_attendance(request, attendance_id):
    """Delete attendance record"""
    attendance = Attendance.objects.get(id=attendance_id)
    attendance.delete()
    return redirect('attendance')

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def bulk_attendance_update(request):
    """Bulk update attendance for multiple students"""
    if request.method == 'POST':
        date = request.POST.get('date')
        status = request.POST.get('status')
        student_ids = request.POST.getlist('student_ids')
        
        if not student_ids:
            return render(request, 'bulk_attendance.html', {'error': 'Select at least one student'})
        
        created_count = 0
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                attendance, created = Attendance.objects.update_or_create(
                    student=student,
                    date=date,
                    defaults={'status': status}
                )
                if created:
                    created_count += 1
            except Exception as e:
                pass
        
        return render(request, 'bulk_attendance.html', {
            'success': f'Updated attendance for {len(student_ids)} students'
        })
    
    students = Student.objects.all()
    
    data = {
        'students': students,
        'status_choices': Attendance._meta.get_field('status').choices,
    }
    
    return render(request, 'bulk_attendance.html', data)

@login_required(login_url='login')
def attendance_statistics(request):
    """View attendance statistics"""
    students = Student.objects.all()
    stats = []
    
    for student in students:
        total = Attendance.objects.filter(student=student).count()
        present = Attendance.objects.filter(student=student, status='present').count()
        absent = Attendance.objects.filter(student=student, status='absent').count()
        leave = Attendance.objects.filter(student=student, status='leave').count()
        late = Attendance.objects.filter(student=student, status='late').count()
        
        percentage = (present / total * 100) if total > 0 else 0
        
        stats.append({
            'student': student,
            'total': total,
            'present': present,
            'absent': absent,
            'leave': leave,
            'late': late,
            'percentage': round(percentage, 2),
        })
    
    data = {
        'stats': stats,
        'total_students': len(students),
    }
    
    return render(request, 'attendance_statistics.html', data)

@login_required(login_url='login')
def export_attendance_csv(request):
    """Export attendance records as CSV"""
    import csv
    
    student_id = request.GET.get('student_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Course', 'Date', 'Status', 'Remarks'])
    
    records = Attendance.objects.select_related('student')
    
    if student_id:
        records = records.filter(student_id=student_id)
    
    if date_from:
        records = records.filter(date__gte=date_from)
    
    if date_to:
        records = records.filter(date__lte=date_to)
    
    for record in records.order_by('-date'):
        writer.writerow([
            record.student.name,
            record.student.course,
            record.date,
            record.get_status_display(),
            record.remarks or ''
        ])
    
    return response

# ============ FEATURE 2: ASSIGNMENT MANAGEMENT ============

@login_required(login_url='login')
def assignments_page(request):
    """View all assignments"""
    assignments = Assignment.objects.all().order_by('-due_date')
    
    data = {
        'assignments': assignments,
        'total_assignments': assignments.count(),
    }
    
    return render(request, 'assignments.html', data)

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def create_assignment(request):
    """Create a new assignment (admin only)"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        course = request.POST.get('course')
        due_date = request.POST.get('due_date')
        total_marks = request.POST.get('total_marks', 100)
        
        Assignment.objects.create(
            title=title,
            description=description,
            course=course,
            due_date=due_date,
            total_marks=total_marks,
            created_by=request.user.username
        )
        return redirect('assignments')
    
    courses = Student.objects.values('course').distinct()
    
    data = {
        'courses': courses,
    }
    
    return render(request, 'create_assignment.html', data)

@login_required(login_url='login')
def assignment_detail(request, assignment_id):
    """View assignment details and submissions"""
    assignment = Assignment.objects.get(id=assignment_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    
    # Check if current user is a student and get their submission
    student_submission = None
    try:
        student = Student.objects.get(name=request.user.username)
        student_submission = AssignmentSubmission.objects.get(assignment=assignment, student=student)
    except:
        pass
    
    data = {
        'assignment': assignment,
        'submissions': submissions,
        'student_submission': student_submission,
        'can_submit': not student_submission and timezone.now() < assignment.due_date,
    }
    
    return render(request, 'assignment_detail.html', data)

@login_required(login_url='login')
def submit_assignment(request, assignment_id):
    """Submit assignment"""
    if request.method == 'POST':
        assignment = Assignment.objects.get(id=assignment_id)
        
        try:
            student = Student.objects.get(name=request.user.username)
            
            if 'submission_file' in request.FILES:
                submission_file = request.FILES['submission_file']
                is_late = timezone.now() > assignment.due_date
                
                submission, created = AssignmentSubmission.objects.update_or_create(
                    assignment=assignment,
                    student=student,
                    defaults={
                        'submission_file': submission_file,
                        'is_late': is_late,
                    }
                )
                
                return redirect('assignment_detail', assignment_id=assignment_id)
        except Exception as e:
            return render(request, 'submit_assignment.html', {'error': str(e)})
    
    assignment = Assignment.objects.get(id=assignment_id)
    
    return render(request, 'submit_assignment.html', {'assignment': assignment})

# ============ FEATURE 3: EMAIL NOTIFICATIONS ============

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def email_notifications(request):
    """Send bulk email notifications to students"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        recipient_ids = request.POST.getlist('recipients')
        
        email_notif = EmailNotification.objects.create(
            subject=subject,
            message=message,
            status='draft'
        )
        
        if recipient_ids:
            recipients = Student.objects.filter(id__in=recipient_ids)
            email_notif.recipients.set(recipients)
            email_notif.status = 'sent'
            email_notif.sent_at = timezone.now()
            email_notif.save()
        
        return redirect('email_notifications')
    
    students = Student.objects.all()
    notifications = EmailNotification.objects.all().order_by('-created_at')
    
    data = {
        'students': students,
        'notifications': notifications,
    }
    
    return render(request, 'email_notifications.html', data)

# ============ FEATURE 4: PERFORMANCE CHARTS ============

@login_required(login_url='login')
def performance_charts(request):
    """Display performance metrics and charts"""
    students = Student.objects.all()
    
    # Prepare data for charts
    chart_data = []
    for student in students:
        try:
            metric = PerformanceMetric.objects.get(student=student)
        except:
            metric = PerformanceMetric.objects.create(student=student)
        
        chart_data.append({
            'id': student.id, 
            'name': student.name,
            'marks': student.marks,
            'attendance': metric.attendance_percentage,
            'assignments': metric.average_assignment_marks,
        })
    
    data = {
        'students': students,
        'chart_data': chart_data,
        'total_students': len(students),
        'average_marks': Student.objects.aggregate(Avg('marks'))['marks__avg'] or 0,
    }
    
    return render(request, 'performance_charts.html', data)

@login_required(login_url='login')
def student_performance(request, student_id):
    """View individual student performance"""
    student = Student.objects.get(id=student_id)
    
    try:
        metric = PerformanceMetric.objects.get(student=student)
    except:
        metric = PerformanceMetric.objects.create(student=student)
    
    assignments = AssignmentSubmission.objects.filter(student=student)
    attendance = Attendance.objects.filter(student=student)
    
    data = {
        'student': student,
        'metric': metric,
        'assignments': assignments,
        'attendance_records': attendance.order_by('-date')[:10],
    }
    
    return render(request, 'student_performance.html', data)

# ============ FEATURE 5: CERTIFICATE GENERATION ============

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def certificates(request):
    """Generate and manage certificates"""
    certificates = Certificate.objects.all().select_related('student')
    students = Student.objects.all()
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        certificate_type = request.POST.get('certificate_type', 'completion')
        course = request.POST.get('course')
        
        student = Student.objects.get(id=student_id)
        
        certificate, created = Certificate.objects.update_or_create(
            student=student,
            course=course,
            defaults={'certificate_type': certificate_type}
        )
        
        return redirect('certificates')
    
    data = {
        'certificates': certificates,
        'students': students,
        'certificate_types': Certificate._meta.get_field('certificate_type').choices,
    }
    
    return render(request, 'certificates.html', data)

@login_required(login_url='login')
def view_certificate(request, certificate_id):
    """View and download certificate"""
    certificate = Certificate.objects.get(id=certificate_id)
    
    data = {
        'certificate': certificate,
    }
    
    return render(request, 'view_certificate.html', data)

# ============ FEATURE 6: SMS ALERTS ============

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def sms_alerts(request):
    """Send SMS alerts to students"""
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        alert_type = request.POST.get('alert_type')
        message = request.POST.get('message')
        
        for student_id in student_ids:
            student = Student.objects.get(id=student_id)
            # In production, use Twilio or similar service
            SMSAlert.objects.create(
                student=student,
                phone_number=request.POST.get(f'phone_{student_id}', ''),
                message=message,
                alert_type=alert_type,
                status='sent'
            )
        
        return redirect('sms_alerts')
    
    students = Student.objects.all()
    alerts = SMSAlert.objects.all().order_by('-created_at')
    
    data = {
        'students': students,
        'alerts': alerts,
        'alert_types': SMSAlert._meta.get_field('alert_type').choices,
    }
    
    return render(request, 'sms_alerts.html', data)
# ============  ============