# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import datetime
import json

# Assuming you have a rich text editor integrated, like django-ckeditor or django-tinymce.
# If not, the 'content' fields will be basic text areas.
# from ckeditor.fields import RichTextField # Example if using CKEditor


class CustomUser(AbstractUser):
    """
    Custom User model to allow login with email and add a phone number.
    The username field is kept for compatibility with Django's admin,
    but email is the primary login field.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(
        _('phone number'),
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    # Set email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('Custom User')
        verbose_name_plural = _('Custom Users')


### Portfolio Content Models

# Skill Model
class Skill(models.Model):
    """Represents a skill with a proficiency level and an optional icon."""
    name = models.CharField(max_length=100, unique=True)
    proficiency = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Proficiency percentage (0-100)"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="FontAwesome or other icon class for visual representation (e.g., 'fa-python')"
    )
    description = models.TextField(blank=True, help_text="A brief description of the skill.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-proficiency']
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')


# Project Model
class Project(models.Model):
    """Details about a personal project."""
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('planned', 'Planned'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from title.")
    description = models.TextField(help_text="Detailed description of the project.")
    image = models.ImageField(upload_to='projects/', blank=True, null=True, help_text="Thumbnail or main image for the project.")
    url = models.URLField(blank=True, help_text="Link to live project demo or GitHub repository.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills_used = models.ManyToManyField(Skill, related_name='projects', blank=True, help_text="Skills applied in this project.")
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags (e.g., 'Django, Tailwind CSS, Python')."
    )
    is_featured = models.BooleanField(default=False, help_text="Check if this project should be featured on the homepage.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')


# Testimonial Model
class Testimonial(models.Model):
    """Stores testimonials from clients or colleagues."""
    author = models.CharField(max_length=100)
    role = models.CharField(
        max_length=100,
        blank=True,
        help_text="Author's role or company (e.g., 'CEO of Example Corp')."
    )
    content = models.TextField(help_text="The actual testimonial text.")
    image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        help_text="Optional profile picture of the testimonial author."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(
        default=False,
        help_text="Check to display this testimonial prominently."
    )

    def __str__(self):
        return f"Testimonial by {self.author}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Testimonial')
        verbose_name_plural = _('Testimonials')


### Enhanced Blog/Notes/Media Models

class BlogPost(models.Model):
    """Represents a blog post, supporting rich HTML content."""
    CATEGORY_CHOICES = [
        ('web_dev', 'Web Development'),
        ('design', 'Design'),
        ('career', 'Career'),
        ('tutorial', 'Tutorial'),
        ('personal', 'Personal'),
        ('tech_review', 'Technology Review'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from title.")
    content = models.TextField(help_text="The full content of the blog post. Can contain HTML.")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_posts',
        help_text="The author of this blog post."
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='web_dev')
    image = models.ImageField(upload_to='blog_covers/', blank=True, null=True, help_text="Main image/cover for the blog post.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False, help_text="Check to make the post publicly visible.")
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags for search and filtering (e.g., 'Django, Frontend, Tutorial')."
    )
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
            ('private', 'Private (Admin Only)')
        ],
        default='public',
        help_text="Who can view this blog post?"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Blog Post')
        verbose_name_plural = _('Blog Posts')


class Note(models.Model):
    """For quick notes or short articles, potentially for registered users only."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(help_text="The content of the note. Can contain HTML.")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
        help_text="The author of this note."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False, help_text="Should this note be publicly visible?")
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
            ('private', 'Private (Author Only)')
        ],
        default='registered',
        help_text="Who can view this note?"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')


class Document(models.Model):
    """For uploading and categorizing files like PDFs, slides, or other documents."""
    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('slides', 'Presentation Slides'),
        ('ebook', 'E-Book'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, help_text="A brief description of the document.")
    file = models.FileField(
        upload_to='documents/',
        help_text="Upload your PDF, PPT, or other relevant document."
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='pdf')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
        help_text="The user who uploaded this document."
    )
    is_published = models.BooleanField(default=False, help_text="Check to make the document publicly downloadable.")
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
            ('private', 'Private (Admin Only)')
        ],
        default='registered',
        help_text="Who can access/download this document?"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('document_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')


class Book(models.Model):
    """Represents a book, either one you recommend or one you've written."""
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, help_text="Author(s) of the book.")
    isbn = models.CharField(max_length=13, blank=True, null=True, unique=True, help_text="International Standard Book Number (ISBN-13).")
    genre = models.CharField(max_length=100, blank=True, help_text="Genre of the book (e.g., 'Fiction', 'Non-fiction', 'Technology').")
    description = models.TextField(blank=True, help_text="A brief summary or review of the book.")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True, help_text="Cover image of the book.")
    purchase_link = models.URLField(blank=True, help_text="Link to purchase the book (e.g., Amazon, publisher's site).")
    recommended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommended_books',
        help_text="The user who recommended this book (likely yourself)."
    )
    published_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False, help_text="Check to feature this book prominently.")
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
        ],
        default='public',
        help_text="Who can view this book listing?"
    )

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['title']
        verbose_name = _('Book')
        verbose_name_plural = _('Books')


### Meetings & Contact Models

class Meeting(models.Model):
    """
    Represents a scheduled meeting or lecture. Users can 'register' for these.
    """
    MEETING_TYPE_CHOICES = [
        ('1-on-1', 'One-on-One Consultation'),
        ('group_lecture', 'Group Lecture/Webinar'),
        ('discovery_call', 'Discovery Call'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200, help_text="Name or topic of the meeting/lecture.")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from title.")
    description = models.TextField(help_text="Detailed agenda or description of the meeting.")
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='1-on-1')
    date = models.DateField(default=datetime.date.today, help_text="Date of the meeting.")
    start_time = models.TimeField(help_text="Start time of the meeting (e.g., 14:00).")
    end_time = models.TimeField(blank=True, null=True, help_text="End time of the meeting (optional).")
    duration_minutes = models.IntegerField(blank=True, null=True, help_text="Duration in minutes.")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offered_meetings',
        help_text="The user offering this meeting/lecture (likely you)."
    )
    meeting_link = models.URLField(blank=True, help_text="Link to the video conferencing room.")
    max_attendees = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of participants allowed (for group lectures)."
    )
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='booked_meetings',
        blank=True,
        help_text="Users who have booked/registered for this meeting."
    )
    is_active = models.BooleanField(default=True, help_text="Is this meeting slot currently available for booking?")
    requires_registration = models.BooleanField(
        default=True,
        help_text="Does this meeting require users to register?"
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Optional: Price for this meeting slot (e.g., for consultations)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} on {self.date} at {self.start_time}"

    def get_absolute_url(self):
        return reverse('meeting_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = _('Meeting/Lecture')
        verbose_name_plural = _('Meetings/Lectures')


class ContactMessage(models.Model):
    """Stores messages submitted via the contact form."""
    name = models.CharField(max_length=100, help_text="Name of the sender.")
    email = models.EmailField(help_text="Email address of the sender.")
    subject = models.CharField(max_length=200, help_text="Subject of the message.")
    message = models.TextField(help_text="The content of the message.")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, help_text="Mark as read once processed.")

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')


### Course System Models

class Course(models.Model):
    """Represents a complete course offering."""
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.TextField(max_length=300, blank=True)
    banner_image = models.ImageField(upload_to='course_banners/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    
    # Course metadata
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    is_featured = models.BooleanField(default=False)
    
    # Schedule
    start_date = models.DateField()
    end_date = models.DateField()
    schedule_note = models.TextField(blank=True, help_text="e.g., Mon-Fri 1-4pm ET")
    location = models.CharField(max_length=255, blank=True)
    is_virtual = models.BooleanField(default=True)
    
    # Pricing/access
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_free = models.BooleanField(default=True)
    access_level = models.CharField(max_length=20, choices=[
        ('public', 'Public'),
        ('registered', 'Registered Users'),
        ('enrolled', 'Enrolled Students Only'),
    ], default='enrolled')
    
    # Prerequisites
    prerequisites = models.TextField(blank=True)
    learning_objectives = models.JSONField(default=list, blank=True, help_text="List of learning objectives")
    
    # Relations to existing models
    meetings = models.ManyToManyField('Meeting', related_name='courses', blank=True)
    notes = models.ManyToManyField('Note', related_name='courses', blank=True)
    books = models.ManyToManyField('Book', related_name='courses', blank=True)
    documents = models.ManyToManyField('Document', related_name='courses', blank=True)
    projects = models.ManyToManyField('Project', related_name='courses', blank=True)
    
    # Statistics
    enrolled_count = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')


class CourseModule(models.Model):
    """Represents a module or lecture within a course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    date = models.DateField(blank=True, null=True)
    is_live_session = models.BooleanField(default=False)
    
    # Links to materials
    lecture_meeting = models.ForeignKey('Meeting', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.ManyToManyField('Note', blank=True)
    documents = models.ManyToManyField('Document', blank=True)
    projects = models.ManyToManyField('Project', blank=True)
    
    # Status
    is_published = models.BooleanField(default=True)
    
    # Resources
    slides_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    code_url = models.URLField(blank=True)
    additional_resources = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseEnrollment(models.Model):
    """Tracks user enrollment in courses."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    progress_data = models.JSONField(default=dict, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('Course Enrollment')
        verbose_name_plural = _('Course Enrollments')
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
    
    def get_progress_percentage(self):
        if 'completed_modules' in self.progress_data and 'total_modules' in self.progress_data:
            completed = len(self.progress_data['completed_modules'])
            total = self.progress_data['total_modules']
            return (completed / total * 100) if total > 0 else 0
        return 0


class FAQ(models.Model):
    """Frequently Asked Questions for courses."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='faqs')
    question = models.TextField()
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
    
    def __str__(self):
        return f"FAQ: {self.question[:50]}..."


class Instructor(models.Model):
    """Course instructors/staff."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instructor_profile')
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=100, blank=True)
    is_lead_instructor = models.BooleanField(default=False)
    courses = models.ManyToManyField(Course, related_name='instructors', blank=True)
    
    # Social/contact
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    
    def __str__(self):
        return self.user.email
    
    class Meta:
        verbose_name = _('Instructor')
        verbose_name_plural = _('Instructors')


class UserCourseProgress(models.Model):
    """
    Tracks user progress in courses (alternative to CourseEnrollment progress_data).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_progress'
    )
    course_key = models.CharField(max_length=100, help_text="Identifier for the course")
    enrollment_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    progress_data = models.JSONField(
        default=dict,
        help_text="Stores completion status and progress metrics"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'course_key']
        verbose_name = _('Course Progress')
        verbose_name_plural = _('Course Progress Records')
    
    def __str__(self):
        return f"{self.user.email} - {self.course_key}"
    
    def save(self, *args, **kwargs):
        if not self.enrollment_id:
            import uuid
            self.enrollment_id = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
# Add these models to your existing models.py

class StudyGroup(models.Model):
    """Study groups for collaborative learning."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='study_groups')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='study_groups', blank=True)
    max_members = models.IntegerField(default=10)
    meeting_schedule = models.JSONField(default=dict, blank=True)  # Store schedule details
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.course.title}"
    
    class Meta:
        verbose_name = _('Study Group')
        verbose_name_plural = _('Study Groups')


class Notification(models.Model):
    """In-app notifications system."""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    TYPE_CHOICES = [
        ('course_update', 'Course Update'),
        ('deadline', 'Deadline'),
        ('achievement', 'Achievement'),
        ('message', 'Message'),
        ('system', 'System'),
        ('community', 'Community'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    data = models.JSONField(default=dict, blank=True)  # Additional data like links, course_slug, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at', 'priority']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')


class UserAnalytics(models.Model):
    """Store user learning analytics."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_analytics')
    
    # Learning patterns
    learning_patterns = models.JSONField(default=dict, blank=True)
    
    # Engagement metrics
    engagement_metrics = models.JSONField(default=dict, blank=True)
    
    # Performance metrics
    performance_metrics = models.JSONField(default=dict, blank=True)
    
    # Goals and progress
    learning_goals = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('User Analytics')
        verbose_name_plural = _('User Analytics')


class UserLearningPath(models.Model):
    """Track user's learning path and progress across courses."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_path')
    path_data = models.JSONField(default=dict, blank=True)
    current_focus = models.CharField(max_length=200, blank=True)
    completion_goal = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Learning Path - {self.user.email}"
    
    class Meta:
        verbose_name = _('Learning Path')
        verbose_name_plural = _('Learning Paths')


class Assignment(models.Model):
    """Course assignments."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]
    
    TYPE_CHOICES = [
        ('problem_set', 'Problem Set'),
        ('project', 'Project'),
        ('essay', 'Essay'),
        ('code', 'Code'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='problem_set')
    max_points = models.IntegerField(default=100)
    due_date = models.DateTimeField()
    instructions = models.JSONField(default=dict, blank=True)
    resources = models.JSONField(default=list, blank=True)
    rubric = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"
    
    class Meta:
        ordering = ['due_date']
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')


class Submission(models.Model):
    """Student submissions for assignments."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    content = models.JSONField(default=dict, blank=True)  # Could be text, file references, etc.
    files = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.assignment.title} - {self.student.email}"
    
    class Meta:
        unique_together = ['assignment', 'student']
        verbose_name = _('Submission')
        verbose_name_plural = _('Submissions')