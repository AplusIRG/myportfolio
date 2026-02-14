from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import datetime
import uuid
from django.utils import timezone

# ============================================================================
# CUSTOM USER MODEL (MERGED)
# ============================================================================

class CustomUser(AbstractUser):
    """
    Enhanced Custom User model supporting both portfolio and course management.
    Email is the primary login field.
    """
    # User Roles
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Administrator'),
        ('parent', 'Parent'),
        ('visitor', 'Visitor'),  # Default for portfolio visitors
    ]
    
    # School Choices
    SCHOOL_CHOICES = [
        ('school_mathematics_natural_sciences', 'School of Mathematics and Natural Sciences'),
        ('school_built_environment', 'School of Built Environment'),
        ('school_business_humanities', 'School of Business and Humanities'),
        ('none', 'Not Applicable'),
    ]
    
    # Course Levels (used elsewhere)
    COURSE_LEVEL_CHOICES = [
        ('highschool', 'HighSchool'),
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('certificate', 'Certificate'),
        ('professional', 'Professional Development'),
    ]
    
    # Portfolio Fields
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    
    # Course Management Fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='visitor')
    school = models.CharField(max_length=50, choices=SCHOOL_CHOICES, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    institution = models.CharField(max_length=200, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    profile_data = models.JSONField(default=dict, blank=True)
    
    # Portfolio-specific fields
    bio = models.TextField(blank=True, help_text="A short bio about yourself")
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text="Profile picture"
    )
    website = models.URLField(blank=True, help_text="Personal website or portfolio")
    location = models.CharField(max_length=100, blank=True, help_text="Your location")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        if self.role == 'visitor':
            return f"{self.email} (Portfolio Visitor)"
        return f"{self.email} ({self.get_role_display()})"
    
    def is_instructor(self):
        return self.role == 'instructor'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_portfolio_visitor(self):
        return self.role == 'visitor'
    
    def get_display_name(self):
        """Get a display name prioritizing full name, then username, then email."""
        if self.get_full_name():
            return self.get_full_name()
        elif self.username:
            return self.username
        return self.email.split('@')[0]
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


# ============================================================================
# PORTFOLIO CONTENT MODELS
# ============================================================================

class Skill(models.Model):
    """Represents a skill with proficiency level and optional icon."""
    name = models.CharField(max_length=100, unique=True)
    proficiency = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Proficiency percentage (0-100)"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="FontAwesome or other icon class (e.g., 'fa-python')"
    )
    description = models.TextField(blank=True, help_text="A brief description of the skill.")
    
    # Many-to-many to courses – using a unique related_name
    related_courses = models.ManyToManyField(
        'Course',
        blank=True,
        related_name='skills_related',   # changed from 'taught_skills'
        help_text="Courses that teach this skill"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-proficiency']
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')


class Project(models.Model):
    """Personal projects."""
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('planned', 'Planned'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(help_text="Detailed description of the project.")
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    url = models.URLField(blank=True, help_text="Link to live demo or GitHub")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills_used = models.ManyToManyField(Skill, related_name='projects', blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    is_featured = models.BooleanField(default=False)
    
    # Link to courses – using a unique related_name to avoid reverse clash
    related_courses = models.ManyToManyField(
        'Course',
        blank=True,
        related_name='projects_as_examples',   # changed from 'example_projects'
        help_text="Courses where this project is used as an example"
    )

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


class Testimonial(models.Model):
    """Testimonials from clients or colleagues."""
    author = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, help_text="Author's role/company")
    content = models.TextField(help_text="The actual testimonial text.")
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='testimonials'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        help_text="Rating from 1 to 5 stars"
    )

    def __str__(self):
        return f"Testimonial by {self.author}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Testimonial')
        verbose_name_plural = _('Testimonials')


class BlogPost(models.Model):
    """Blog posts supporting rich HTML content."""
    CATEGORY_CHOICES = [
        ('web_dev', 'Web Development'),
        ('design', 'Design'),
        ('career', 'Career'),
        ('tutorial', 'Tutorial'),
        ('personal', 'Personal'),
        ('tech_review', 'Technology Review'),
        ('course_related', 'Course Related'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(help_text="Full content – can contain HTML.")
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_posts'
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='web_dev')
    image = models.ImageField(upload_to='blog_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    tags = models.CharField(max_length=200, blank=True)
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
            ('private', 'Private (Admin Only)'),
            ('course_students', 'Course Students Only'),
        ],
        default='public'
    )
    
    # Additional fields for blog functionality
    read_time = models.IntegerField(default=5, help_text="Estimated reading time in minutes")
    views = models.IntegerField(default=0)
    
    related_courses = models.ManyToManyField(
        'Course',
        blank=True,
        related_name='blog_posts'
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
    """Quick notes / short articles."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(help_text="Content – can contain HTML.")
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
            ('private', 'Private (Author Only)'),
            ('course_students', 'Course Students Only'),
        ],
        default='registered'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes'
    )
    tags = models.CharField(max_length=200, blank=True)

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
    """Files like PDFs, slides, assignments, etc."""
    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('slides', 'Presentation Slides'),
        ('ebook', 'E-Book'),
        ('assignment', 'Assignment'),
        ('lecture_notes', 'Lecture Notes'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='pdf')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )
    is_published = models.BooleanField(default=False)
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
            ('private', 'Private (Admin Only)'),
            ('course_students', 'Course Students Only'),
        ],
        default='registered'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    file_size = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)

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
    """Recommended books or books written."""
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True, null=True, unique=True)
    genre = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    purchase_link = models.URLField(blank=True)
    recommended_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommended_books'
    )
    published_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
        ],
        default='public'
    )
    related_courses = models.ManyToManyField(
        'Course',
        blank=True,
        related_name='recommended_books'
    )

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['title']
        verbose_name = _('Book')
        verbose_name_plural = _('Books')


class Meeting(models.Model):
    """Scheduled meetings/lectures."""
    MEETING_TYPE_CHOICES = [
        ('1-on-1', 'One-on-One Consultation'),
        ('group_lecture', 'Group Lecture/Webinar'),
        ('discovery_call', 'Discovery Call'),
        ('course_office_hours', 'Course Office Hours'),
        ('course_lecture', 'Course Lecture'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='1-on-1')
    date = models.DateField(default=datetime.date.today)
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='offered_meetings'
    )
    meeting_link = models.URLField(blank=True)
    max_attendees = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)]
    )
    attendees = models.ManyToManyField(
        CustomUser,
        related_name='booked_meetings',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    requires_registration = models.BooleanField(default=True)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings'
    )
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
        ]
    )
    recurrence_end_date = models.DateField(blank=True, null=True)

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
    """Messages from contact form."""
    MESSAGE_TYPE_CHOICES = [
        ('general', 'General Inquiry'),
        ('course', 'Course Inquiry'),
        ('technical', 'Technical Support'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='general')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_messages'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries'
    )

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')


# ============================================================================
# COURSE MANAGEMENT MODELS
# ============================================================================

class Course(models.Model):
    """Represents a course offered through the portfolio."""
    DIFFICULTY_CHOICES = [
        ('introductory', 'Introductory'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    LEVEL_CHOICES = CustomUser.COURSE_LEVEL_CHOICES
    
    course_id = models.CharField(max_length=20, unique=True)
    course_code = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    
    school = models.CharField(max_length=50, choices=CustomUser.SCHOOL_CHOICES)
    department = models.CharField(max_length=100)
    instructor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'instructor'},
        related_name='instructed_courses'
    )
    
    credits = models.IntegerField(default=3)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='undergraduate')
    duration = models.CharField(max_length=50, default='14 weeks')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate')
    
    enrollment_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    views = models.IntegerField(default=0)
    
    prerequisites = models.JSONField(default=list, blank=True)
    learning_outcomes = models.JSONField(default=list, blank=True)
    syllabus = models.JSONField(default=list, blank=True)
    resources_structure = models.JSONField(default=dict, blank=True)
    
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    promo_video = models.URLField(blank=True)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_open_for_enrollment = models.BooleanField(default=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    # Many-to-many fields with unique related_names
    skills_taught = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='courses_teaching',   # changed from 'courses_teaching_skill'
        help_text="Skills that students will learn in this course"
    )
    
    # This field will be the reverse of Project.related_courses (now projects_as_examples)
    example_projects = models.ManyToManyField(
        Project,
        blank=True,
        related_name='courses_using_project'   # this is now unique and not conflicting
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.price == 0.00:
            self.is_free = True
        else:
            self.is_free = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_code}: {self.title}"

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['course_code']
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')


class Enrollment(models.Model):
    """User enrollment in courses."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)
    progress_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    payment_made = models.BooleanField(default=False)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    certificate_issued = models.BooleanField(default=False)
    certificate_issue_date = models.DateTimeField(blank=True, null=True)
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
    
    def __str__(self):
        return f"{self.user.email} - {self.course.course_code}"


class UserProgress(models.Model):
    """Tracks user progress in a course."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress')
    chapters_completed = models.IntegerField(default=0)
    total_chapters = models.IntegerField(default=0)
    assignments_submitted = models.IntegerField(default=0)
    total_assignments = models.IntegerField(default=0)
    current_chapter = models.IntegerField(default=1)
    last_accessed = models.DateTimeField(auto_now=True)
    quiz_scores = models.JSONField(default=dict, blank=True)
    time_spent = models.IntegerField(default=0)  # in minutes
    grade = models.FloatField(default=0.0)
    streak_days = models.IntegerField(default=0)
    last_streak_update = models.DateField(blank=True, null=True)
    
    completed_modules = models.JSONField(default=list, blank=True)
    completed_lessons = models.JSONField(default=list, blank=True)
    completed_quizzes = models.JSONField(default=list, blank=True)
    
    average_quiz_score = models.FloatField(default=0.0)
    assignment_average = models.FloatField(default=0.0)

    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('User Progress')
        verbose_name_plural = _('User Progresses')
    
    def __str__(self):
        return f"{self.user.email} - {self.course.course_code} - Progress: {self.calculate_progress()}%"
    
    def calculate_progress(self):
        if self.total_chapters == 0:
            return 0
        return (self.chapters_completed / self.total_chapters) * 100


class CourseModule(models.Model):
    """Module within a course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']
        verbose_name = _('Course Module')
        verbose_name_plural = _('Course Modules')
    
    def __str__(self):
        return f"{self.course.course_code} - Module {self.order}: {self.title}"


class Lesson(models.Model):
    """Lesson within a module."""
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    duration_minutes = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    requires_completion = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    attached_documents = models.ManyToManyField(Document, blank=True, related_name='lessons')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.module.course.course_code}-{self.title}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.module.course.course_code} - Lesson {self.order}: {self.title}"
    
    class Meta:
        ordering = ['order']
        unique_together = ['module', 'order']
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')


class Assignment(models.Model):
    """Course assignments."""
    ASSIGNMENT_TYPES = [
        ('homework', 'Homework'),
        ('project', 'Project'),
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
        ('lab', 'Lab Work'),
        ('essay', 'Essay'),
        ('presentation', 'Presentation'),
    ]
    
    assignment_id = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    max_points = models.IntegerField(default=100)
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES)
    resources = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_assignments')
    
    # This is a ForeignKey, not ManyToManyField.
    related_project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_assignments'
    )
    
    allows_file_upload = models.BooleanField(default=True)
    allowed_file_types = models.JSONField(default=list, blank=True)
    max_file_size_mb = models.IntegerField(default=10)
    
    def __str__(self):
        return f"{self.title} - {self.course.course_code}"
    
    class Meta:
        ordering = ['due_date']
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')


class Submission(models.Model):
    """Student submissions for assignments."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    is_graded = models.BooleanField(default=False)
    graded_at = models.DateTimeField(blank=True, null=True)
    graded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    
    class Meta:
        unique_together = ['user', 'assignment']
        verbose_name = _('Submission')
        verbose_name_plural = _('Submissions')
    
    def __str__(self):
        return f"{self.user.email} - {self.assignment.title}"


class EmailVerification(models.Model):
    """Email verification codes."""
    VERIFICATION_TYPES = [
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
        ('enrollment_confirmation', 'Enrollment Confirmation'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='email_verifications')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    verification_type = models.CharField(
        max_length=23,   # Increased from 20 to accommodate the longest choice (23 chars)
        choices=VERIFICATION_TYPES,
        default='email_verification'
    )
    
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=24)
    
    def __str__(self):
        return f"{self.user.email} - {self.code}"
    
    class Meta:
        verbose_name = _('Email Verification')
        verbose_name_plural = _('Email Verifications')


class ParentConnection(models.Model):
    """Connects parents to their student accounts."""
    parent = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='parent_connections_as_parent'
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='parent_connections_as_student'
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    
    can_view_grades = models.BooleanField(default=True)
    can_view_attendance = models.BooleanField(default=True)
    can_receive_notifications = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['parent', 'student']
        verbose_name = _('Parent Connection')
        verbose_name_plural = _('Parent Connections')
    
    def __str__(self):
        return f"{self.parent.email} -> {self.student.email}"


class Certificate(models.Model):
    """Course completion certificates."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates_issued')
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    download_url = models.URLField(blank=True)
    is_verified = models.BooleanField(default=True)
    verification_code = models.CharField(max_length=20, blank=True)
    
    grade = models.CharField(max_length=10, blank=True)
    completion_hours = models.IntegerField(default=0)
    instructor_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('Certificate')
        verbose_name_plural = _('Certificates')
    
    def __str__(self):
        return f"Certificate - {self.user.email} - {self.course.title}"


class CourseReview(models.Model):
    """Reviews and ratings for courses."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='course_reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    helpful_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('Course Review')
        verbose_name_plural = _('Course Reviews')
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title} - {self.rating} stars"