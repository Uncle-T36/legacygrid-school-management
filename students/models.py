from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class AcademicYear(models.Model):
    """Academic year model"""
    name = models.CharField(max_length=20, unique=True)  # e.g., "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one academic year is current
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Term(models.Model):
    """School term/semester model"""
    TERM_CHOICES = [
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
        ('semester1', 'Semester 1'),
        ('semester2', 'Semester 2'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=20, choices=TERM_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['academic_year', 'name']
        ordering = ['academic_year', 'start_date']
    
    def __str__(self):
        return f"{self.academic_year.name} - {self.get_name_display()}"


class Grade(models.Model):
    """Grade/Class level model"""
    name = models.CharField(max_length=50)  # e.g., "Grade 1", "Form 4", "Year 12"
    level = models.IntegerField()  # Numeric level for ordering
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='grades')
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['level']
        unique_together = ['school', 'name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Subject(models.Model):
    """Subject model"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)  # e.g., "MATH", "ENG", "SCI"
    description = models.TextField(blank=True)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='subjects')
    grades = models.ManyToManyField(Grade, related_name='subjects')
    
    class Meta:
        unique_together = ['school', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class StudentClass(models.Model):
    """Class/Stream model for grouping students"""
    name = models.CharField(max_length=50)  # e.g., "1A", "4 Science", "Year 12 Maths"
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='classes')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='classes_teaching',
        limit_choices_to={'role': 'teacher'}
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='classes')
    max_students = models.PositiveIntegerField(default=30)
    
    class Meta:
        unique_together = ['grade', 'name', 'academic_year']
        ordering = ['grade__level', 'name']
    
    def __str__(self):
        return f"{self.grade.name} - {self.name}"
    
    @property
    def current_enrollment(self):
        return self.enrollments.filter(is_active=True).count()


class Student(models.Model):
    """Student profile model"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=20, unique=True)
    admission_date = models.DateField(default=timezone.now)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    medical_conditions = models.TextField(blank=True)
    
    # Guardian Information
    guardian_name = models.CharField(max_length=100)
    guardian_relationship = models.CharField(max_length=50)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField(blank=True)
    guardian_address = models.TextField()
    
    # Academic Information
    current_class = models.ForeignKey(
        StudentClass, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='current_students'
    )
    
    # Additional Information
    transport_required = models.BooleanField(default=False)
    lunch_program = models.BooleanField(default=False)
    special_needs = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['student_id']
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    def get_current_enrollment(self):
        return self.enrollments.filter(is_active=True).first()


class Enrollment(models.Model):
    """Student enrollment in a class for a specific academic year"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='enrollments')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'academic_year']
        ordering = ['-academic_year', 'student__student_id']
    
    def __str__(self):
        return f"{self.student} in {self.student_class} ({self.academic_year})"


class Attendance(models.Model):
    """Daily attendance tracking"""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    remarks = models.TextField(blank=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='attendance_marked'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date', 'subject']
        ordering = ['-date', 'student__student_id']
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class AssessmentType(models.Model):
    """Types of assessments (e.g., Quiz, Test, Exam, Assignment)"""
    name = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)  # Percentage weight
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='assessment_types')
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.weight}%)"


class Assessment(models.Model):
    """Individual assessment/exam"""
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name='assessments')
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='assessments')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='assessments')
    
    date_conducted = models.DateField()
    total_marks = models.PositiveIntegerField(default=100)
    pass_mark = models.PositiveIntegerField(default=50)
    
    instructions = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='assessments_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_conducted']
    
    def __str__(self):
        return f"{self.title} - {self.subject} - {self.student_class}"


class StudentGrade(models.Model):
    """Individual student grade for an assessment"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='student_grades')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Calculated fields
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    letter_grade = models.CharField(max_length=2, blank=True)
    remarks = models.TextField(blank=True)
    
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='grades_entered'
    )
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'assessment']
        ordering = ['-assessment__date_conducted']
    
    def save(self, *args, **kwargs):
        # Calculate percentage
        if self.marks_obtained is not None and self.assessment.total_marks > 0:
            self.percentage = (self.marks_obtained / self.assessment.total_marks) * 100
            
            # Calculate letter grade based on percentage
            if self.percentage >= 90:
                self.letter_grade = 'A+'
            elif self.percentage >= 80:
                self.letter_grade = 'A'
            elif self.percentage >= 70:
                self.letter_grade = 'B'
            elif self.percentage >= 60:
                self.letter_grade = 'C'
            elif self.percentage >= 50:
                self.letter_grade = 'D'
            else:
                self.letter_grade = 'F'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student} - {self.assessment} - {self.marks_obtained}/{self.assessment.total_marks}"


class StudentDocument(models.Model):
    """Student document uploads"""
    DOCUMENT_TYPES = [
        ('birth_certificate', 'Birth Certificate'),
        ('medical_record', 'Medical Record'),
        ('previous_school', 'Previous School Report'),
        ('identification', 'Identification Document'),
        ('photo', 'Student Photo'),
        ('guardian_id', 'Guardian ID'),
        ('other', 'Other'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='student_documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='documents_uploaded'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='documents_verified'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.student} - {self.get_document_type_display()}"
