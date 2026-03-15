import csv
from io import StringIO
from django.http import HttpResponse
from .models import Student

def export_students_csv(students):
    """Export students to CSV format"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Course', 'Marks', 'Age'])
    
    for student in students:
        writer.writerow([
            student.id,
            student.name,
            student.course,
            student.marks,
            student.age
        ])
    
    return response

def import_students_csv(csv_file):
    """Import students from CSV file"""
    try:
        decoded_file = csv_file.read().decode('utf-8')
        reader = csv.DictReader(StringIO(decoded_file))
        
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                Student.objects.create(
                    name=row.get('Name', '').strip(),
                    course=row.get('Course', '').strip(),
                    marks=int(row.get('Marks', 0)),
                    age=int(row.get('Age', 18))
                )
                created_count += 1
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return created_count, errors
    except Exception as e:
        return 0, [str(e)]
