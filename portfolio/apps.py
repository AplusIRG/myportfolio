from django.apps import AppConfig
import os

class PortfolioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio'



class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'
    
    def ready(self):
        if os.environ.get('RUN_MAIN'):
            from .services import EnhancedCourseService
            from . import mathematical_methods_1, principles_of_physics_1, multivariate_data_analysis
            
            # Create default courses if they don't exist
            try:
                service = EnhancedCourseService()
                
                # Create Mathematical Methods 1
                math_data = mathematical_methods_1.get_course_data()
                if not self.get_model('Course').objects.filter(slug='mathematical-methods-1').exists():
                    service.create_enhanced_course(math_data)
                
                # Create Principles of Physics 1
                physics_data = principles_of_physics_1.get_course_data()
                if not self.get_model('Course').objects.filter(slug='principles-of-physics-1').exists():
                    service.create_enhanced_course(physics_data)
                
                # Create Multivariate Data Analysis
                data_data = multivariate_data_analysis.get_course_data()
                if not self.get_model('Course').objects.filter(slug='multivariate-data-analysis').exists():
                    service.create_enhanced_course(data_data)
                    
            except Exception as e:
                print(f"Error creating default courses: {e}")