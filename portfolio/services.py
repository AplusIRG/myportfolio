"""
Comprehensive Course Management System with Enhanced Student Experience
"""
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Avg, Q, F, ExpressionWrapper, DurationField
from django.utils.timezone import timedelta
from django.core.cache import cache
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
import uuid
import json
import statistics
from collections import defaultdict
import pandas as pd
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from decimal import Decimal
import stripe
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)
User = get_user_model()

# Initialize Stripe if API key exists
try:
    stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None
except:
    pass


class EnhancedCourseService:
    """
    Comprehensive course management with data science, notifications,
    payments, and progressive learning features.
    """
    
    def __init__(self, user=None):
        self.user = user
        self.cache_prefix = "course_service"
    
    def create_enhanced_course(self, course_data: Dict, instructor_id=None) -> Dict:
        """Create a course with all enhanced features."""
        from .models import Course, CourseModule, FAQ, Meeting, Instructor
        
        with transaction.atomic():
            # Generate UUID for course
            course_uuid = str(uuid.uuid4())
            
            # Create main course
            course = Course.objects.create(
                title=course_data.get('title'),
                subtitle=course_data.get('subtitle', ''),
                description=course_data.get('description', ''),
                short_description=course_data.get('short_description', ''),
                level=course_data.get('level', 'intermediate'),
                status=course_data.get('status', 'upcoming'),
                start_date=course_data.get('start_date', timezone.now().date()),
                end_date=course_data.get('end_date', timezone.now().date() + timedelta(days=90)),
                schedule_note=course_data.get('schedule_note', ''),
                location=course_data.get('location', 'Virtual'),
                is_virtual=course_data.get('is_virtual', True),
                prerequisites=course_data.get('prerequisites', ''),
                learning_objectives=course_data.get('learning_objectives', []),
                is_free=course_data.get('is_free', True),
                price=course_data.get('price', 0.00),
                access_level=course_data.get('access_level', 'enrolled'),
                banner_image=course_data.get('banner_image', None),
                thumbnail=course_data.get('thumbnail', None),
                # Add metadata for analytics
                metadata={
                    'uuid': course_uuid,
                    'created_by': instructor_id,
                    'version': '1.0',
                    'features': {
                        'analytics': True,
                        'notifications': True,
                        'certificates': True,
                        'discussions': True,
                        'leaderboard': True,
                    }
                }
            )
            
            # Create course modules
            modules_created = []
            for idx, module_data in enumerate(course_data.get('modules', [])):
                module = CourseModule.objects.create(
                    course=course,
                    title=module_data['title'],
                    order=module_data.get('order', idx + 1),
                    description=module_data.get('description', ''),
                    date=module_data.get('date'),
                    is_live_session=module_data.get('is_live_session', False),
                    slides_url=module_data.get('slides_url', ''),
                    video_url=module_data.get('video_url', ''),
                    code_url=module_data.get('code_url', ''),
                    additional_resources=module_data.get('additional_resources', []),
                    metadata={
                        'estimated_duration': module_data.get('estimated_duration', '60 minutes'),
                        'difficulty': module_data.get('difficulty', 'medium'),
                        'prerequisites': module_data.get('module_prerequisites', []),
                        'learning_outcomes': module_data.get('learning_outcomes', [])
                    }
                )
                modules_created.append(module)
            
            # Create FAQs
            faqs_created = []
            for idx, faq_data in enumerate(course_data.get('faqs', [])):
                faq = FAQ.objects.create(
                    course=course,
                    question=faq_data['question'],
                    answer=faq_data['answer'],
                    order=faq_data.get('order', idx + 1)
                )
                faqs_created.append(faq)
            
            # Assign instructor if provided
            if instructor_id:
                try:
                    instructor = Instructor.objects.get(id=instructor_id)
                    course.instructors.add(instructor)
                except Instructor.DoesNotExist:
                    pass
            
            # Initialize course analytics
            self._initialize_course_analytics(course)
            
            # Set up default notifications
            self._setup_course_notifications(course)
            
            return {
                'success': True,
                'course': course,
                'modules_created': len(modules_created),
                'faqs_created': len(faqs_created),
                'course_uuid': course_uuid
            }
    
    def enroll_user(self, course_slug: str, payment_info: Dict = None) -> Dict:
        """Enroll user in a course with payment handling."""
        from .models import Course, CourseEnrollment
        
        if not self.user:
            raise ValueError("User must be authenticated")
        
        try:
            course = Course.objects.get(slug=course_slug)
            
            # Check if already enrolled
            existing = CourseEnrollment.objects.filter(user=self.user, course=course).first()
            if existing:
                return {
                    'success': True,
                    'already_enrolled': True,
                    'enrollment': existing
                }
            
            # Handle payment if course is not free
            payment_success = True
            payment_data = {}
            if not course.is_free and course.price > 0:
                payment_result = self._process_payment(course, payment_info)
                if not payment_result.get('success'):
                    return payment_result
                payment_data = payment_result.get('payment_data', {})
                payment_success = payment_result.get('success')
            
            if payment_success:
                # Create enrollment
                enrollment = CourseEnrollment.objects.create(
                    user=self.user,
                    course=course,
                    progress_data={
                        'completed_modules': [],
                        'total_modules': course.modules.filter(is_published=True).count(),
                        'started_at': timezone.now().isoformat(),
                        'last_module_accessed': None,
                        'quiz_scores': {},
                        'assignment_submissions': [],
                        'time_spent': {},
                        'notes': [],
                        'bookmarks': [],
                        'streak_days': 0,
                        'last_active_date': timezone.now().date().isoformat(),
                        'achievements': [],
                        'payment_info': payment_data
                    }
                )
                
                # Update course enrollment count
                course.enrolled_count = CourseEnrollment.objects.filter(course=course, is_active=True).count()
                course.save()
                
                # Initialize user course analytics
                self._initialize_user_analytics(self.user, course)
                
                # Send enrollment notifications
                self._send_enrollment_notifications(course, enrollment)
                
                # Create welcome sequence
                self._start_welcome_sequence(course, enrollment)
                
                # Add to learning path recommendations
                self._update_learning_path(self.user, course)
                
                return {
                    'success': True,
                    'enrollment': enrollment,
                    'course': course,
                    'welcome_message': f"🎉 Welcome to {course.title}! Your learning journey begins now.",
                    'next_steps': [
                        "Complete your profile setup",
                        "Join the course community",
                        "Start with Module 1"
                    ]
                }
            
        except Course.DoesNotExist:
            raise ValueError(f"Course with slug '{course_slug}' not found")
    
    def get_enhanced_dashboard(self, course_slug: str) -> Dict:
        """Get comprehensive course dashboard with analytics."""
        from .models import Course, CourseEnrollment, CourseModule
        
        cache_key = f"{self.cache_prefix}_dashboard_{course_slug}_{self.user.id if self.user else 'anon'}"
        cached_data = cache.get(cache_key)
        
        if cached_data and self.user:
            return cached_data
        
        try:
            course = Course.objects.get(slug=course_slug)
            
            # Get user enrollment
            enrollment = None
            progress_data = {}
            if self.user:
                enrollment = CourseEnrollment.objects.filter(
                    user=self.user, 
                    course=course
                ).first()
                if enrollment:
                    progress_data = enrollment.progress_data
            
            # Get enhanced modules with rich data
            modules = self._get_enhanced_modules(course, enrollment)
            
            # Get course analytics
            analytics = self._get_course_analytics(course)
            
            # Get user progress with insights
            progress = self._get_user_progress_insights(course, enrollment)
            
            # Get recommendations
            recommendations = self._get_recommendations(course, enrollment)
            
            # Get community activity
            community = self._get_community_activity(course)
            
            # Get upcoming deadlines
            deadlines = self._get_upcoming_deadlines(course, enrollment)
            
            # Get user's learning statistics
            learning_stats = self._get_learning_statistics(self.user, course) if self.user else None
            
            result = {
                'course': course,
                'enrollment': enrollment,
                'modules': modules,
                'analytics': analytics,
                'progress': progress,
                'recommendations': recommendations,
                'community': community,
                'deadlines': deadlines,
                'learning_stats': learning_stats,
                'is_enrolled': enrollment is not None,
                'can_enroll': self._can_enroll(course),
                'current_streak': progress_data.get('streak_days', 0) if progress_data else 0,
                'estimated_completion_time': self._estimate_completion_time(course, progress),
                'leaderboard_position': self._get_leaderboard_position(course, self.user) if self.user else None
            }
            
            # Cache for 5 minutes if user is logged in
            if self.user:
                cache.set(cache_key, result, 300)
            
            return result
            
        except Course.DoesNotExist:
            raise ValueError(f"Course not found")
    
    def track_learning_activity(self, course_slug: str, activity_type: str, 
                                module_id: int = None, duration: int = 0) -> Dict:
        """Track detailed learning activities for analytics."""
        from .models import Course, CourseEnrollment
        
        if not self.user:
            raise ValueError("User must be authenticated")
        
        try:
            course = Course.objects.get(slug=course_slug)
            enrollment = CourseEnrollment.objects.get(user=self.user, course=course)
            
            timestamp = timezone.now()
            
            # Update streak
            self._update_learning_streak(enrollment)
            
            # Track time spent
            if module_id and duration > 0:
                time_spent = enrollment.progress_data.get('time_spent', {})
                module_key = str(module_id)
                if module_key in time_spent:
                    time_spent[module_key] += duration
                else:
                    time_spent[module_key] = duration
                enrollment.progress_data['time_spent'] = time_spent
            
            # Record activity
            activity_log = enrollment.progress_data.get('activity_log', [])
            activity_log.append({
                'type': activity_type,
                'module_id': module_id,
                'timestamp': timestamp.isoformat(),
                'duration': duration
            })
            
            # Keep only last 100 activities
            if len(activity_log) > 100:
                activity_log = activity_log[-100:]
            
            enrollment.progress_data['activity_log'] = activity_log
            enrollment.last_accessed = timestamp
            enrollment.save()
            
            # Update user learning profile
            self._update_learning_profile(self.user, course, activity_type)
            
            # Check for achievement unlocks
            achievements = self._check_achievements(enrollment)
            
            return {
                'success': True,
                'streak_updated': enrollment.progress_data.get('streak_days', 0),
                'achievements_unlocked': achievements
            }
            
        except (Course.DoesNotExist, CourseEnrollment.DoesNotExist):
            raise ValueError("Course or enrollment not found")
    
    def generate_learning_report(self, course_slug: str) -> Dict:
        """Generate comprehensive learning report with visualizations."""
        from .models import Course, CourseEnrollment
        
        if not self.user:
            raise ValueError("User must be authenticated")
        
        try:
            course = Course.objects.get(slug=course_slug)
            enrollment = CourseEnrollment.objects.get(user=self.user, course=course)
            
            # Generate progress visualization
            progress_chart = self._generate_progress_chart(enrollment)
            
            # Generate time distribution chart
            time_chart = self._generate_time_distribution_chart(enrollment)
            
            # Calculate learning metrics
            metrics = self._calculate_learning_metrics(enrollment)
            
            # Generate recommendations based on performance
            performance_recommendations = self._generate_performance_recommendations(
                enrollment, metrics
            )
            
            # Create comparison with peer performance
            peer_comparison = self._compare_with_peers(course, enrollment)
            
            # Generate PDF report (simplified version)
            report_data = self._generate_report_data(enrollment, metrics)
            
            return {
                'success': True,
                'report': {
                    'course_title': course.title,
                    'student_name': self.user.get_full_name() or self.user.email,
                    'progress_chart': progress_chart,
                    'time_chart': time_chart,
                    'metrics': metrics,
                    'recommendations': performance_recommendations,
                    'peer_comparison': peer_comparison,
                    'generated_at': timezone.now().isoformat(),
                    'report_id': f"REPORT-{uuid.uuid4().hex[:8].upper()}"
                }
            }
            
        except (Course.DoesNotExist, CourseEnrollment.DoesNotExist):
            raise ValueError("Course or enrollment not found")
    
    def create_study_group(self, course_slug: str, group_data: Dict) -> Dict:
        """Create a study group for collaborative learning."""
        from .models import Course, StudyGroup
        
        if not self.user:
            raise ValueError("User must be authenticated")
        
        try:
            course = Course.objects.get(slug=course_slug)
            
            study_group = StudyGroup.objects.create(
                course=course,
                name=group_data['name'],
                description=group_data.get('description', ''),
                created_by=self.user,
                max_members=group_data.get('max_members', 10),
                meeting_schedule=group_data.get('meeting_schedule', {}),
                is_public=group_data.get('is_public', True)
            )
            
            # Add creator as member
            study_group.members.add(self.user)
            
            # Set up group notifications
            self._setup_group_notifications(study_group)
            
            # Create initial discussion
            if group_data.get('initial_discussion'):
                DiscussionPost.objects.create(
                    group=study_group,
                    author=self.user,
                    title=f"Welcome to {study_group.name}",
                    content=group_data['initial_discussion']
                )
            
            return {
                'success': True,
                'group': study_group,
                'message': f"Study group '{study_group.name}' created successfully!"
            }
            
        except Course.DoesNotExist:
            raise ValueError(f"Course not found")
    
    def send_course_notification(self, course_slug: str, notification_type: str, 
                                 data: Dict = None) -> Dict:
        """Send intelligent notifications to course participants."""
        from .models import Course, CourseEnrollment
        
        try:
            course = Course.objects.get(slug=course_slug)
            enrollments = CourseEnrollment.objects.filter(course=course, is_active=True)
            
            notifications_sent = 0
            errors = []
            
            for enrollment in enrollments:
                try:
                    notification_data = self._prepare_notification(
                        notification_type, enrollment.user, course, data
                    )
                    
                    # Send via multiple channels
                    channels = data.get('channels', ['email', 'in_app'])
                    
                    if 'email' in channels:
                        self._send_email_notification(
                            enrollment.user.email,
                            notification_data['subject'],
                            notification_data['message'],
                            notification_data.get('html_message')
                        )
                    
                    if 'in_app' in channels:
                        self._create_in_app_notification(
                            enrollment.user,
                            notification_data
                        )
                    
                    if 'push' in channels and hasattr(settings, 'FCM_API_KEY'):
                        self._send_push_notification(
                            enrollment.user,
                            notification_data
                        )
                    
                    notifications_sent += 1
                    
                except Exception as e:
                    errors.append(str(e))
                    logger.error(f"Failed to send notification to {enrollment.user.email}: {e}")
            
            return {
                'success': True,
                'notifications_sent': notifications_sent,
                'errors': errors if errors else None
            }
            
        except Course.DoesNotExist:
            raise ValueError(f"Course not found")
    
    def get_adaptive_learning_path(self, course_slug: str) -> Dict:
        """Generate adaptive learning path based on user's progress and preferences."""
        from .models import Course, CourseEnrollment
        
        if not self.user:
            raise ValueError("User must be authenticated")
        
        try:
            course = Course.objects.get(slug=course_slug)
            enrollment = CourseEnrollment.objects.filter(user=self.user, course=course).first()
            
            if not enrollment:
                # Return default learning path
                return self._get_default_learning_path(course)
            
            # Analyze user's learning patterns
            learning_patterns = self._analyze_learning_patterns(enrollment)
            
            # Get user's preferred learning style
            learning_style = self._get_learning_style(self.user)
            
            # Generate personalized path
            personalized_path = self._generate_personalized_path(
                course, enrollment, learning_patterns, learning_style
            )
            
            return {
                'success': True,
                'learning_path': personalized_path,
                'estimated_total_time': self._calculate_total_time(personalized_path),
                'recommended_pace': self._recommend_pace(enrollment, personalized_path),
                'difficulty_adjustment': self._suggest_difficulty_adjustment(enrollment)
            }
            
        except Course.DoesNotExist:
            raise ValueError(f"Course not found")
    
    # Helper methods
    def _get_enhanced_modules(self, course, enrollment):
        """Get modules with enhanced data and user-specific status."""
        from .models import CourseModule
        
        modules = []
        for module in course.modules.filter(is_published=True).order_by('order'):
            module_data = {
                'id': module.id,
                'title': module.title,
                'order': module.order,
                'description': module.description,
                'date': module.date,
                'is_live_session': module.is_live_session,
                'resources': self._format_module_resources(module),
                'metadata': module.metadata if hasattr(module, 'metadata') else {},
                'status': 'locked',
                'progress': 0,
                'time_estimate': module.metadata.get('estimated_duration', '60 minutes') if hasattr(module, 'metadata') else '60 minutes',
                'difficulty': module.metadata.get('difficulty', 'medium') if hasattr(module, 'metadata') else 'medium',
                'prerequisites_met': True
            }
            
            if enrollment:
                module_data['status'] = self._get_module_status(module, enrollment)
                module_data['progress'] = self._get_module_progress(module, enrollment)
                module_data['time_spent'] = enrollment.progress_data.get('time_spent', {}).get(str(module.id), 0)
                module_data['notes'] = self._get_module_notes(enrollment, module.id)
                module_data['bookmarked'] = module.id in enrollment.progress_data.get('bookmarks', [])
            
            modules.append(module_data)
        
        return modules
    
    def _get_module_status(self, module, enrollment):
        """Determine module status with more granularity."""
        completed_modules = enrollment.progress_data.get('completed_modules', [])
        
        if module.id in completed_modules:
            return 'completed'
        
        # Check prerequisites
        prerequisites = module.metadata.get('prerequisites', []) if hasattr(module, 'metadata') else []
        for prereq_id in prerequisites:
            if prereq_id not in completed_modules:
                return 'locked'
        
        # Check if it's the next module
        if not completed_modules:
            return 'available' if module.order == 1 else 'locked'
        
        last_completed = max(completed_modules) if completed_modules else 0
        if module.order <= last_completed + 1:
            return 'available'
        
        return 'upcoming'
    
    def _initialize_course_analytics(self, course):
        """Initialize analytics tracking for a course."""
        analytics_data = {
            'total_enrollments': 0,
            'active_enrollments': 0,
            'completion_rate': 0.0,
            'average_progress': 0.0,
            'average_time_spent': 0.0,
            'module_completion_rates': {},
            'weekly_activity': {},
            'difficulty_feedback': {},
            'popular_modules': [],
            'dropout_points': [],
            'created_at': timezone.now().isoformat()
        }
        
        # Store in course metadata or separate analytics model
        if not hasattr(course, 'analytics_data'):
            course.analytics_data = analytics_data
            course.save()
    
    def _initialize_user_analytics(self, user, course):
        """Initialize analytics for a user in a course."""
        from .models import UserAnalytics
        
        UserAnalytics.objects.get_or_create(
            user=user,
            course=course,
            defaults={
                'learning_patterns': {
                    'preferred_learning_times': [],
                    'average_session_duration': 0,
                    'preferred_content_types': [],
                    'difficulty_preference': 'medium',
                    'retention_rate': 0.0
                },
                'engagement_metrics': {
                    'daily_active_minutes': 0,
                    'weekly_engagement': 0,
                    'completion_consistency': 0.0
                },
                'performance_metrics': {
                    'quiz_average': 0.0,
                    'assignment_scores': [],
                    'concept_mastery': {}
                }
            }
        )
    
    def _update_learning_streak(self, enrollment):
        """Update user's learning streak."""
        today = timezone.now().date()
        last_active = enrollment.progress_data.get('last_active_date')
        
        if last_active:
            last_active_date = datetime.fromisoformat(last_active).date()
            days_diff = (today - last_active_date).days
            
            if days_diff == 1:
                # Consecutive day
                current_streak = enrollment.progress_data.get('streak_days', 0) + 1
                enrollment.progress_data['streak_days'] = current_streak
                
                # Check for streak achievements
                if current_streak in [7, 30, 100]:
                    self._award_achievement(enrollment, f'streak_{current_streak}')
            elif days_diff > 1:
                # Broken streak
                enrollment.progress_data['streak_days'] = 1
        else:
            # First day
            enrollment.progress_data['streak_days'] = 1
        
        enrollment.progress_data['last_active_date'] = today.isoformat()
        enrollment.save()
    
    def _update_learning_profile(self, user, course, activity_type):
        """Update user's learning profile based on activities."""
        from .models import UserAnalytics
        
        try:
            analytics = UserAnalytics.objects.get(user=user, course=course)
            
            # Update learning patterns
            patterns = analytics.learning_patterns
            
            # Track preferred learning times
            current_hour = timezone.now().hour
            if current_hour not in patterns.get('preferred_learning_times', []):
                times = patterns.get('preferred_learning_times', [])
                times.append(current_hour)
                patterns['preferred_learning_times'] = times[:24]  # Keep last 24
            
            # Track content preferences
            content_types = patterns.get('preferred_content_types', [])
            if activity_type not in content_types:
                content_types.append(activity_type)
                patterns['preferred_content_types'] = content_types[:10]
            
            analytics.learning_patterns = patterns
            analytics.save()
            
        except UserAnalytics.DoesNotExist:
            pass
    
    def _get_course_analytics(self, course):
        """Get comprehensive course analytics."""
        from .models import CourseEnrollment
        
        enrollments = CourseEnrollment.objects.filter(course=course, is_active=True)
        
        # Calculate basic metrics
        total_enrolled = enrollments.count()
        active_enrollments = enrollments.filter(
            last_accessed__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Calculate progress statistics
        progress_values = [e.get_progress_percentage() for e in enrollments]
        average_progress = statistics.mean(progress_values) if progress_values else 0
        
        # Calculate completion rate
        completed = enrollments.filter(completed_at__isnull=False).count()
        completion_rate = (completed / total_enrolled * 100) if total_enrolled > 0 else 0
        
        return {
            'total_enrolled': total_enrolled,
            'active_enrollments': active_enrollments,
            'average_progress': round(average_progress, 1),
            'completion_rate': round(completion_rate, 1),
            'engagement_rate': round((active_enrollments / total_enrolled * 100) if total_enrolled > 0 else 0, 1),
            'weekly_trend': self._get_weekly_trend(course),
            'module_popularity': self._get_module_popularity(course),
            'time_of_day_activity': self._get_time_of_day_activity(course)
        }
    
    def _get_user_progress_insights(self, course, enrollment):
        """Get detailed progress insights for user."""
        if not enrollment:
            return None
        
        progress_percentage = enrollment.get_progress_percentage()
        completed_modules = len(enrollment.progress_data.get('completed_modules', []))
        total_modules = enrollment.progress_data.get('total_modules', 0)
        
        # Calculate pace
        started_at = datetime.fromisoformat(enrollment.progress_data.get('started_at', timezone.now().isoformat()))
        days_since_start = (timezone.now() - started_at).days
        
        expected_pace = (total_modules / 90) * days_since_start  # 90-day course
        actual_pace = completed_modules
        
        pace_status = 'on_track'
        if actual_pace < expected_pace * 0.7:
            pace_status = 'behind'
        elif actual_pace > expected_pace * 1.3:
            pace_status = 'ahead'
        
        # Calculate estimated completion
        if completed_modules > 0:
            days_per_module = days_since_start / completed_modules if completed_modules > 0 else 0
            remaining_modules = total_modules - completed_modules
            estimated_days_remaining = remaining_modules * days_per_module
        else:
            estimated_days_remaining = 90  # Default
        
        return {
            'percentage': progress_percentage,
            'completed_modules': completed_modules,
            'total_modules': total_modules,
            'pace_status': pace_status,
            'estimated_completion_date': (
                timezone.now() + timedelta(days=estimated_days_remaining)
            ).date().isoformat() if estimated_days_remaining else None,
            'streak': enrollment.progress_data.get('streak_days', 0),
            'time_spent_total': sum(enrollment.progress_data.get('time_spent', {}).values()),
            'achievements': enrollment.progress_data.get('achievements', [])
        }
    
    def _get_recommendations(self, course, enrollment):
        """Get personalized recommendations."""
        recommendations = []
        
        if enrollment:
            # Based on progress
            progress = enrollment.get_progress_percentage()
            
            if progress < 30:
                recommendations.append({
                    'type': 'motivational',
                    'title': 'Start Strong!',
                    'message': 'Complete your first module to build momentum.',
                    'priority': 'high'
                })
            elif progress < 70:
                recommendations.append({
                    'type': 'engagement',
                    'title': 'Join a Study Group',
                    'message': 'Collaborate with peers to enhance learning.',
                    'priority': 'medium'
                })
            
            # Based on activity patterns
            time_spent = enrollment.progress_data.get('time_spent', {})
            if time_spent:
                avg_time = sum(time_spent.values()) / len(time_spent)
                if avg_time < 30:  # Less than 30 minutes per module
                    recommendations.append({
                        'type': 'study_habit',
                        'title': 'Deep Dive Recommended',
                        'message': 'Spend more time on each module for better retention.',
                        'priority': 'medium'
                    })
        
        # General recommendations
        recommendations.extend([
            {
                'type': 'resource',
                'title': 'Supplementary Materials',
                'message': 'Check out the additional resources section for each module.',
                'priority': 'low'
            },
            {
                'type': 'community',
                'title': 'Participate in Discussions',
                'message': 'Engage with other students in course forums.',
                'priority': 'medium'
            }
        ])
        
        return recommendations
    
    def _get_community_activity(self, course):
        """Get recent community activity."""
        # This would typically come from a Discussion model
        # For now, return simulated data
        return {
            'recent_posts': 24,
            'active_discussions': 5,
            'study_groups': 3,
            'top_contributors': [
                {'name': 'Alex Johnson', 'contributions': 42},
                {'name': 'Sam Wilson', 'contributions': 38},
                {'name': 'Taylor Smith', 'contributions': 31}
            ]
        }
    
    def _get_upcoming_deadlines(self, course, enrollment):
        """Get upcoming deadlines for enrolled user."""
        if not enrollment:
            return []
        
        deadlines = []
        today = timezone.now().date()
        
        # Check live sessions
        live_sessions = course.modules.filter(
            is_live_session=True,
            date__gte=today
        ).order_by('date')[:3]
        
        for session in live_sessions:
            deadlines.append({
                'type': 'live_session',
                'title': session.title,
                'date': session.date,
                'priority': 'high' if (session.date - today).days <= 1 else 'medium'
            })
        
        # Check assignment deadlines (would come from Assignment model)
        # For now, simulate based on module completion
        remaining_modules = course.modules.filter(
            is_published=True,
            order__gt=len(enrollment.progress_data.get('completed_modules', []))
        ).order_by('order')[:5]
        
        for i, module in enumerate(remaining_modules):
            suggested_date = today + timedelta(days=i * 3)  # Every 3 days
            deadlines.append({
                'type': 'module',
                'title': f"Complete: {module.title}",
                'date': suggested_date,
                'priority': 'medium' if i == 0 else 'low'
            })
        
        return sorted(deadlines, key=lambda x: x['date'])
    
    def _get_learning_statistics(self, user, course):
        """Get user's learning statistics for this course."""
        from .models import CourseEnrollment
        
        try:
            enrollment = CourseEnrollment.objects.get(user=user, course=course)
            
            # Calculate various statistics
            time_spent = enrollment.progress_data.get('time_spent', {})
            total_time = sum(time_spent.values())
            avg_time_per_module = total_time / len(time_spent) if time_spent else 0
            
            activity_log = enrollment.progress_data.get('activity_log', [])
            recent_activities = [a for a in activity_log if 
                               datetime.fromisoformat(a['timestamp']) > 
                               timezone.now() - timedelta(days=7)]
            
            return {
                'total_time_minutes': total_time,
                'avg_time_per_module': round(avg_time_per_module, 1),
                'weekly_activities': len(recent_activities),
                'peak_learning_hours': self._calculate_peak_hours(activity_log),
                'consistency_score': self._calculate_consistency_score(enrollment),
                'retention_estimate': self._estimate_retention(enrollment)
            }
            
        except CourseEnrollment.DoesNotExist:
            return None
    
    def _estimate_completion_time(self, course, progress):
        """Estimate time to complete course."""
        if not progress:
            return "90 days (estimated)"
        
        remaining_percentage = 100 - progress.get('percentage', 0)
        days_so_far = (timezone.now() - 
                      datetime.fromisoformat(progress.get('started_at', timezone.now().isoformat()))).days
        
        if progress.get('percentage', 0) > 0:
            days_per_percent = days_so_far / progress.get('percentage', 1)
            remaining_days = remaining_percentage * days_per_percent
            return f"{int(remaining_days)} days (based on your pace)"
        
        return "90 days (estimated)"
    
    def _get_leaderboard_position(self, course, user):
        """Get user's position on course leaderboard."""
        from .models import CourseEnrollment
        
        enrollments = CourseEnrollment.objects.filter(
            course=course, is_active=True
        ).annotate(
            progress_percentage=F('progress_data__completed_modules') * 100 / F('progress_data__total_modules')
        ).order_by('-progress_percentage', 'last_accessed')
        
        positions = list(enrollments.values_list('user_id', flat=True))
        
        try:
            position = positions.index(user.id) + 1
            total = len(positions)
            
            return {
                'position': position,
                'total': total,
                'percentile': round((position / total) * 100) if total > 0 else 0,
                'top_percent': round((position / total) * 100) <= 10 if total > 0 else False
            }
        except ValueError:
            return None
    
    def _calculate_peak_hours(self, activity_log):
        """Calculate user's peak learning hours."""
        if not activity_log:
            return []
        
        hours = []
        for activity in activity_log:
            try:
                hour = datetime.fromisoformat(activity['timestamp']).hour
                hours.append(hour)
            except:
                continue
        
        if hours:
            # Find most frequent hours
            from collections import Counter
            hour_counts = Counter(hours)
            most_common = hour_counts.most_common(3)
            return [hour for hour, count in most_common]
        
        return []
    
    def _calculate_consistency_score(self, enrollment):
        """Calculate learning consistency score."""
        activity_log = enrollment.progress_data.get('activity_log', [])
        
        if not activity_log or len(activity_log) < 7:
            return 0
        
        # Check activity over last 30 days
        recent_activities = [
            a for a in activity_log 
            if datetime.fromisoformat(a['timestamp']) > timezone.now() - timedelta(days=30)
        ]
        
        if not recent_activities:
            return 0
        
        # Group by day
        days_with_activity = set()
        for activity in recent_activities:
            day = datetime.fromisoformat(activity['timestamp']).date()
            days_with_activity.add(day)
        
        consistency = len(days_with_activity) / 30
        return round(consistency * 100, 1)
    
    def _estimate_retention(self, enrollment):
        """Estimate knowledge retention based on learning patterns."""
        # Simplified retention estimation
        activity_log = enrollment.progress_data.get('activity_log', [])
        
        if not activity_log:
            return 50  # Default
        
        # Consider recency and frequency
        recent_activities = len([
            a for a in activity_log 
            if datetime.fromisoformat(a['timestamp']) > timezone.now() - timedelta(days=7)
        ])
        
        total_activities = len(activity_log)
        
        if total_activities == 0:
            return 50
        
        recency_score = min(recent_activities / 7 * 50, 50)  # Up to 50 points
        frequency_score = min(total_activities / 30 * 50, 50)  # Up to 50 points
        
        return round(recency_score + frequency_score)
    
    def _generate_progress_chart(self, enrollment):
        """Generate progress chart as base64 image."""
        try:
            # Get progress data
            progress_data = enrollment.progress_data
            completed = len(progress_data.get('completed_modules', []))
            total = progress_data.get('total_modules', 0)
            
            # Create chart
            fig, ax = plt.subplots(figsize=(10, 4))
            
            # Progress bar
            bars = ax.bar(['Progress'], [completed], color='#4CAF50')
            ax.bar(['Progress'], [total - completed], bottom=[completed], color='#E0E0E0')
            
            # Add percentage text
            ax.text(0, completed + 1, f'{completed}/{total} ({int(completed/total*100)}%)', 
                   ha='center', va='bottom', fontsize=12)
            
            ax.set_ylim(0, total)
            ax.set_ylabel('Modules')
            ax.set_title('Course Progress')
            
            # Convert to base64
            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error generating progress chart: {e}")
            return None
    
    def _generate_time_distribution_chart(self, enrollment):
        """Generate time distribution chart."""
        try:
            time_spent = enrollment.progress_data.get('time_spent', {})
            
            if not time_spent:
                return None
            
            # Prepare data
            modules = list(time_spent.keys())
            times = list(time_spent.values())
            
            # Create chart
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.bar(range(len(modules)), times, color='#2196F3')
            ax.set_xlabel('Modules')
            ax.set_ylabel('Time Spent (minutes)')
            ax.set_title('Time Distribution Across Modules')
            ax.set_xticks(range(len(modules)))
            ax.set_xticklabels([f'M{i}' for i in modules], rotation=45)
            
            # Convert to base64
            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error generating time chart: {e}")
            return None
    
    def _calculate_learning_metrics(self, enrollment):
        """Calculate comprehensive learning metrics."""
        progress_data = enrollment.progress_data
        
        # Basic metrics
        completed = len(progress_data.get('completed_modules', []))
        total = progress_data.get('total_modules', 0)
        time_spent = sum(progress_data.get('time_spent', {}).values())
        
        # Advanced metrics
        activity_log = progress_data.get('activity_log', [])
        recent_activities = [
            a for a in activity_log 
            if datetime.fromisoformat(a['timestamp']) > timezone.now() - timedelta(days=7)
        ]
        
        # Calculate engagement score
        engagement_score = min(len(recent_activities) * 10, 100)
        
        # Calculate efficiency score (time per module)
        avg_time_per_module = time_spent / completed if completed > 0 else 0
        efficiency_score = max(0, 100 - (avg_time_per_module / 60))  # Assuming 1 hour is optimal
        
        # Calculate consistency score
        consistency_score = self._calculate_consistency_score(enrollment)
        
        return {
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 1),
            'total_time_hours': round(time_spent / 60, 1),
            'avg_time_per_module': round(avg_time_per_module, 1),
            'engagement_score': round(engagement_score, 1),
            'efficiency_score': round(efficiency_score, 1),
            'consistency_score': round(consistency_score, 1),
            'streak_days': progress_data.get('streak_days', 0),
            'achievements_count': len(progress_data.get('achievements', []))
        }
    
    def _generate_performance_recommendations(self, enrollment, metrics):
        """Generate personalized recommendations based on performance."""
        recommendations = []
        
        # Based on completion rate
        if metrics['completion_rate'] < 30:
            recommendations.append({
                'area': 'Pace',
                'suggestion': 'Try to complete at least one module every 3 days to stay on track.',
                'action': 'Set daily learning goals'
            })
        
        # Based on engagement
        if metrics['engagement_score'] < 50:
            recommendations.append({
                'area': 'Engagement',
                'suggestion': 'Try to engage with course materials daily, even for short periods.',
                'action': 'Schedule 20-minute daily sessions'
            })
        
        # Based on efficiency
        if metrics['efficiency_score'] < 40:
            recommendations.append({
                'area': 'Efficiency',
                'suggestion': 'Consider focusing on key concepts rather than trying to master everything at once.',
                'action': 'Use the 80/20 rule - focus on core concepts'
            })
        
        # Based on consistency
        if metrics['consistency_score'] < 60:
            recommendations.append({
                'area': 'Consistency',
                'suggestion': 'Regular short study sessions are more effective than occasional long ones.',
                'action': 'Establish a daily learning routine'
            })
        
        return recommendations
    
    def _compare_with_peers(self, course, enrollment):
        """Compare user's performance with peers."""
        from .models import CourseEnrollment
        
        peers = CourseEnrollment.objects.filter(
            course=course, 
            is_active=True
        ).exclude(user=enrollment.user)
        
        if not peers.exists():
            return None
        
        # Calculate peer averages
        peer_progress = []
        peer_times = []
        
        for peer in peers:
            peer_progress.append(peer.get_progress_percentage())
            time_spent = sum(peer.progress_data.get('time_spent', {}).values())
            peer_times.append(time_spent)
        
        user_progress = enrollment.get_progress_percentage()
        user_time = sum(enrollment.progress_data.get('time_spent', {}).values())
        
        return {
            'user_progress': round(user_progress, 1),
            'peer_avg_progress': round(statistics.mean(peer_progress) if peer_progress else 0, 1),
            'user_time_hours': round(user_time / 60, 1),
            'peer_avg_time_hours': round(statistics.mean(peer_times) / 60 if peer_times else 0, 1),
            'percentile_progress': self._calculate_percentile(user_progress, peer_progress),
            'comparison': 'above_average' if user_progress > statistics.mean(peer_progress) else 'below_average'
        }
    
    def _calculate_percentile(self, user_value, peer_values):
        """Calculate percentile rank."""
        if not peer_values:
            return 50
        
        count_below = sum(1 for v in peer_values if v < user_value)
        total = len(peer_values)
        
        return round((count_below / total) * 100) if total > 0 else 50
    
    def _generate_report_data(self, enrollment, metrics):
        """Generate comprehensive report data."""
        course = enrollment.course
        user = enrollment.user
        
        return {
            'report_id': f"REPORT-{uuid.uuid4().hex[:8].upper()}",
            'generated_at': timezone.now().isoformat(),
            'student': {
                'name': user.get_full_name() or user.email,
                'email': user.email,
                'enrollment_date': enrollment.enrollment_date.date().isoformat()
            },
            'course': {
                'title': course.title,
                'code': course.slug,
                'level': course.level,
                'instructor': course.instructors.first().user.get_full_name() if course.instructors.exists() else 'N/A'
            },
            'metrics': metrics,
            'summary': self._generate_report_summary(metrics),
            'next_steps': [
                f"Aim for {metrics['completion_rate'] + 20}% completion in the next 30 days",
                "Participate in at least 2 discussion forums per week",
                "Complete one practice assignment weekly"
            ]
        }
    
    def _generate_report_summary(self, metrics):
        """Generate textual summary of performance."""
        strengths = []
        areas_for_improvement = []
        
        if metrics['engagement_score'] > 70:
            strengths.append("Excellent engagement with course materials")
        else:
            areas_for_improvement.append("Increase engagement frequency")
        
        if metrics['efficiency_score'] > 60:
            strengths.append("Good learning efficiency")
        else:
            areas_for_improvement.append("Improve time management during study sessions")
        
        if metrics['consistency_score'] > 70:
            strengths.append("Strong consistency in learning habits")
        else:
            areas_for_improvement.append("Work on maintaining regular study schedule")
        
        summary = "Overall, you're making good progress. "
        if strengths:
            summary += f"Your strengths include: {', '.join(strength.lower() for strength in strengths)}. "
        if areas_for_improvement:
            summary += f"Areas for improvement: {', '.join(area.lower() for area in areas_for_improvement)}."
        
        return summary
    
    def _setup_course_notifications(self, course):
        """Set up default notification templates for a course."""
        notification_templates = {
            'welcome': {
                'subject': f'Welcome to {course.title}! 🎉',
                'template': 'courses/notifications/welcome.html'
            },
            'module_release': {
                'subject': 'New Module Available: {module_title}',
                'template': 'courses/notifications/module_release.html'
            },
            'reminder': {
                'subject': 'Reminder: {event_title} starts soon!',
                'template': 'courses/notifications/reminder.html'
            },
            'achievement': {
                'subject': 'Achievement Unlocked! 🏆',
                'template': 'courses/notifications/achievement.html'
            },
            'deadline': {
                'subject': 'Upcoming Deadline: {assignment_title}',
                'template': 'courses/notifications/deadline.html'
            }
        }
        
        # Store templates in course metadata
        if not hasattr(course, 'notification_templates'):
            course.notification_templates = notification_templates
            course.save()
    
    def _send_enrollment_notifications(self, course, enrollment):
        """Send comprehensive enrollment notifications."""
        # Welcome email
        context = {
            'user': enrollment.user,
            'course': course,
            'enrollment': enrollment,
            'dashboard_url': f"{settings.SITE_URL}/courses/{course.slug}/dashboard",
            'start_date': course.start_date.strftime("%B %d, %Y"),
            'modules_count': course.modules.count(),
            'instructor': course.instructors.first().user.get_full_name() if course.instructors.exists() else 'The Instructor'
        }
        
        # Send welcome email
        html_message = render_to_string('courses/emails/enrollment_welcome.html', context)
        text_message = render_to_string('courses/emails/enrollment_welcome.txt', context)
        
        send_mail(
            subject=f"🎉 Welcome to {course.title}!",
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[enrollment.user.email],
            html_message=html_message,
            fail_silently=True
        )
        
        # Send onboarding sequence
        self._send_onboarding_sequence(course, enrollment)
    
    def _send_onboarding_sequence(self, course, enrollment):
        """Send onboarding email sequence."""
        sequences = [
            {
                'delay_days': 1,
                'subject': f'Getting Started with {course.title}',
                'template': 'courses/emails/onboarding_day1.html'
            },
            {
                'delay_days': 3,
                'subject': 'Your Learning Path & Resources',
                'template': 'courses/emails/onboarding_day3.html'
            },
            {
                'delay_days': 7,
                'subject': 'Week 1 Check-in & Community',
                'template': 'courses/emails/onboarding_day7.html'
            }
        ]
        
        # In a production environment, you would use a task queue (Celery)
        # For now, we'll store the sequence in the enrollment data
        enrollment.progress_data['onboarding_sequence'] = sequences
        enrollment.save()
    
    def _start_welcome_sequence(self, course, enrollment):
        """Start the welcome interaction sequence."""
        # Create initial tasks/checklist
        checklist = [
            {'task': 'Complete profile setup', 'completed': False},
            {'task': 'Review course syllabus', 'completed': False},
            {'task': 'Join course community', 'completed': False},
            {'task': 'Set learning goals', 'completed': False},
            {'task': 'Start Module 1', 'completed': False}
        ]
        
        enrollment.progress_data['onboarding_checklist'] = checklist
        
        # Set initial learning goals
        goals = {
            'weekly_goal': 'Complete 2-3 modules per week',
            'daily_commitment': '30-60 minutes of focused learning',
            'target_completion': course.end_date.strftime("%B %d, %Y")
        }
        
        enrollment.progress_data['learning_goals'] = goals
        enrollment.save()
    
    def _update_learning_path(self, user, course):
        """Update user's learning path with new course."""
        from .models import UserLearningPath
        
        learning_path, created = UserLearningPath.objects.get_or_create(
            user=user,
            defaults={'path_data': {'courses': [], 'skills': [], 'goals': []}}
        )
        
        path_data = learning_path.path_data
        if course.slug not in [c['slug'] for c in path_data.get('courses', [])]:
            path_data.setdefault('courses', []).append({
                'slug': course.slug,
                'title': course.title,
                'added_date': timezone.now().isoformat(),
                'status': 'in_progress',
                'priority': 'medium'
            })
            
            learning_path.path_data = path_data
            learning_path.save()
    
    def _check_achievements(self, enrollment):
        """Check and award achievements based on progress."""
        achievements = []
        
        progress_data = enrollment.progress_data
        completed_modules = len(progress_data.get('completed_modules', []))
        streak_days = progress_data.get('streak_days', 0)
        
        # Module completion achievements
        if completed_modules >= 5 and 'module_master_5' not in progress_data.get('achievements', []):
            achievements.append(self._award_achievement(enrollment, 'module_master_5'))
        
        if completed_modules >= 10 and 'module_master_10' not in progress_data.get('achievements', []):
            achievements.append(self._award_achievement(enrollment, 'module_master_10'))
        
        # Streak achievements
        if streak_days >= 7 and 'weekly_streak' not in progress_data.get('achievements', []):
            achievements.append(self._award_achievement(enrollment, 'weekly_streak'))
        
        if streak_days >= 30 and 'monthly_streak' not in progress_data.get('achievements', []):
            achievements.append(self._award_achievement(enrollment, 'monthly_streak'))
        
        # Time spent achievements
        total_time = sum(progress_data.get('time_spent', {}).values())
        if total_time >= 600 and 'time_investor' not in progress_data.get('achievements', []):  # 10 hours
            achievements.append(self._award_achievement(enrollment, 'time_investor'))
        
        return achievements
    
    def _award_achievement(self, enrollment, achievement_key):
        """Award an achievement to user."""
        achievement_definitions = {
            'module_master_5': {
                'title': 'Module Master (5)',
                'description': 'Completed 5 modules',
                'icon': '📚',
                'points': 50
            },
            'module_master_10': {
                'title': 'Module Master (10)',
                'description': 'Completed 10 modules',
                'icon': '🏆',
                'points': 100
            },
            'weekly_streak': {
                'title': 'Weekly Streak',
                'description': '7 consecutive days of learning',
                'icon': '🔥',
                'points': 75
            },
            'monthly_streak': {
                'title': 'Monthly Streak',
                'description': '30 consecutive days of learning',
                'icon': '⚡',
                'points': 200
            },
            'time_investor': {
                'title': 'Time Investor',
                'description': 'Spent 10+ hours learning',
                'icon': '⏰',
                'points': 150
            }
        }
        
        if achievement_key in achievement_definitions:
            achievement = achievement_definitions[achievement_key]
            
            # Add to user's achievements
            achievements = enrollment.progress_data.get('achievements', [])
            if achievement_key not in achievements:
                achievements.append(achievement_key)
                enrollment.progress_data['achievements'] = achievements
                
                # Add points
                current_points = enrollment.progress_data.get('points', 0)
                enrollment.progress_data['points'] = current_points + achievement['points']
                
                enrollment.save()
                
                # Send notification
                self._send_achievement_notification(enrollment.user, achievement)
                
                return achievement
        
        return None
    
    def _send_achievement_notification(self, user, achievement):
        """Send achievement notification."""
        context = {
            'user': user,
            'achievement': achievement,
            'unlocked_at': timezone.now().strftime("%B %d, %Y at %I:%M %p")
        }
        
        html_message = render_to_string('courses/emails/achievement_unlocked.html', context)
        text_message = render_to_string('courses/emails/achievement_unlocked.txt', context)
        
        send_mail(
            subject=f"🏆 Achievement Unlocked: {achievement['title']}!",
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True
        )
    
    def _process_payment(self, course, payment_info):
        """Process course payment."""
        if not payment_info and hasattr(settings, 'STRIPE_SECRET_KEY'):
            # Create Stripe checkout session
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': course.title,
                                'description': course.short_description,
                            },
                            'unit_amount': int(course.price * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f"{settings.SITE_URL}/courses/{course.slug}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=f"{settings.SITE_URL}/courses/{course.slug}",
                    metadata={
                        'course_slug': course.slug,
                        'user_id': self.user.id
                    }
                )
                
                return {
                    'success': True,
                    'requires_action': True,
                    'payment_data': {
                        'session_id': checkout_session.id,
                        'redirect_url': checkout_session.url
                    }
                }
                
            except stripe.error.StripeError as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        elif payment_info and payment_info.get('payment_method') == 'manual':
            # Manual payment (e.g., invoice, bank transfer)
            return {
                'success': True,
                'payment_data': {
                    'method': 'manual',
                    'status': 'pending',
                    'invoice_id': f"INV-{uuid.uuid4().hex[:8].upper()}"
                }
            }
        
        return {
            'success': False,
            'error': 'Payment information required'
        }
    
    def _prepare_notification(self, notification_type, user, course, data):
        """Prepare notification data."""
        templates = {
            'module_released': {
                'subject': f'New Module Available: {data.get("module_title", "New Content")}',
                'message': f'A new module "{data.get("module_title")}" is now available in {course.title}.',
                'priority': 'medium'
            },
            'live_session': {
                'subject': f'Live Session Reminder: {data.get("session_title", "Upcoming Session")}',
                'message': f'Live session "{data.get("session_title")}" starts in 1 hour.',
                'priority': 'high'
            },
            'deadline': {
                'subject': f'Deadline Approaching: {data.get("assignment_title", "Assignment")}',
                'message': f'Assignment "{data.get("assignment_title")}" is due in 24 hours.',
                'priority': 'high'
            },
            'announcement': {
                'subject': f'Course Announcement: {data.get("title", "Important Update")}',
                'message': data.get("message", "Check the course announcements for updates."),
                'priority': data.get("priority", "medium")
            }
        }
        
        template = templates.get(notification_type, {
            'subject': 'Course Notification',
            'message': 'You have a new notification.',
            'priority': 'medium'
        })
        
        return {
            'subject': template['subject'],
            'message': template['message'],
            'priority': template['priority'],
            'user': user,
            'course': course,
            'notification_type': notification_type,
            'timestamp': timezone.now().isoformat()
        }
    
    def _send_email_notification(self, email, subject, message, html_message=None):
        """Send email notification."""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            return False
    
    def _create_in_app_notification(self, user, notification_data):
        """Create in-app notification."""
        from .models import Notification
        
        Notification.objects.create(
            user=user,
            title=notification_data['subject'],
            message=notification_data['message'],
            notification_type=notification_data['notification_type'],
            priority=notification_data['priority'],
            data={
                'course_slug': notification_data['course'].slug,
                'timestamp': notification_data['timestamp']
            }
        )
        return True
    
    def _send_push_notification(self, user, notification_data):
        """Send push notification (Firebase Cloud Messaging)."""
        # This is a placeholder - in production, you would integrate with FCM
        try:
            # Implementation would go here
            pass
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
        
        return False
    
    def _get_weekly_trend(self, course):
        """Get weekly enrollment and activity trend."""
        # Calculate trend for last 8 weeks
        end_date = timezone.now().date()
        start_date = end_date - timedelta(weeks=8)
        
        from .models import CourseEnrollment
        
        # Get weekly enrollments
        weekly_data = []
        for week in range(8):
            week_start = start_date + timedelta(weeks=week)
            week_end = week_start + timedelta(days=6)
            
            enrollments = CourseEnrollment.objects.filter(
                course=course,
                enrollment_date__date__range=[week_start, week_end]
            ).count()
            
            weekly_data.append({
                'week': week_start.strftime('%b %d'),
                'enrollments': enrollments
            })
        
        return weekly_data
    
    def _get_module_popularity(self, course):
        """Get module popularity based on completion rates."""
        from .models import CourseEnrollment
        
        enrollments = CourseEnrollment.objects.filter(course=course, is_active=True)
        total_enrolled = enrollments.count()
        
        if total_enrolled == 0:
            return []
        
        module_completion = {}
        for module in course.modules.filter(is_published=True):
            completed_count = sum(
                1 for e in enrollments 
                if module.id in e.progress_data.get('completed_modules', [])
            )
            completion_rate = (completed_count / total_enrolled * 100) if total_enrolled > 0 else 0
            
            module_completion[module.title] = round(completion_rate, 1)
        
        # Sort by completion rate
        sorted_modules = sorted(
            module_completion.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return [{'module': name, 'completion_rate': rate} for name, rate in sorted_modules]
    
    def _get_time_of_day_activity(self, course):
        """Get activity distribution by time of day."""
        from .models import CourseEnrollment
        
        # This would typically come from activity logs
        # For now, simulate based on last access times
        enrollments = CourseEnrollment.objects.filter(
            course=course,
            last_accessed__gte=timezone.now() - timedelta(days=30)
        )
        
        hour_counts = {str(hour): 0 for hour in range(24)}
        
        for enrollment in enrollments:
            hour = enrollment.last_accessed.hour
            hour_counts[str(hour)] += 1
        
        # Convert to percentage
        total = sum(hour_counts.values())
        if total > 0:
            for hour in hour_counts:
                hour_counts[hour] = round((hour_counts[hour] / total) * 100, 1)
        
        return hour_counts
    
    def _get_module_progress(self, module, enrollment):
        """Get detailed progress for a specific module."""
        progress_data = enrollment.progress_data
        
        # Check if module is completed
        if module.id in progress_data.get('completed_modules', []):
            return 100
        
        # Check time spent
        time_spent = progress_data.get('time_spent', {}).get(str(module.id), 0)
        
        # Estimate progress based on time spent (assuming 60 minutes per module)
        if time_spent > 0:
            estimated_progress = min((time_spent / 60) * 100, 95)  # Max 95% until completed
            return round(estimated_progress, 1)
        
        return 0
    
    def _get_module_notes(self, enrollment, module_id):
        """Get user's notes for a specific module."""
        all_notes = enrollment.progress_data.get('notes', [])
        module_notes = [note for note in all_notes if note.get('module_id') == module_id]
        return module_notes
    
    def _can_enroll(self, course):
        """Enhanced enrollment check."""
        if not self.user:
            return False
        
        # Check if user already enrolled
        from .models import CourseEnrollment
        if CourseEnrollment.objects.filter(user=self.user, course=course).exists():
            return False
        
        # Check course status
        if course.status not in ['upcoming', 'active']:
            return False
        
        # Check prerequisites
        if course.prerequisites:
            # Could implement prerequisite checking here
            pass
        
        # Check enrollment limits (if any)
        if hasattr(course, 'max_enrollments') and course.max_enrollments:
            current_enrollments = CourseEnrollment.objects.filter(course=course, is_active=True).count()
            if current_enrollments >= course.max_enrollments:
                return False
        
        return True
    
    def _format_module_resources(self, module):
        """Format resources with enhanced information."""
        resources = {}
        
        if module.slides_url:
            resources['slides'] = {
                'url': module.slides_url,
                'label': 'Slides',
                'icon': '📊',
                'type': 'presentation',
                'estimated_time': '30 min'
            }
        
        if module.video_url:
            resources['video'] = {
                'url': module.video_url,
                'label': 'Video Lecture',
                'icon': '🎥',
                'type': 'video',
                'estimated_time': '45 min'
            }
        
        if module.code_url:
            resources['code'] = {
                'url': module.code_url,
                'label': 'Code Examples',
                'icon': '💻',
                'type': 'code',
                'estimated_time': '60 min'
            }
        
        # Add meeting link
        if module.lecture_meeting and module.lecture_meeting.meeting_link:
            resources['meeting'] = {
                'url': module.lecture_meeting.meeting_link,
                'label': 'Live Session',
                'icon': '🎯',
                'type': 'live',
                'estimated_time': '90 min'
            }
        
        # Add practice exercises if available
        if hasattr(module, 'exercises_url') and module.exercises_url:
            resources['exercises'] = {
                'url': module.exercises_url,
                'label': 'Practice Exercises',
                'icon': '📝',
                'type': 'practice',
                'estimated_time': '45 min'
            }
        
        return resources
    
    def _analyze_learning_patterns(self, enrollment):
        """Analyze user's learning patterns."""
        progress_data = enrollment.progress_data
        
        patterns = {
            'preferred_learning_times': [],
            'session_lengths': [],
            'content_preferences': {},
            'retention_rate': 0,
            'consistency_score': 0
        }
        
        # Analyze activity log
        activity_log = progress_data.get('activity_log', [])
        if activity_log:
            # Extract times
            times = []
            durations = []
            
            for activity in activity_log:
                try:
                    timestamp = datetime.fromisoformat(activity['timestamp'])
                    times.append(timestamp.hour)
                    durations.append(activity.get('duration', 0))
                except:
                    continue
            
            if times:
                # Find peak hours
                from collections import Counter
                hour_counts = Counter(times)
                common_hours = hour_counts.most_common(3)
                patterns['preferred_learning_times'] = [hour for hour, count in common_hours]
            
            if durations:
                patterns['average_session_length'] = statistics.mean(durations)
        
        return patterns
    
    def _get_learning_style(self, user):
        """Determine user's learning style."""
        # This could be based on user preferences or inferred from behavior
        # For now, return a default
        return {
            'style': 'visual',  # visual, auditory, reading/writing, kinesthetic
            'confidence': 0.7,
            'recommended_adaptations': ['video_content', 'diagrams', 'interactive_visuals']
        }
    
    def _generate_personalized_path(self, course, enrollment, learning_patterns, learning_style):
        """Generate personalized learning path."""
        modules = list(course.modules.filter(is_published=True).order_by('order'))
        
        personalized_path = []
        for module in modules:
            module_info = {
                'id': module.id,
                'title': module.title,
                'order': module.order,
                'recommended_order': module.order,  # May be adjusted
                'suggested_schedule': self._suggest_schedule(module, learning_patterns),
                'recommended_resources': self._recommend_resources(module, learning_style),
                'estimated_time': module.metadata.get('estimated_duration', '60 minutes') if hasattr(module, 'metadata') else '60 minutes',
                'difficulty': module.metadata.get('difficulty', 'medium') if hasattr(module, 'metadata') else 'medium',
                'prerequisites': module.metadata.get('prerequisites', []) if hasattr(module, 'metadata') else []
            }
            
            personalized_path.append(module_info)
        
        return personalized_path
    
    def _suggest_schedule(self, module, learning_patterns):
        """Suggest optimal schedule for module completion."""
        preferred_hours = learning_patterns.get('preferred_learning_times', [9, 14, 20])
        
        if preferred_hours:
            best_hour = preferred_hours[0]
            return {
                'best_time_of_day': f"{best_hour}:00",
                'suggested_days': ['Monday', 'Wednesday', 'Friday'],
                'estimated_sessions': 2,
                'session_length': '45 minutes'
            }
        
        return {
            'best_time_of_day': 'Evening',
            'suggested_days': ['Flexible'],
            'estimated_sessions': 2,
            'session_length': '45 minutes'
        }
    
    def _recommend_resources(self, module, learning_style):
        """Recommend resources based on learning style."""
        style = learning_style.get('style', 'visual')
        
        recommendations = []
        
        if style == 'visual':
            if module.video_url:
                recommendations.append({'type': 'video', 'priority': 'high'})
            if module.slides_url:
                recommendations.append({'type': 'slides', 'priority': 'medium'})
        
        elif style == 'auditory':
            if module.video_url:
                recommendations.append({'type': 'video', 'priority': 'high'})
            recommendations.append({'type': 'audio_summary', 'priority': 'medium'})
        
        elif style == 'reading/writing':
            if module.slides_url:
                recommendations.append({'type': 'slides', 'priority': 'high'})
            recommendations.append({'type': 'reading_material', 'priority': 'high'})
        
        else:  # kinesthetic
            if module.code_url:
                recommendations.append({'type': 'code', 'priority': 'high'})
            recommendations.append({'type': 'hands_on_exercise', 'priority': 'high'})
        
        return recommendations
    
    def _calculate_total_time(self, learning_path):
        """Calculate total estimated time for learning path."""
        total_minutes = 0
        
        for module in learning_path:
            time_str = module.get('estimated_time', '60 minutes')
            # Parse time string (simplified)
            if 'hour' in time_str.lower():
                hours = int(time_str.split()[0])
                total_minutes += hours * 60
            else:
                minutes = int(time_str.split()[0])
                total_minutes += minutes
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        return f"{hours}h {minutes}m"
    
    def _recommend_pace(self, enrollment, learning_path):
        """Recommend learning pace based on user's schedule."""
        progress_data = enrollment.progress_data
        completed = len(progress_data.get('completed_modules', []))
        total = len(learning_path)
        
        if completed == 0:
            return {
                'pace': 'moderate',
                'modules_per_week': 2,
                'hours_per_week': 4,
                'expected_completion': '12 weeks'
            }
        
        # Calculate current pace
        started_at = datetime.fromisoformat(progress_data.get('started_at', timezone.now().isoformat()))
        days_elapsed = (timezone.now() - started_at).days
        
        if days_elapsed == 0:
            days_elapsed = 1
        
        current_pace = completed / days_elapsed
        remaining_modules = total - completed
        
        if current_pace < 0.5:  # Less than half a module per day
            return {
                'pace': 'gentle',
                'modules_per_week': 2,
                'hours_per_week': 3,
                'expected_completion': f'{int(remaining_modules / 0.3)} days'
            }
        elif current_pace < 1:
            return {
                'pace': 'moderate',
                'modules_per_week': 4,
                'hours_per_week': 6,
                'expected_completion': f'{int(remaining_modules / 0.7)} days'
            }
        else:
            return {
                'pace': 'intensive',
                'modules_per_week': 7,
                'hours_per_week': 10,
                'expected_completion': f'{int(remaining_modules / 1.2)} days'
            }
    
    def _suggest_difficulty_adjustment(self, enrollment):
        """Suggest difficulty adjustments based on performance."""
        progress_data = enrollment.progress_data
        quiz_scores = progress_data.get('quiz_scores', {})
        
        if not quiz_scores:
            return {
                'adjustment': 'none',
                'reason': 'Insufficient performance data',
                'suggestion': 'Complete a few quizzes to get personalized suggestions'
            }
        
        # Calculate average score
        scores = list(quiz_scores.values())
        avg_score = statistics.mean(scores) if scores else 0
        
        if avg_score > 85:
            return {
                'adjustment': 'increase',
                'reason': 'Excellent quiz performance',
                'suggestion': 'Try advanced exercises and challenge problems'
            }
        elif avg_score > 70:
            return {
                'adjustment': 'maintain',
                'reason': 'Good understanding of material',
                'suggestion': 'Continue current pace, focus on weak areas'
            }
        else:
            return {
                'adjustment': 'decrease',
                'reason': 'Struggling with current difficulty',
                'suggestion': 'Review foundational concepts and use additional practice resources'
            }
    
    def _get_default_learning_path(self, course):
        """Get default learning path for new users."""
        modules = list(course.modules.filter(is_published=True).order_by('order'))
        
        default_path = []
        for module in modules:
            default_path.append({
                'week': (module.order - 1) // 3 + 1,
                'day': (module.order - 1) % 3 + 1,
                'module': module.title,
                'focus': self._extract_key_concepts(module.description),
                'activities': [
                    'Watch lecture video',
                    'Review slides',
                    'Complete practice exercises',
                    'Participate in discussion'
                ]
            })
        
        return {
            'path': default_path,
            'total_weeks': len(modules) // 3 + 1,
            'weekly_commitment': '4-6 hours',
            'recommended_schedule': 'Mon/Wed/Fri for 1-2 hours'
        }
    
    def _extract_key_concepts(self, description):
        """Extract key concepts from module description."""
        # Simplified extraction - in production, use NLP
        keywords = ['function', 'equation', 'theory', 'principle', 'method', 'analysis']
        found = []
        
        for keyword in keywords:
            if keyword in description.lower():
                found.append(keyword.capitalize())
        
        return found[:3] if found else ['Core concepts']