"""
Django management command to create default courses.
Run with: python manage.py create_default_courses
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from datetime import date, timedelta
from portfolio.models import Course, CourseModule, FAQ, Instructor, CustomUser
import json

class Command(BaseCommand):
    help = 'Create default courses for the portfolio website'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating default courses...'))
        
        # Get or create instructor (you)
        try:
            instructor_user = CustomUser.objects.get(email='sichombarobertbob@gmail.com')
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.WARNING('Creating instructor user...'))
            instructor_user = CustomUser.objects.create_user(
                username='robert',
                email='sichombarobertbob@gmail.com',
                password='temp_password123',
                first_name='Robert',
                last_name='Sichomba',
                phone_number='+260974609823'
            )
        
        # Create or get instructor profile
        instructor, created = Instructor.objects.get_or_create(
            user=instructor_user,
            defaults={
                'role': 'Lead Instructor & Course Designer',
                'bio': 'Expert Data Scientist and Full-Stack Developer with 5+ years of experience in teaching and developing educational content.',
                'is_lead_instructor': True,
                'linkedin_url': 'https://www.linkedin.com/in/robert-sichomba',
                'github_url': 'https://github.com/sichomba',
                'website_url': 'https://robertsichomba.com'
            }
        )
        
        # Course 1: Mathematical Methods 1
        math_course, _ = Course.objects.get_or_create(
            title='Mathematical Methods 1',
            defaults={
                'subtitle': 'Comprehensive Mathematics from Fundamentals to Advanced Applications',
                'description': """A rigorous course covering essential mathematical methods required for 
                science, engineering, and advanced studies. This course systematically builds from basic 
                algebra and functions through calculus, linear algebra, and probability theory.""",
                'short_description': 'Master essential mathematical methods for science and engineering',
                'slug': slugify('Mathematical Methods 1'),
                'level': 'intermediate',
                'status': 'active',
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=120),
                'schedule_note': 'New modules released weekly. Live problem sessions every Wednesday 7-9 PM EST',
                'location': 'Virtual Classroom + Live Sessions',
                'is_virtual': True,
                'prerequisites': 'High school algebra and geometry. Basic calculus recommended but not required.',
                'is_free': True,
                'price': 0.00,
                'access_level': 'enrolled',
                'duration': '12 weeks',
                'is_featured': True,
                'enrolled_count': 0
            }
        )
        math_course.instructors.add(instructor)
        
        # Course 2: Multivariate Data Analysis
        data_course, _ = Course.objects.get_or_create(
            title='Multivariate Data Analysis',
            defaults={
                'subtitle': 'Advanced Statistical Methods for Complex Data Systems',
                'description': """An advanced course in statistical methods for analyzing complex, 
                high-dimensional data. This course covers multivariate statistical techniques including 
                factor analysis, cluster analysis, discriminant analysis, and multivariate regression.""",
                'short_description': 'Master advanced multivariate statistical techniques for complex data analysis',
                'slug': slugify('Multivariate Data Analysis'),
                'level': 'advanced',
                'status': 'active',
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=150),
                'schedule_note': 'Weekly modules with live coding sessions. Project work throughout.',
                'location': 'Virtual Classroom + Data Lab',
                'is_virtual': True,
                'prerequisites': 'Statistics 101, linear algebra, basic programming (Python/R)',
                'is_free': False,
                'price': 199.00,
                'access_level': 'enrolled',
                'duration': '16 weeks',
                'is_featured': True,
                'enrolled_count': 0
            }
        )
        data_course.instructors.add(instructor)
        
        # Course 3: Principles of Physics 1
        physics_course, _ = Course.objects.get_or_create(
            title='Principles of Physics 1',
            defaults={
                'subtitle': 'Foundational Physics: Mechanics, Thermodynamics, and Wave Phenomena',
                'description': """A comprehensive introduction to university-level physics covering 
                classical mechanics, thermodynamics, wave motion, and optics. This course emphasizes 
                both conceptual understanding and quantitative problem-solving skills.""",
                'short_description': 'Master fundamental physics principles with hands-on applications',
                'slug': slugify('Principles of Physics 1'),
                'level': 'intermediate',
                'status': 'active',
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=180),
                'schedule_note': 'Two modules per week. Lab sessions every Saturday 10 AM-12 PM EST',
                'location': 'Virtual Lab + Live Demonstrations',
                'is_virtual': True,
                'prerequisites': 'High school physics and calculus. Familiarity with vectors.',
                'is_free': True,
                'price': 0.00,
                'access_level': 'enrolled',
                'duration': '18 weeks',
                'is_featured': True,
                'enrolled_count': 0
            }
        )
        physics_course.instructors.add(instructor)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created/updated {Course.objects.count()} courses!'))