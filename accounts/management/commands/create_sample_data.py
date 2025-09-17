from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from schools.models import School
from students.models import (
    AcademicYear, Term, Grade, Subject, StudentClass, 
    Student, AssessmentType
)
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Creates sample data for testing the school management system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create superuser (owner)
        if not User.objects.filter(username='Uncle-T36').exists():
            owner = User.objects.create_superuser(
                username='Uncle-T36',
                email='admin@legacygrid.co.zw',
                password='admin123',
                first_name='System',
                last_name='Owner',
                role='owner'
            )
            self.stdout.write(self.style.SUCCESS('Created owner user: Uncle-T36'))
        else:
            owner = User.objects.get(username='Uncle-T36')
        
        # Create demo school
        school, created = School.objects.get_or_create(
            name='LegacyGrid Demo School',
            defaults={
                'owner': owner,
                'address': '123 Education Street, Demo City, Zimbabwe'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created school: {school.name}'))
        
        # Create academic year
        current_year = timezone.now().year
        academic_year, created = AcademicYear.objects.get_or_create(
            name=f'{current_year}-{current_year + 1}',
            defaults={
                'start_date': date(current_year, 1, 15),
                'end_date': date(current_year, 12, 15),
                'is_current': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created academic year: {academic_year.name}'))
        
        # Create terms
        terms_data = [
            ('term1', date(current_year, 1, 15), date(current_year, 4, 15), True),
            ('term2', date(current_year, 5, 1), date(current_year, 8, 15), False),
            ('term3', date(current_year, 9, 1), date(current_year, 12, 15), False),
        ]
        
        for term_name, start_date, end_date, is_current in terms_data:
            term, created = Term.objects.get_or_create(
                academic_year=academic_year,
                name=term_name,
                defaults={
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_current': is_current
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created term: {term}'))
        
        # Create grades
        grades_data = [
            ('Grade 1', 1), ('Grade 2', 2), ('Grade 3', 3), ('Grade 4', 4),
            ('Grade 5', 5), ('Grade 6', 6), ('Grade 7', 7),
            ('Form 1', 8), ('Form 2', 9), ('Form 3', 10), 
            ('Form 4', 11), ('Form 5', 12), ('Form 6', 13)
        ]
        
        for grade_name, level in grades_data:
            grade, created = Grade.objects.get_or_create(
                school=school,
                name=grade_name,
                defaults={'level': level}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created grade: {grade_name}'))
        
        # Create subjects
        subjects_data = [
            ('Mathematics', 'MATH'), ('English', 'ENG'), ('Science', 'SCI'),
            ('History', 'HIST'), ('Geography', 'GEO'), ('Physical Education', 'PE'),
            ('Art', 'ART'), ('Music', 'MUS'), ('Computer Science', 'CS'),
            ('Physics', 'PHY'), ('Chemistry', 'CHEM'), ('Biology', 'BIO')
        ]
        
        for subject_name, code in subjects_data:
            subject, created = Subject.objects.get_or_create(
                school=school,
                code=code,
                defaults={'name': subject_name}
            )
            if created:
                # Add to appropriate grades
                if code in ['MATH', 'ENG', 'SCI']:
                    # Core subjects for all grades
                    subject.grades.set(Grade.objects.filter(school=school))
                elif code in ['PHY', 'CHEM', 'BIO']:
                    # Science subjects for higher grades
                    subject.grades.set(Grade.objects.filter(school=school, level__gte=8))
                else:
                    # Other subjects for middle grades
                    subject.grades.set(Grade.objects.filter(school=school, level__gte=5))
                
                self.stdout.write(self.style.SUCCESS(f'Created subject: {subject_name}'))
        
        # Create sample users
        users_data = [
            ('admin', 'admin123', 'John', 'Administrator', 'admin@demo.school', 'admin'),
            ('teacher1', 'teacher123', 'Jane', 'Smith', 'jane.smith@demo.school', 'teacher'),
            ('teacher2', 'teacher123', 'Mike', 'Johnson', 'mike.johnson@demo.school', 'teacher'),
            ('parent1', 'parent123', 'Sarah', 'Williams', 'sarah.williams@demo.school', 'parent'),
            ('parent2', 'parent123', 'David', 'Brown', 'david.brown@demo.school', 'parent'),
            ('student1', 'student123', 'Emma', 'Wilson', 'emma.wilson@demo.school', 'student'),
            ('student2', 'student123', 'Alex', 'Taylor', 'alex.taylor@demo.school', 'student'),
            ('student3', 'student123', 'Sophia', 'Davis', 'sophia.davis@demo.school', 'student'),
        ]
        
        created_users = {}
        for username, password, first_name, last_name, email, role in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    # 'school': school  # Will be added in a later migration
                }
            )
            if created:
                user.set_password(password)
                user.save()
                created_users[username] = user
                self.stdout.write(self.style.SUCCESS(f'Created user: {username} ({role})'))
            else:
                created_users[username] = user
        
        # Create classes
        grade_1 = Grade.objects.get(school=school, name='Grade 1')
        grade_5 = Grade.objects.get(school=school, name='Grade 5')
        form_1 = Grade.objects.get(school=school, name='Form 1')
        
        classes_data = [
            (grade_1, '1A', 'teacher1'),
            (grade_5, '5A', 'teacher2'),
            (form_1, '1 Science', 'teacher1'),
        ]
        
        for grade, class_name, teacher_username in classes_data:
            teacher = created_users.get(teacher_username)
            student_class, created = StudentClass.objects.get_or_create(
                grade=grade,
                name=class_name,
                academic_year=academic_year,
                defaults={
                    'teacher': teacher,
                    'max_students': 30
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created class: {student_class}'))
        
        # Create sample students
        students_data = [
            ('student1', 'STU001', '1A'),
            ('student2', 'STU002', '5A'), 
            ('student3', 'STU003', '1 Science'),
        ]
        
        for username, student_id, class_name in students_data:
            user = created_users.get(username)
            if user and not hasattr(user, 'student_profile'):
                # Find the class
                student_class = StudentClass.objects.filter(name=class_name).first()
                
                student = Student.objects.create(
                    user=user,
                    student_id=student_id,
                    admission_date=date(current_year, 1, 15),
                    date_of_birth=date(2010, 1, 1),
                    gender='M' if 'alex' in username.lower() else 'F',
                    guardian_name=f'Guardian of {user.first_name}',
                    guardian_relationship='Parent',
                    guardian_phone='+263 77 123 4567',
                    guardian_email=f'guardian.{username}@demo.school',
                    guardian_address='123 Demo Street, Demo City',
                    current_class=student_class,
                    transport_required=True,
                    lunch_program=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created student: {student}'))
        
        # Create assessment types
        assessment_types_data = [
            ('Quiz', 10.0),
            ('Test', 20.0),
            ('Assignment', 15.0),
            ('Exam', 55.0),
        ]
        
        for type_name, weight in assessment_types_data:
            assessment_type, created = AssessmentType.objects.get_or_create(
                school=school,
                name=type_name,
                defaults={'weight': weight}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created assessment type: {type_name}'))
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nSample data created successfully!\n\n'
                'Demo Login Credentials:\n'
                '- Owner: Uncle-T36 / admin123\n'
                '- Admin: admin / admin123\n'
                '- Teacher: teacher1 / teacher123\n'
                '- Parent: parent1 / parent123\n'
                '- Student: student1 / student123\n'
            )
        )