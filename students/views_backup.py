from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def student_list(request):
    """List all students"""
    return render(request, 'students/student_list.html', {
        'title': 'Students',
        'students': [],  # Placeholder
    })

@login_required
def student_add(request):
    """Add new student"""
    return render(request, 'students/student_add.html', {
        'title': 'Add Student',
    })

@login_required
def student_detail(request, student_id):
    """Student detail view"""
    return render(request, 'students/student_detail.html', {
        'title': 'Student Details',
        'student_id': student_id,
    })

@login_required
def student_report_card(request, student_id):
    """Student report card"""
    return render(request, 'students/student_report_card.html', {
        'title': 'Report Card',
        'student_id': student_id,
    })

@login_required
def attendance_overview(request):
    """Attendance overview"""
    return render(request, 'students/attendance_overview.html', {
        'title': 'Attendance Overview',
    })

@login_required
def take_attendance(request, class_id):
    """Take attendance for class"""
    return render(request, 'students/take_attendance.html', {
        'title': 'Take Attendance',
        'class_id': class_id,
    })

@login_required
def grades_overview(request):
    """Grades overview"""
    return render(request, 'students/grades_overview.html', {
        'title': 'Grades Overview',
    })

@login_required
def enter_grades(request, assessment_id):
    """Enter grades for assessment"""
    return render(request, 'students/enter_grades.html', {
        'title': 'Enter Grades',
        'assessment_id': assessment_id,
    })
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Filter by class
    class_filter = request.GET.get('class', '')
    if class_filter:
        students = students.filter(current_class_id=class_filter)
    
    # Filter by grade
    grade_filter = request.GET.get('grade', '')
    if grade_filter:
        students = students.filter(current_class__grade_id=grade_filter)
    
    # Pagination
    paginator = Paginator(students, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    if request.user.role != 'owner' and not request.user.is_superuser:
        classes = StudentClass.objects.filter(grade__school=request.user.school)
        grades = Grade.objects.filter(school=request.user.school)
    else:
        classes = StudentClass.objects.all()
        grades = Grade.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'classes': classes,
        'grades': grades,
        'class_filter': class_filter,
        'grade_filter': grade_filter,
    }
    
    return render(request, 'students/student_list.html', context)


@login_required
@permission_required('manage_students')
@audit_action('student_add')
def student_add(request):
    """Add new student"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            if request.user.role != 'owner' and not request.user.is_superuser:
                student.user.school = request.user.school
            student.save()
            messages.success(request, f'Student {student.user.get_full_name()} added successfully!')
            return redirect('student_detail', student_id=student.pk)
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'students/student_form.html', {
        'form': form,
        'title': 'Add New Student'
    })


@login_required
@permission_required('view_students')
@audit_action('student_detail_view')
def student_detail(request, student_id):
    """Student detail view"""
    student = get_object_or_404(Student, pk=student_id)
    
    # Check access permissions
    if request.user.role == 'parent':
        # Parents can only view their own children
        if not student.user.parent_children.filter(parent=request.user).exists():
            messages.error(request, 'You can only view your own children.')
            return redirect('dashboard')
    elif request.user.role == 'student':
        # Students can only view their own profile
        if student.user != request.user:
            messages.error(request, 'You can only view your own profile.')
            return redirect('dashboard')
    elif request.user.role not in ['owner', 'admin'] and not request.user.is_superuser:
        # Teachers can only view students in their school
        if student.user.school != request.user.school:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    # Get student's recent grades
    recent_grades = StudentGrade.objects.filter(student=student).select_related(
        'assessment', 'assessment__subject'
    ).order_by('-assessment__date_conducted')[:10]
    
    # Get attendance summary for current term
    current_term = Term.objects.filter(is_current=True).first()
    attendance_summary = {}
    if current_term:
        attendance_records = Attendance.objects.filter(
            student=student,
            date__range=[current_term.start_date, current_term.end_date]
        )
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='present').count()
        attendance_summary = {
            'total_days': total_days,
            'present_days': present_days,
            'percentage': (present_days / total_days * 100) if total_days > 0 else 0
        }
    
    # Get student documents
    documents = StudentDocument.objects.filter(student=student).order_by('-uploaded_at')
    
    context = {
        'student': student,
        'recent_grades': recent_grades,
        'attendance_summary': attendance_summary,
        'documents': documents,
        'current_term': current_term,
    }
    
    return render(request, 'students/student_detail.html', context)


@login_required
@role_required(['teacher', 'admin', 'owner'])
@audit_action('attendance_overview')
def attendance_overview(request):
    """Attendance overview for teachers and admins"""
    today = timezone.now().date()
    
    # Get current term
    current_term = Term.objects.filter(is_current=True).first()
    
    # Get classes based on user role
    if request.user.role == 'teacher':
        classes = StudentClass.objects.filter(teacher=request.user)
    else:
        if request.user.role != 'owner' and not request.user.is_superuser:
            classes = StudentClass.objects.filter(grade__school=request.user.school)
        else:
            classes = StudentClass.objects.all()
    
    # Get attendance stats for today
    today_attendance = {}
    for cls in classes:
        students_count = cls.current_students.count()
        present_count = Attendance.objects.filter(
            student__current_class=cls,
            date=today,
            status='present'
        ).count()
        today_attendance[cls.id] = {
            'total': students_count,
            'present': present_count,
            'absent': students_count - present_count,
            'percentage': (present_count / students_count * 100) if students_count > 0 else 0
        }
    
    context = {
        'classes': classes,
        'today_attendance': today_attendance,
        'current_term': current_term,
        'today': today,
    }
    
    return render(request, 'students/attendance_overview.html', context)


@login_required
@role_required(['teacher', 'admin', 'owner'])
@audit_action('take_attendance')
def take_attendance(request, class_id):
    """Take attendance for a specific class"""
    student_class = get_object_or_404(StudentClass, pk=class_id)
    
    # Check permission
    if request.user.role == 'teacher' and student_class.teacher != request.user:
        messages.error(request, 'You can only take attendance for your own classes.')
        return redirect('attendance_overview')
    
    today = timezone.now().date()
    students = student_class.current_students.all().order_by('student_id')
    
    if request.method == 'POST':
        # Process attendance data
        for student in students:
            status = request.POST.get(f'attendance_{student.id}')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            
            if status:
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    date=today,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': request.user
                    }
                )
                if not created:
                    attendance.status = status
                    attendance.remarks = remarks
                    attendance.marked_by = request.user
                    attendance.save()
        
        messages.success(request, f'Attendance recorded for {student_class.name}')
        return redirect('attendance_overview')
    
    # Get existing attendance for today
    existing_attendance = {
        att.student_id: att for att in 
        Attendance.objects.filter(date=today, student__in=students)
    }
    
    context = {
        'student_class': student_class,
        'students': students,
        'today': today,
        'existing_attendance': existing_attendance,
        'status_choices': Attendance.STATUS_CHOICES,
    }
    
    return render(request, 'students/take_attendance.html', context)


@login_required
@role_required(['teacher', 'admin', 'owner'])
@audit_action('grades_overview')
def grades_overview(request):
    """Grades overview"""
    # Get assessments based on user role
    if request.user.role == 'teacher':
        assessments = Assessment.objects.filter(
            created_by=request.user
        ).select_related('subject', 'student_class', 'term')
    else:
        if request.user.role != 'owner' and not request.user.is_superuser:
            assessments = Assessment.objects.filter(
                subject__school=request.user.school
            ).select_related('subject', 'student_class', 'term')
        else:
            assessments = Assessment.objects.all().select_related('subject', 'student_class', 'term')
    
    # Get recent assessments
    recent_assessments = assessments.order_by('-date_conducted')[:10]
    
    # Get pending grade entries (assessments without all grades entered)
    pending_assessments = []
    for assessment in recent_assessments:
        total_students = assessment.student_class.current_students.count()
        graded_students = assessment.student_grades.count()
        if graded_students < total_students:
            pending_assessments.append({
                'assessment': assessment,
                'total_students': total_students,
                'graded_students': graded_students,
                'pending': total_students - graded_students
            })
    
    context = {
        'recent_assessments': recent_assessments,
        'pending_assessments': pending_assessments,
    }
    
    return render(request, 'students/grades_overview.html', context)


@login_required
@role_required(['teacher', 'admin', 'owner'])
@audit_action('enter_grades')
def enter_grades(request, assessment_id):
    """Enter grades for an assessment"""
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    
    # Check permission
    if request.user.role == 'teacher' and assessment.created_by != request.user:
        messages.error(request, 'You can only enter grades for your own assessments.')
        return redirect('grades_overview')
    
    students = assessment.student_class.current_students.all().order_by('student_id')
    
    if request.method == 'POST':
        # Process grade data
        for student in students:
            marks = request.POST.get(f'marks_{student.id}')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            
            if marks:
                try:
                    marks = float(marks)
                    if 0 <= marks <= assessment.total_marks:
                        grade, created = StudentGrade.objects.get_or_create(
                            student=student,
                            assessment=assessment,
                            defaults={
                                'marks_obtained': marks,
                                'remarks': remarks,
                                'entered_by': request.user
                            }
                        )
                        if not created:
                            grade.marks_obtained = marks
                            grade.remarks = remarks
                            grade.entered_by = request.user
                            grade.save()
                except ValueError:
                    continue
        
        messages.success(request, f'Grades entered for {assessment.title}')
        return redirect('grades_overview')
    
    # Get existing grades
    existing_grades = {
        grade.student_id: grade for grade in 
        StudentGrade.objects.filter(assessment=assessment)
    }
    
    context = {
        'assessment': assessment,
        'students': students,
        'existing_grades': existing_grades,
    }
    
    return render(request, 'students/enter_grades.html', context)


@login_required
@permission_required('view_students')
def student_report_card(request, student_id):
    """Generate student report card"""
    student = get_object_or_404(Student, pk=student_id)
    
    # Check access permissions (same as student_detail)
    if request.user.role == 'parent':
        if not student.user.parent_children.filter(parent=request.user).exists():
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    elif request.user.role == 'student':
        if student.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    # Get current term or allow term selection
    term_id = request.GET.get('term')
    if term_id:
        term = get_object_or_404(Term, pk=term_id)
    else:
        term = Term.objects.filter(is_current=True).first()
    
    if not term:
        messages.error(request, 'No active term found.')
        return redirect('student_detail', student_id=student_id)
    
    # Get grades for the term
    grades = StudentGrade.objects.filter(
        student=student,
        assessment__term=term
    ).select_related('assessment', 'assessment__subject').order_by('assessment__subject__name')
    
    # Group grades by subject
    subject_grades = {}
    for grade in grades:
        subject = grade.assessment.subject
        if subject not in subject_grades:
            subject_grades[subject] = []
        subject_grades[subject].append(grade)
    
    # Calculate subject averages
    subject_averages = {}
    for subject, grade_list in subject_grades.items():
        total_marks = sum(grade.marks_obtained for grade in grade_list)
        total_possible = sum(grade.assessment.total_marks for grade in grade_list)
        average = (total_marks / total_possible * 100) if total_possible > 0 else 0
        subject_averages[subject] = {
            'average': average,
            'letter_grade': get_letter_grade(average),
            'grades': grade_list
        }
    
    # Calculate overall average
    overall_average = sum(avg['average'] for avg in subject_averages.values()) / len(subject_averages) if subject_averages else 0
    
    # Get attendance for the term
    attendance_records = Attendance.objects.filter(
        student=student,
        date__range=[term.start_date, term.end_date]
    )
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    context = {
        'student': student,
        'term': term,
        'subject_averages': subject_averages,
        'overall_average': overall_average,
        'overall_letter_grade': get_letter_grade(overall_average),
        'attendance_percentage': attendance_percentage,
        'total_days': total_days,
        'present_days': present_days,
    }
    
    return render(request, 'students/report_card.html', context)


def get_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B'
    elif percentage >= 60:
        return 'C'
    elif percentage >= 50:
        return 'D'
    else:
        return 'F'
