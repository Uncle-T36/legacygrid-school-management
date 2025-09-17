from django import forms
from django.contrib.auth import get_user_model
from accounts.models import User
from .models import (
    Student, StudentClass, Grade, Subject, Attendance, 
    Assessment, StudentGrade, StudentDocument, AcademicYear, Term
)

User = get_user_model()


class StudentRegistrationForm(forms.ModelForm):
    """Form for registering new students"""
    
    # User fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Student
        fields = [
            'student_id', 'admission_date', 'date_of_birth', 'gender', 
            'blood_group', 'medical_conditions', 'guardian_name', 
            'guardian_relationship', 'guardian_phone', 'guardian_email', 
            'guardian_address', 'current_class', 'transport_required', 
            'lunch_program', 'special_needs'
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'guardian_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_class': forms.Select(attrs={'class': 'form-select'}),
            'transport_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lunch_program': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'special_needs': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter classes by user's school if not owner
        if user and user.role != 'owner' and not user.is_superuser:
            self.fields['current_class'].queryset = StudentClass.objects.filter(
                grade__school=user.school
            )
    
    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError('A student with this ID already exists.')
        return student_id
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def save(self, commit=True):
        # Create the user first
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role='student'
        )
        
        # Create the student
        student = super().save(commit=False)
        student.user = user
        
        if commit:
            student.save()
        
        return student


class AttendanceForm(forms.ModelForm):
    """Form for taking attendance"""
    
    class Meta:
        model = Attendance
        fields = ['status', 'remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks'})
        }


class BulkAttendanceForm(forms.Form):
    """Form for bulk attendance taking"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        empty_label="All Day Attendance",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter subjects by user's school
        if user and user.role != 'owner' and not user.is_superuser:
            self.fields['subject'].queryset = Subject.objects.filter(school=user.school)


class AssessmentForm(forms.ModelForm):
    """Form for creating assessments"""
    
    class Meta:
        model = Assessment
        fields = [
            'title', 'subject', 'assessment_type', 'student_class', 'term',
            'date_conducted', 'total_marks', 'pass_mark', 'instructions'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'assessment_type': forms.Select(attrs={'class': 'form-select'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'term': forms.Select(attrs={'class': 'form-select'}),
            'date_conducted': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'pass_mark': forms.NumberInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter by user's school if not owner
        if user and user.role != 'owner' and not user.is_superuser:
            self.fields['subject'].queryset = Subject.objects.filter(school=user.school)
            self.fields['student_class'].queryset = StudentClass.objects.filter(
                grade__school=user.school
            )


class GradeEntryForm(forms.ModelForm):
    """Form for entering individual grades"""
    
    class Meta:
        model = StudentGrade
        fields = ['marks_obtained', 'remarks']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'remarks': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional remarks'
            })
        }
    
    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('assessment', None)
        super().__init__(*args, **kwargs)
        
        if assessment:
            self.fields['marks_obtained'].widget.attrs['max'] = str(assessment.total_marks)
            self.fields['marks_obtained'].help_text = f'Maximum marks: {assessment.total_marks}'


class StudentDocumentForm(forms.ModelForm):
    """Form for uploading student documents"""
    
    class Meta:
        model = StudentDocument
        fields = ['document_type', 'title', 'file', 'description']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StudentSearchForm(forms.Form):
    """Form for searching students"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, student ID, or email...'
        })
    )
    grade = forms.ModelChoiceField(
        queryset=Grade.objects.all(),
        required=False,
        empty_label="All Grades",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    student_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        required=False,
        empty_label="All Classes",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Students'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter by user's school if not owner
        if user and user.role != 'owner' and not user.is_superuser:
            self.fields['grade'].queryset = Grade.objects.filter(school=user.school)
            self.fields['student_class'].queryset = StudentClass.objects.filter(
                grade__school=user.school
            )


class GradeForm(forms.ModelForm):
    """Form for creating/editing grades"""
    
    class Meta:
        model = Grade
        fields = ['name', 'level', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StudentClassForm(forms.ModelForm):
    """Form for creating/editing student classes"""
    
    class Meta:
        model = StudentClass
        fields = ['name', 'grade', 'teacher', 'academic_year', 'max_students']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.Select(attrs={'class': 'form-select'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter teachers and grades by school
        if user and user.role != 'owner' and not user.is_superuser:
            self.fields['teacher'].queryset = User.objects.filter(
                role='teacher',
                school=user.school
            )
            self.fields['grade'].queryset = Grade.objects.filter(school=user.school)


class SubjectForm(forms.ModelForm):
    """Form for creating/editing subjects"""
    
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description', 'grades']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'grades': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter grades by school
        if user and user.role != 'owner' and not user.is_superuser:
            self.fields['grades'].queryset = Grade.objects.filter(school=user.school)